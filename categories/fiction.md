---
layout: default
title: Fiction
permalink: /categories/fiction/
---

# Fiction

Short stories, fragments, and fictional experiments.

{% assign category_posts = site.posts | where_exp: "post", "post.category == 'Fiction' or post.categories contains 'Fiction'" | sort: "date" | reverse %}
{% include category-post-list.html posts=category_posts %}
