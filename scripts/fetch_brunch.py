#!/usr/bin/env python3
"""Fetch public Brunch article metadata into _data/brunch.json.

The script keeps the previous cache when parsing fails or returns zero posts.
It intentionally stores only metadata used for outbound links.
"""

from __future__ import annotations

import datetime as dt
import html
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


AUTHOR = os.environ.get("BRUNCH_AUTHOR", "rup-l")
BASE_URL = f"https://brunch.co.kr/@{AUTHOR}"
API_URL = f"https://api.brunch.co.kr/v2/article/%40{AUTHOR}?lastTime=0&thumbnail=Y&membershipContent=false"
ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = ROOT / "_data" / "brunch.json"
USER_AGENT = "BoundaryBrunchSync/1.0 (+https://ize-studio.github.io/)"


class BrunchSyncWarning(RuntimeError):
    pass


def fetch_url(url: str, timeout: int = 15) -> str:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/json,text/html;q=0.9,*/*;q=0.8",
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        status = getattr(response, "status", 200)
        if status >= 400:
            raise BrunchSyncWarning(f"HTTP {status} while fetching {url}")
        charset = response.headers.get_content_charset() or "utf-8"
        return response.read().decode(charset, errors="replace")


def find_article_lists(value: Any) -> list[list[dict[str, Any]]]:
    lists: list[list[dict[str, Any]]] = []
    if isinstance(value, list) and all(isinstance(item, dict) for item in value):
        lists.append(value)
    elif isinstance(value, dict):
        for nested in value.values():
            lists.extend(find_article_lists(nested))
    return lists


def normalize_timestamp(value: Any) -> str:
    if value in (None, ""):
        return ""
    if isinstance(value, str):
        stripped = value.strip()
        if re.fullmatch(r"\d{4}[.-]\d{1,2}[.-]\d{1,2}", stripped):
            return re.sub(r"[.]", "-", stripped)
        if re.fullmatch(r"\d{4}-\d{1,2}-\d{1,2}", stripped):
            parts = [int(part) for part in stripped.split("-")]
            return dt.date(parts[0], parts[1], parts[2]).isoformat()
        if stripped.isdigit():
            value = int(stripped)
        else:
            return stripped
    if isinstance(value, (int, float)):
        seconds = float(value)
        if seconds > 10_000_000_000:
            seconds = seconds / 1000
        return dt.datetime.fromtimestamp(seconds, tz=dt.timezone.utc).date().isoformat()
    return ""


def article_url(item: dict[str, Any]) -> str:
    direct_url = item.get("url") or item.get("articleUrl") or item.get("article_url")
    if isinstance(direct_url, str) and direct_url:
        if direct_url.startswith("http"):
            return direct_url
        if direct_url.startswith("/"):
            return f"https://brunch.co.kr{direct_url}"

    article_no = item.get("no") or item.get("articleNo") or item.get("articleId")
    if article_no:
        return f"{BASE_URL}/{article_no}"
    return ""


def normalize_post(item: dict[str, Any]) -> dict[str, str] | None:
    title = item.get("title") or item.get("articleTitle") or item.get("subject")
    if not isinstance(title, str) or not title.strip():
        return None
    url = article_url(item)
    if not url:
        return None

    excerpt = item.get("contentSummary") or item.get("summary") or item.get("description") or ""
    thumbnail = item.get("articleImageUrl") or item.get("thumbnail") or item.get("thumbnailUrl") or ""
    date = normalize_timestamp(item.get("publishTime") or item.get("publishedTime") or item.get("date"))

    return {
        "title": html.unescape(title).strip(),
        "url": url,
        "date": date,
        "excerpt": html.unescape(str(excerpt)).strip(),
        "thumbnail": str(thumbnail).strip(),
        "source": "Brunch",
        "lang": "ko",
    }


def parse_api_payload(raw: str) -> list[dict[str, str]]:
    payload = json.loads(raw)
    candidates = find_article_lists(payload)
    posts: list[dict[str, str]] = []
    for candidate in candidates:
        normalized = [post for item in candidate if (post := normalize_post(item))]
        if len(normalized) > len(posts):
            posts = normalized
    return dedupe_and_sort(posts)


def parse_html_payload(raw: str) -> list[dict[str, str]]:
    posts: list[dict[str, str]] = []
    pattern = re.compile(
        rf'href=["\'](?P<url>(?:https://brunch\.co\.kr)?/@{re.escape(AUTHOR)}/(?P<no>\d+))["\'][^>]*>(?P<title>.*?)</a>',
        re.IGNORECASE | re.DOTALL,
    )
    for match in pattern.finditer(raw):
        title = re.sub(r"<[^>]+>", " ", match.group("title"))
        title = html.unescape(re.sub(r"\s+", " ", title)).strip()
        if not title:
            continue
        url = match.group("url")
        if url.startswith("/"):
            url = f"https://brunch.co.kr{url}"
        posts.append(
            {
                "title": title,
                "url": url,
                "date": "",
                "excerpt": "",
                "thumbnail": "",
                "source": "Brunch",
                "lang": "ko",
            }
        )
    return dedupe_and_sort(posts)


def dedupe_and_sort(posts: list[dict[str, str]]) -> list[dict[str, str]]:
    by_url: dict[str, dict[str, str]] = {}
    for post in posts:
        url = post.get("url", "")
        if url and url not in by_url:
            by_url[url] = post
    return sorted(by_url.values(), key=lambda item: (item.get("date", ""), item.get("url", "")), reverse=True)


def load_existing(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        return data if isinstance(data, list) else []
    except (OSError, json.JSONDecodeError):
        return []


def write_cache(path: Path, posts: list[dict[str, str]]) -> bool:
    if not posts:
        raise BrunchSyncWarning("Brunch parse returned zero posts; keeping previous cache.")
    path.parent.mkdir(parents=True, exist_ok=True)
    new_text = json.dumps(posts, ensure_ascii=False, indent=2) + "\n"
    old_text = path.read_text(encoding="utf-8") if path.exists() else ""
    if old_text == new_text:
        return False
    path.write_text(new_text, encoding="utf-8")
    return True


def fetch_posts() -> list[dict[str, str]]:
    try:
        return parse_api_payload(fetch_url(API_URL))
    except (BrunchSyncWarning, urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        print(f"API fetch warning: {exc}", file=sys.stderr)
    return parse_html_payload(fetch_url(BASE_URL))


def main() -> int:
    existing = load_existing(OUTPUT_PATH)
    try:
        posts = fetch_posts()
        changed = write_cache(OUTPUT_PATH, posts)
        print(f"Fetched {len(posts)} Brunch posts. Cache {'updated' if changed else 'unchanged'}.")
    except Exception as exc:  # The workflow should preserve the last known good cache.
        print(f"Brunch sync warning: {exc}", file=sys.stderr)
        print(f"Kept existing cache with {len(existing)} posts.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
