---
layout: default
title: Writing Tools
permalink: /categories/writing-tools/
---

# Writing Tools

Notes on typewriters, keyboards, e-ink devices, software, and writing workflows.

{% assign category_posts = site.posts | where_exp: "post", "post.category == 'Writing Tools' or post.categories contains 'Writing Tools'" | sort: "date" | reverse %}
{% include category-post-list.html posts=category_posts %}
