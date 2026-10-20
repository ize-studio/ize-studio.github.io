#!/usr/bin/env python3
"""Build paired Korean posts from Brunch sources for existing English posts."""

from __future__ import annotations

import argparse
import html
import json
import re
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ENGLISH_DIR = ROOT / "_posts"
KOREAN_DIR = ROOT / "_korean_posts"
BRUNCH_CACHE = ROOT / "_data" / "brunch.json"
SITE_URL = "https://ize-studio.github.io"
USER_AGENT = "BoundaryKoreanArchive/1.0 (+https://ize-studio.github.io/)"
FRONT_MATTER_RE = re.compile(r"\A---\r?\n(?P<front>.*?)\r?\n---\r?\n(?P<body>.*)\Z", re.DOTALL)
BRUNCH_URL_RE = re.compile(r"https://brunch\.co\.kr/@rup-l/(?P<number>\d+)")


@dataclass
class SourcePost:
    number: int
    title: str
    date: str
    source_url: str
    body: str
    keywords: list[str]


def split_document(text: str) -> tuple[str, str]:
    match = FRONT_MATTER_RE.match(text)
    if not match:
        raise ValueError("Markdown file has no valid front matter")
    return match.group("front"), match.group("body")


def scalar(front: str, key: str) -> str:
    match = re.search(rf"(?m)^{re.escape(key)}:\s*(.*?)\s*$", front)
    if not match:
        return ""
    return match.group(1).strip().strip('"').strip("'")


def list_value(front: str, key: str) -> list[str]:
    inline = scalar(front, key)
    if inline.startswith("[") and inline.endswith("]"):
        return [part.strip().strip('"').strip("'") for part in inline[1:-1].split(",") if part.strip()]
    block = re.search(rf"(?ms)^{re.escape(key)}:\s*\r?\n(?P<items>(?:\s+-\s+.*\r?\n?)*)", front)
    if not block:
        return []
    return [
        line.strip()[2:].strip().strip('"').strip("'")
        for line in block.group("items").splitlines()
        if line.strip().startswith("- ")
    ]


def set_scalar(front: str, key: str, value: str) -> str:
    rendered = json.dumps(value, ensure_ascii=False)
    pattern = re.compile(rf"(?m)^{re.escape(key)}:\s*.*$")
    if pattern.search(front):
        return pattern.sub(f"{key}: {rendered}", front, count=1)
    return f"{front.rstrip()}\n{key}: {rendered}"


def normalize_date(value: str) -> str:
    return value.strip().strip('"').strip("'")


def normalize_local_body(body: str) -> str:
    paragraphs = [line.strip() for line in body.splitlines() if line.strip()]
    return "\n\n".join(paragraphs).strip() + "\n"


def load_local_sources(source_dir: Path) -> dict[int, SourcePost]:
    sources: dict[int, SourcePost] = {}
    if not source_dir.exists():
        return sources
    for path in source_dir.glob("*.md"):
        try:
            front, body = split_document(path.read_text(encoding="utf-8-sig"))
        except (OSError, UnicodeError, ValueError):
            continue
        number_text = scalar(front, "brunch_no")
        if not number_text.isdigit():
            continue
        number = int(number_text)
        sources[number] = SourcePost(
            number=number,
            title=scalar(front, "title"),
            date=normalize_date(scalar(front, "date")),
            source_url=scalar(front, "source") or f"https://brunch.co.kr/@rup-l/{number}",
            body=normalize_local_body(body),
            keywords=list_value(front, "keywords"),
        )
    return sources


def load_existing_sources() -> dict[int, SourcePost]:
    sources: dict[int, SourcePost] = {}
    if not KOREAN_DIR.exists():
        return sources
    for path in KOREAN_DIR.glob("brunch-*.md"):
        try:
            front, body = split_document(path.read_text(encoding="utf-8-sig"))
        except (OSError, UnicodeError, ValueError):
            continue
        number_text = scalar(front, "brunch_no")
        if not number_text.isdigit():
            continue
        number = int(number_text)
        sources[number] = SourcePost(
            number=number,
            title=scalar(front, "title"),
            date=normalize_date(scalar(front, "date")),
            source_url=scalar(front, "original_url") or f"https://brunch.co.kr/@rup-l/{number}",
            body=body.strip() + "\n",
            keywords=list_value(front, "tags"),
        )
    return sources


def astro_unwrap(value: Any) -> Any:
    if isinstance(value, list):
        if len(value) == 1 and value[0] == 0:
            return None
        if len(value) == 2 and value[0] in (0, 1):
            return astro_unwrap(value[1])
        return [astro_unwrap(item) for item in value]
    if isinstance(value, dict):
        return {key: astro_unwrap(item) for key, item in value.items()}
    return value


