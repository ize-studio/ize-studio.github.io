---
layout: default
title: Reading Notes
permalink: /categories/reading-notes/
---

# Reading Notes

Book notes, quotations in context, and observations gathered while reading.

{% assign category_posts = site.posts | where_exp: "post", "post.category == 'Reading Notes' or post.categories contains 'Reading Notes'" | sort: "date" | reverse %}
{% include category-post-list.html posts=category_posts %}
