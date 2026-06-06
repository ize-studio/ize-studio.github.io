---
layout: default
title: Projects
permalink: /categories/projects/
---

# Projects

Project records, experiments, build logs, and design decisions.

{% assign category_posts = site.posts | where_exp: "post", "post.category == 'Projects' or post.categories contains 'Projects'" | sort: "date" | reverse %}
{% include category-post-list.html posts=category_posts %}