def collect_text_tokens(value: Any, tokens: list[str]) -> None:
    if isinstance(value, dict):
        node_type = value.get("type")
        if isinstance(node_type, str) and node_type.lower() == "br":
            tokens.append("\n\n")
            return
        if isinstance(node_type, str) and node_type.lower() == "anchor" and value.get("link"):
            linked_tokens: list[str] = []
            collect_text_tokens(value.get("children", []), linked_tokens)
            label = "".join(linked_tokens).strip()
            link = str(value["link"])
            if re.fullmatch(r"https?://\S+", label) and link.endswith(label) and link != label:
                link = label
            link = link.replace(")", "%29")
            if label:
                label = label.replace("[", "\\[").replace("]", "\\]")
                tokens.append(f"[{label}]({link})")
            else:
                tokens.append(f"<{link}>")
            return
        text_value = value.get("text")
        if isinstance(text_value, str) and text_value:
            tokens.append(text_value.replace("\r", ""))
            return
        children = value.get("children")
        if children is not None:
            collect_text_tokens(children, tokens)
            return
        for nested in value.values():
            collect_text_tokens(nested, tokens)
    elif isinstance(value, list):
        for nested in value:
            collect_text_tokens(nested, tokens)


def markdown_from_astro_props(raw_html: str) -> str:
    match = re.search(
        r'<astro-island[^>]+component-export="ArticleBodyWithDarkMode"[^>]+props="(?P<props>.*?)"[^>]*>',
        raw_html,
        re.DOTALL,
    )
    if not match:
        return ""
    payload = json.loads(html.unescape(match.group("props")))
    decoded = astro_unwrap(payload)
    elements = decoded.get("elements", []) if isinstance(decoded, dict) else []
    blocks: list[str] = []
    for element in elements:
        if not isinstance(element, dict):
            continue
        tokens: list[str] = []
        collect_text_tokens(element.get("textComponent", element), tokens)
        text = "".join(tokens)
        text = re.sub(r"[ \t]+\n", "\n", text)
        text = re.sub(r"\n{3,}", "\n\n", text).strip()
        if not text:
            continue
        element_type = str(element.get("type", "")).upper()
        if "QUOTE" in element_type:
            text = "\n".join(f"> {line}" if line else ">" for line in text.splitlines())
        elif element_type in {"TITLE", "SUBTITLE", "HEADING"}:
            text = f"## {text}"
        blocks.append(text)
    return "\n\n".join(blocks).strip()


