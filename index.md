---
layout: default
title: Home
---

<section class="intro">
  <p class="kicker">Ize Studio</p>
  <h1>Essays on writing, reading, typewriters, e-ink tools, and the making of Ize Compose.</h1>
  <p>
    An English archive for essays, fiction, reading notes, tool reflections, and project records.
  </p>
</section>

<section class="section">
  <div class="section-heading">
    <h2>Latest Posts</h2>
  </div>

  {% if site.posts.size > 0 %}
    <div class="post-list">
      {% for post in site.posts limit: 8 %}
        <article class="post-item">
          <a href="{{ post.url | relative_url }}">
            <span class="post-meta">{{ post.date | date: "%B %-d, %Y" }}{% if post.category %} &middot; {{ post.category }}{% endif %}</span>
            <h3>{{ post.title }}</h3>
            {% if post.excerpt %}
              <p>{{ post.excerpt | strip_html | truncate: 180 }}</p>
            {% endif %}
          </a>
        </article>
      {% endfor %}
    </div>
  {% else %}
    <p class="empty">No posts yet. The archive is ready for its first essay.</p>
  {% endif %}
</section>

<section class="section">
  <div class="section-heading">
    <h2>Categories</h2>
  </div>

  <div class="category-grid">
    <a href="{{ '/categories/essays/' | relative_url }}">Essays</a>
    <a href="{{ '/categories/writing-tools/' | relative_url }}">Writing Tools</a>
    <a href="{{ '/categories/reading-notes/' | relative_url }}">Reading Notes</a>
    <a href="{{ '/categories/projects/' | relative_url }}">Projects</a>
    <a href="{{ '/categories/fiction/' | relative_url }}">Fiction</a>
  </div>
</section>
