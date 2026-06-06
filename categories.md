---
layout: default
title: Categories
permalink: /categories/
---

# Categories

<div class="category-grid category-index">
  {% assign essays_posts = site.posts | where_exp: "post", "post.category == 'Essays' or post.categories contains 'Essays'" %}
  <a class="category-card" href="{{ '/categories/essays/' | relative_url }}">
    <strong>Essays</strong>
    <span>Long-form reflections on writing, reading, language, and tools.</span>
    <em>{{ essays_posts.size }} posts</em>
  </a>

  {% assign writing_tools_posts = site.posts | where_exp: "post", "post.category == 'Writing Tools' or post.categories contains 'Writing Tools'" %}
  <a class="category-card" href="{{ '/categories/writing-tools/' | relative_url }}">
    <strong>Writing Tools</strong>
    <span>Typewriters, keyboards, e-ink devices, software, and writing workflows.</span>
    <em>{{ writing_tools_posts.size }} posts</em>
  </a>

  {% assign reading_notes_posts = site.posts | where_exp: "post", "post.category == 'Reading Notes' or post.categories contains 'Reading Notes'" %}
  <a class="category-card" href="{{ '/categories/reading-notes/' | relative_url }}">
    <strong>Reading Notes</strong>
    <span>Book notes, quotations in context, and observations gathered while reading.</span>
    <em>{{ reading_notes_posts.size }} posts</em>
  </a>

  {% assign projects_posts = site.posts | where_exp: "post", "post.category == 'Projects' or post.categories contains 'Projects'" %}
  <a class="category-card" href="{{ '/categories/projects/' | relative_url }}">
    <strong>Projects</strong>
    <span>Project records, experiments, build logs, and design decisions.</span>
    <em>{{ projects_posts.size }} posts</em>
  </a>

  {% assign fiction_posts = site.posts | where_exp: "post", "post.category == 'Fiction' or post.categories contains 'Fiction'" %}
  <a class="category-card" href="{{ '/categories/fiction/' | relative_url }}">
    <strong>Fiction</strong>
    <span>Short stories, fragments, and fictional experiments.</span>
    <em>{{ fiction_posts.size }} posts</em>
  </a>
</div>
