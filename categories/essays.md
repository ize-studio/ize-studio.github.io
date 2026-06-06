---
layout: default
title: Essays
permalink: /categories/essays/
---

# Essays

Long-form reflections on writing, reading, language, and tools.

{% assign category_posts = site.posts | where_exp: "post", "post.category == 'Essays' or post.categories contains 'Essays'" | sort: "date" | reverse %}
{% include category-post-list.html posts=category_posts %}
