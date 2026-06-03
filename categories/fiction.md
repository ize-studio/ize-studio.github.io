---
layout: default
title: Fiction
permalink: /categories/fiction/
---

# Fiction

Short stories, fragments, and fictional experiments.

{% assign category_posts = site.posts | where: "category", "Fiction" %}
{% include category-post-list.html posts=category_posts %}
