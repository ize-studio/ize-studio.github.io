#!/usr/bin/env python3

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import import_korean_posts


class ImportKoreanPostsTests(unittest.TestCase):
    def test_normalize_local_body_makes_markdown_paragraphs(self):
        body = "첫 문단\n둘째 문단\n\n셋째 문단\n"
        self.assertEqual(import_korean_posts.normalize_local_body(body), "첫 문단\n\n둘째 문단\n\n셋째 문단\n")

    def test_astro_unwrap_and_text_collection_preserve_breaks(self):
        encoded = [
            0,
            {
                "children": [
                    1,
                    [
                        [0, {"text": [0, "첫 문단"]}],
                        [0, {"type": [0, "br"]}],
                        [0, {"text": [0, "둘째 문단"]}],
                    ],
                ]
            },
        ]
        decoded = import_korean_posts.astro_unwrap(encoded)
        tokens = []
        import_korean_posts.collect_text_tokens(decoded, tokens)
        self.assertEqual("".join(tokens), "첫 문단\n\n둘째 문단")

    def test_text_collection_preserves_anchor_as_markdown(self):
        node = {
            "type": "anchor",
            "link": "https://example.com/source",
            "children": [{"text": "원문", "children": None}],
        }
        tokens = []
        import_korean_posts.collect_text_tokens(node, tokens)
        self.assertEqual("".join(tokens), "[원문](https://example.com/source)")

    def test_visible_absolute_url_repairs_concatenated_brunch_link(self):
        node = {
            "type": "anchor",
            "link": "https://brunch.co.kr/@rup-l/398https://youtu.be/example",
            "children": [{"text": "https://youtu.be/example", "children": None}],
        }
        tokens = []
        import_korean_posts.collect_text_tokens(node, tokens)
        self.assertEqual("".join(tokens), "[https://youtu.be/example](https://youtu.be/example)")

    def test_cached_brunch_numbers_are_deduplicated(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "brunch.json"
            path.write_text(
                '[{"url":"https://brunch.co.kr/@rup-l/394"},'
                '{"url":"https://brunch.co.kr/@rup-l/394"},'
                '{"url":"https://example.com/not-brunch"}]',
                encoding="utf-8",
            )
            self.assertEqual(import_korean_posts.cached_brunch_numbers(path), [394])

    def test_update_english_document_points_to_korean_post(self):
        original = """---
layout: post
title: "English"
date: 2026-01-01
canonical_url: "https://brunch.co.kr/@rup-l/123"
---

Body.

---

Korean original: [원문](https://brunch.co.kr/@rup-l/123)
"""
        updated = import_korean_posts.update_english_document(original, 123)
        self.assertIn('canonical_url: "https://ize-studio.github.io/ko/posts/brunch-123.html"', updated)
        self.assertIn('original_url: "/ko/posts/brunch-123.html"', updated)
        self.assertIn('translation_key: "brunch-123"', updated)
        self.assertNotIn("Korean original:", updated)


if __name__ == "__main__":
    unittest.main()
