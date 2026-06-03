---
layout: default
title: Categories
permalink: /categories/
---

# Categories

<div class="category-sections">
  <section id="essays">
    <h2>Essays</h2>
    <p>Long-form reflections on writing, reading, language, and tools.</p>
    {% assign category_posts = site.posts | where: "category", "Essays" %}
    {% include category-post-list.html posts=category_posts %}
  </section>

  <section id="writing-tools">
    <h2>Writing Tools</h2>
    <p>Notes on typewriters, keyboards, e-ink devices, software, and writing workflows.</p>
    {% assign category_posts = site.posts | where: "category", "Writing Tools" %}
    {% include category-post-list.html posts=category_posts %}
  </section>

  <section id="reading-notes">
    <h2>Reading Notes</h2>
    <p>Book notes, quotations in context, and observations gathered while reading.</p>
    {% assign category_posts = site.posts | where: "category", "Reading Notes" %}
    {% include category-post-list.html posts=category_posts %}
  </section>

  <section id="projects">
    <h2>Projects</h2>
    <p>Project records, experiments, build logs, and design decisions.</p>
    {% assign category_posts = site.posts | where: "category", "Projects" %}
    {% include category-post-list.html posts=category_posts %}
  </section>

  <section id="fiction">
    <h2>Fiction</h2>
    <p>Short stories, fragments, and fictional experiments.</p>
    {% assign category_posts = site.posts | where: "category", "Fiction" %}
    {% include category-post-list.html posts=category_posts %}
  </section>
</div>
