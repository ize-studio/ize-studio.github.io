---
layout: default
title: Categories
permalink: /categories/
---

# Categories

<div class="category-grid category-index">
  {% assign essays_posts = site.posts | where: "category", "Essays" %}
  <a href="{{ '/categories/essays/' | relative_url }}">
    <strong>Essays</strong>
    <span>{{ essays_posts.size }} posts</span>
  </a>

  {% assign writing_tools_posts = site.posts | where: "category", "Writing Tools" %}
  <a href="{{ '/categories/writing-tools/' | relative_url }}">
    <strong>Writing Tools</strong>
    <span>{{ writing_tools_posts.size }} posts</span>
  </a>

  {% assign reading_notes_posts = site.posts | where: "category", "Reading Notes" %}
  <a href="{{ '/categories/reading-notes/' | relative_url }}">
    <strong>Reading Notes</strong>
    <span>{{ reading_notes_posts.size }} posts</span>
  </a>

  {% assign projects_posts = site.posts | where: "category", "Projects" %}
  <a href="{{ '/categories/projects/' | relative_url }}">
    <strong>Projects</strong>
    <span>{{ projects_posts.size }} posts</span>
  </a>

  {% assign fiction_posts = site.posts | where: "category", "Fiction" %}
  <a href="{{ '/categories/fiction/' | relative_url }}">
    <strong>Fiction</strong>
    <span>{{ fiction_posts.size }} posts</span>
  </a>
</div>
