#!/usr/bin/env python3

import json
import tempfile
import unittest
from pathlib import Path

import fetch_brunch


class FetchBrunchTests(unittest.TestCase):
    def test_parse_api_payload_deduplicates_and_sorts(self):
        raw = json.dumps(
            {
                "data": {
                    "articleList": [
                        {"no": 1, "title": "Old", "publishTime": 1714176000000},
                        {"no": 2, "title": "New", "publishTime": 1782691200000},
                        {"no": 2, "title": "New duplicate", "publishTime": 1782691200000},
                    ]
                }
            }
        )
        posts = fetch_brunch.parse_api_payload(raw)
        self.assertEqual([post["title"] for post in posts], ["New", "Old"])
        self.assertEqual(len(posts), 2)

    def test_zero_posts_does_not_overwrite_existing_cache(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "brunch.json"
            original = '[{"title":"Existing","url":"https://brunch.co.kr/@rup-l/1"}]\n'
            path.write_text(original, encoding="utf-8")
            with self.assertRaises(fetch_brunch.BrunchSyncWarning):
                fetch_brunch.write_cache(path, [])
            self.assertEqual(path.read_text(encoding="utf-8"), original)

    def test_malformed_json_raises_without_normalized_posts(self):
        with self.assertRaises(json.JSONDecodeError):
            fetch_brunch.parse_api_payload("{not json")

    def test_html_fallback_extracts_article_links(self):
        raw = '<a href="/@rup-l/10"><span>글 제목</span></a><a href="/@rup-l/10">중복</a>'
        posts = fetch_brunch.parse_html_payload(raw)
        self.assertEqual(len(posts), 1)
        self.assertEqual(posts[0]["url"], "https://brunch.co.kr/@rup-l/10")
        self.assertEqual(posts[0]["title"], "글 제목")


if __name__ == "__main__":
    unittest.main()
