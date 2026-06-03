---
layout: default
title: Projects
permalink: /categories/projects/
---

# Projects

Project records, experiments, build logs, and design decisions.

{% assign category_posts = site.posts | where: "category", "Projects" %}
{% include category-post-list.html posts=category_posts %}
