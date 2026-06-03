---
layout: default
title: Reading Notes
permalink: /categories/reading-notes/
---

# Reading Notes

Book notes, quotations in context, and observations gathered while reading.

{% assign category_posts = site.posts | where: "category", "Reading Notes" %}
{% include category-post-list.html posts=category_posts %}
