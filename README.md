# BOUNDARY

Writing, projects, machines, and objects by RUP L.

This is the source repository for the BOUNDARY GitHub Pages site. It is currently published through the `ize-studio` GitHub account.

The site is a Jekyll archive for essays, fiction, reading notes, writing tools, project records, Korean writing links, and future small editions or objects.

## Local Run

```sh
bundle exec jekyll build
bundle exec jekyll serve
```

This repository is built by GitHub Actions and published to `ize-studio/ize-studio.github.io`.

## Structure

- `_posts/`: English archive posts. Existing post URLs use `/posts/:categories/:title.html`.
- `writing/`: editorial writing index.
- `fiction/`: fiction index.
- `projects/`: project record index.
- `shop/`: object and edition shelf.
- `_products/`: optional product collection. Draft products are not shown.
- `_data/brunch.json`: cached Brunch article metadata.
- `scripts/fetch_brunch.py`: Brunch metadata sync script.

## Adding a Post

Add Markdown files to `_posts` using the Jekyll filename format:

```text
YYYY-MM-DD-title.md
```

Front matter:

```yaml
---
layout: post
title: "Post Title"
date: 2026-06-03
category: Essays
---
```

`category` and `categories` are both accepted:

```yaml
category: Essays
```

```yaml
categories: [Essays]
```

Category aliases include singular, plural, and Korean names for the existing archive pages.

## Adding a Product

Add a Markdown file to `_products/`:

```yaml
---
title: "Object Title"
category: Book
year: 2026
status: upcoming
price:
currency: KRW
cover:
purchase_url:
---
```

Supported status values:

- `available`
- `soldout`
- `upcoming`
- `archive`
- `draft`

`draft` products are not shown on the site.

## Brunch Sync

The Brunch cache is metadata only. It stores title, URL, date, excerpt, thumbnail, source, and language.

Run manually:

```sh
python scripts/test_fetch_brunch.py
python scripts/fetch_brunch.py
```

The scheduled workflow is `.github/workflows/sync-brunch.yml`. If parsing returns zero posts or fails, the script keeps the previous `_data/brunch.json` cache.

## Deploy

`.github/workflows/publish.yml` builds this source repository with Jekyll and publishes the generated site to the public GitHub Pages repository.
