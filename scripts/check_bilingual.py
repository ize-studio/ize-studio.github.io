#!/usr/bin/env python3
"""Validate stored English/Korean translation pairs without external packages."""

from __future__ import annotations

from pathlib import Path

import import_korean_posts


ROOT = Path(__file__).resolve().parents[1]


def documents(directory: Path) -> list[tuple[Path, str, str]]:
    result: list[tuple[Path, str, str]] = []
    for path in sorted(directory.glob("*.md")):
        front, body = import_korean_posts.split_document(path.read_text(encoding="utf-8-sig"))
        result.append((path, front, body))
    return result


def main() -> int:
    english = documents(ROOT / "_posts")
    korean = documents(ROOT / "_korean_posts")
    errors: list[str] = []

    english_by_key: dict[str, tuple[Path, str, str]] = {}
    korean_by_key: dict[str, tuple[Path, str, str]] = {}
    for document in english:
        key = import_korean_posts.scalar(document[1], "translation_key")
        if not key:
            errors.append(f"Missing English translation_key: {document[0].name}")
            continue
        if key in english_by_key:
            errors.append(f"Duplicate English translation_key: {key}")
        english_by_key[key] = document
    for document in korean:
        key = import_korean_posts.scalar(document[1], "translation_key")
        if not key:
            errors.append(f"Missing Korean translation_key: {document[0].name}")
            continue
        if key in korean_by_key:
            errors.append(f"Duplicate Korean translation_key: {key}")
        korean_by_key[key] = document
        if not document[2].strip():
            errors.append(f"Empty Korean body: {document[0].name}")

    for key, (_, front, _) in english_by_key.items():
        korean_document = korean_by_key.get(key)
        if korean_document is None:
            errors.append(f"Missing Korean counterpart: {key}")
            continue
        number = key.removeprefix("brunch-")
        expected = f"https://ize-studio.github.io/ko/posts/brunch-{number}.html"
        if import_korean_posts.scalar(front, "canonical_url") != expected:
            errors.append(f"Wrong English original link: {key}")
        korean_original = import_korean_posts.scalar(korean_document[1], "canonical_url")
        if korean_original != f"https://brunch.co.kr/@rup-l/{number}":
            errors.append(f"Wrong Korean original link: {key}")

    for key in korean_by_key.keys() - english_by_key.keys():
        errors.append(f"Missing English counterpart: {key}")

    required_pages = [
        "ko/index.md",
        "ko/writing/index.html",
        "ko/fiction/index.html",
        "ko/research/index.html",
        "ko/projects/index.html",
        "ko/shop/index.html",
        "ko/about/index.html",
        "ko/categories/index.html",
    ]
    for relative_path in required_pages:
        if not (ROOT / relative_path).exists():
            errors.append(f"Missing Korean page: {relative_path}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"Validated {len(english_by_key)} bilingual post pairs and {len(required_pages)} Korean pages.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