def fetch_source(number: int) -> SourcePost:
    source_url = f"https://brunch.co.kr/@rup-l/{number}"
    request = urllib.request.Request(
        source_url,
        headers={"User-Agent": USER_AGENT, "Accept": "text/html,*/*;q=0.8"},
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        raw_html = response.read().decode(response.headers.get_content_charset() or "utf-8", errors="replace")

    metadata: dict[str, Any] | None = None
    for raw_json in re.findall(r'<script type="application/ld\+json">(.*?)</script>', raw_html, re.DOTALL):
        try:
            candidate = json.loads(raw_json)
        except json.JSONDecodeError:
            continue
        if candidate.get("@type") == "BlogPosting":
            metadata = candidate
            break
    if not metadata:
        raise RuntimeError(f"No BlogPosting metadata found for {source_url}")

    body = markdown_from_astro_props(raw_html)
    if not body:
        body = str(metadata.get("articleBody", "")).strip()
        title = str(metadata.get("headline", "")).strip()
        if title and body.startswith(f"{title} "):
            body = body[len(title) + 1 :]
    if not body:
        raise RuntimeError(f"No article body found for {source_url}")

    keywords = metadata.get("keywords", [])
    if isinstance(keywords, str):
        keywords = [part.strip() for part in keywords.split(",") if part.strip()]
    return SourcePost(
        number=number,
        title=str(metadata.get("headline", "")).strip(),
        date=normalize_date(str(metadata.get("datePublished", ""))),
        source_url=source_url,
        body=body.strip() + "\n",
        keywords=[str(item) for item in keywords],
    )


def english_posts() -> list[tuple[Path, str, str, int]]:
    posts: list[tuple[Path, str, str, int]] = []
    for path in sorted(ENGLISH_DIR.glob("*.md")):
        text = path.read_text(encoding="utf-8-sig")
        front, _ = split_document(text)
        source_value = scalar(front, "brunch_url") or scalar(front, "canonical_url")
        url_match = BRUNCH_URL_RE.search(source_value)
        if not url_match:
            continue
        posts.append((path, text, front, int(url_match.group("number"))))
    return posts


def cached_brunch_numbers(path: Path = BRUNCH_CACHE) -> list[int]:
    if not path.exists():
        return []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    numbers: set[int] = set()
    for item in payload if isinstance(payload, list) else []:
        if not isinstance(item, dict):
            continue
        match = BRUNCH_URL_RE.fullmatch(str(item.get("url", "")).strip())
        if match:
            numbers.add(int(match.group("number")))
    return sorted(numbers)


def render_korean_post(source: SourcePost, english_front: str) -> str:
    categories = list_value(english_front, "categories")
    if not categories:
        category = scalar(english_front, "category")
        categories = [category] if category else ["한국어 작품"]
    front_lines = [
        "---",
        "layout: post",
        f"title: {json.dumps(source.title, ensure_ascii=False)}",
        f"date: {json.dumps(source.date, ensure_ascii=False)}",
        f"categories: [{', '.join(json.dumps(item, ensure_ascii=False) for item in categories)}]",
        f"tags: [{', '.join(json.dumps(item, ensure_ascii=False) for item in source.keywords)}]",
        "lang: ko",
        f"translation_key: {json.dumps(f'brunch-{source.number}')}",
        f"canonical_url: {json.dumps(source.source_url)}",
        f"original_url: {json.dumps(source.source_url)}",
        f"brunch_no: {source.number}",
        "---",
        "",
    ]
    return "\n".join(front_lines) + source.body


def update_english_document(text: str, number: int) -> str:
    front, body = split_document(text)
    korean_path = f"/ko/posts/brunch-{number}.html"
    front = set_scalar(front, "brunch_url", f"https://brunch.co.kr/@rup-l/{number}")
    front = set_scalar(front, "canonical_url", f"{SITE_URL}{korean_path}")
    front = set_scalar(front, "original_url", korean_path)
    front = set_scalar(front, "translation_key", f"brunch-{number}")
    front = set_scalar(front, "lang", "en")
    body = re.sub(
        rf"(\]\()https://brunch\.co\.kr/@rup-l/{number}(\))",
        rf"\g<1>{korean_path}\g<2>",
        body,
    )
    body = re.sub(
        r"\n+(?:---\s*\n+)?(?:Original Korean article|Korean original):\s*\[[^\]]+\]\([^\)]+\)\s*\Z",
        "\n",
        body,
        flags=re.IGNORECASE,
    )
    return f"---\n{front}\n---\n{body}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-dir", type=Path, default=Path(r"D:\brunch"))
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--allow-missing", action="store_true")
    parser.add_argument(
        "--refresh-live",
        action="store_true",
        help="Refetch posts that are not present in the local source archive.",
    )
    parser.add_argument(
        "--include-brunch-cache",
        action="store_true",
        help="Create Korean-only posts for Brunch cache entries without English translations.",
    )
    args = parser.parse_args()

    local_sources = load_local_sources(args.source_dir)
    existing_sources = load_existing_sources()
    pairs = english_posts()
    english_by_number = {number: (path, text, front) for path, text, front, number in pairs}
    target_numbers = set(english_by_number)
    if args.include_brunch_cache:
        target_numbers.update(cached_brunch_numbers())
    fetched = 0
    missing: list[int] = []
    if not args.dry_run:
        KOREAN_DIR.mkdir(parents=True, exist_ok=True)

    for number in sorted(target_numbers):
        english_document = english_by_number.get(number)
        if english_document:
            path, text, front = english_document
        else:
            path = None
            text = ""
            front = ""
        source = local_sources.get(number)
        if source is None and not args.refresh_live:
            source = existing_sources.get(number)
        if source is None:
            try:
                source = fetch_source(number)
                fetched += 1
            except Exception as exc:
                if not args.allow_missing:
                    raise
                print(f"Warning: could not import Brunch article {number}: {exc}")
                missing.append(number)
                continue
        if not source.title or not source.body.strip():
            raise RuntimeError(f"Incomplete Korean source for Brunch article {number}")
        if args.dry_run:
            print(f"{number}: {path.name} -> {source.title}")
            continue
        korean_path = KOREAN_DIR / f"brunch-{number}.md"
        korean_path.write_text(render_korean_post(source, front), encoding="utf-8", newline="\n")
        if path is not None:
            path.write_text(update_english_document(text, number), encoding="utf-8", newline="\n")

    imported = len(target_numbers) - len(missing)
    korean_only = len(target_numbers - set(english_by_number))
    print(
        f"Imported {imported} Korean posts ({imported - fetched} cached/local, "
        f"{fetched} fetched, {korean_only} Korean-only, {len(missing)} missing)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
