# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

The marketing website for ValuedHR (a fractional HR / people-ops consultancy), deployed as static HTML to Hostinger. There is no build system, package manager, framework, or test suite — every page is a single self-contained `.html` file with inline `<style>` and `<script>` tags. Edit the HTML directly; there is nothing to compile.

## Pages

- `index.html` — the live homepage (Midnight Navy / Signal Blue palette, DM Sans + IBM Plex Mono). This is what visitors see at `valuedhr.com/`.
- `valuedhr-website.html` — an alternate/draft homepage concept ("AI + Human HR & Operations", Navy/Teal palette, Plus Jakarta Sans + Instrument Serif). Not linked from nav on any page; treat as a standalone variant, not a partial of `index.html`. Don't assume changes to one should be mirrored in the other unless asked.
- `blog.html` — the blog index. Article cards are hardcoded `<div class="article-card">` markup (not generated from a data file) with `data-cat` and `data-title` attributes; client-side JS in the trailing `<script>` block filters/searches by matching against those attributes (`updateGrid()`).
- `proposal.html` — a private, per-prospect rate card/proposal page. Marked `noindex, nofollow` and not linked from any nav — it's meant to be sent as a direct URL to individual leads, not discovered.
- `articles/*.html` — ~55 individual blog posts, one file per article. Each is a full standalone HTML document with its own copy of the nav, footer, and inline CSS (same DM Sans/IBM Plex Mono/Instrument Serif design tokens as `blog.html`), plus a `schema.org/Article` JSON-LD block in the head.

## Adding a new blog article

There's no template file or generator — copy the structure of an existing file in `articles/` (e.g. `articles/5-signs-youve-outgrown-managing-hr-yourself.html`) and adjust:
1. `<title>`, meta description, canonical URL, and the `Article` JSON-LD block (headline, datePublished, description).
2. The hero `<h2 class="cat">`/category tag, `<h1>`, and byline/date/read-time line.
3. The article body inside `.body`.
4. Then add a matching `<div class="article-card">` entry to `blog.html`'s grid, with `data-cat` and `data-title` set consistently so the existing filter/search JS picks it up.

Nav links across articles and blog pages use root-relative paths (`/index.html`, `/blog.html`, `/index.html#contact`) — keep new links consistent with that pattern.

## Design system conventions

`index.html` and `articles/*.html`/`blog.html` use two visually distinct but internally consistent token sets defined as CSS custom properties in each file's own `<style>` block (there's no shared stylesheet):
- **Homepage (`index.html`) system**: Midnight Navy `#0A1F3C` primary, Signal Blue `#3B82F6` accent, Sky `#9DC3FF`, Mist `#F5F6F8` background; `--color-*`, `--text-*`, `--space-*`, `--radius-*`, `--shadow-*` custom properties; fonts are DM Sans (body/display) + IBM Plex Mono (labels/eyebrows).
- **Blog/articles system**: same Navy/Signal Blue-family palette but shorthand var names (`--bg`, `--primary`, `--accent`, `--muted`), Instrument Serif for headings, Plus Jakarta Sans for body.
- **`valuedhr-website.html`/`proposal.html` system**: Navy `#0A1628` primary, Teal `#00888F` accent, warm cream `#F8F7F3` background, Plus Jakarta Sans + Instrument Serif.

When editing a page, reuse that file's existing custom properties rather than hardcoding new colors, and match whichever token/naming convention that file already uses.

## Third-party integrations

- **Zoho SalesIQ** chat widget — loaded via `$zoho.salesiq` script tag near the end of `<body>` on customer-facing pages.
- **PageSense** analytics — loaded via `cdn.pagesense.io` script on `blog.html`.
- The homepage contact form (`.contact-form` in `index.html`) has no backend — its submit handler (bottom of `index.html`) is a client-side-only demo that shows a "Request Received" state and resets; it does not actually send data anywhere. Don't assume form submissions are wired to an API.

## Deployment

There is no CI. `deploy.sh` and `setup-autodeploy.sh` are Michelle Mendez's personal machine scripts (hardcoded local `REPO_DIR` path, a local `.github-token` file for auth, and a macOS LaunchAgent that watches `index.html`/`blog.html` for changes and auto-commits/pushes to `main`). These are not meant to run in this environment — they document the deploy pipeline (push to `main` on GitHub → Hostinger auto-deploys) but reference a local filesystem layout that won't exist here. Commit messages from that pipeline follow the pattern `Site update — Month Day, Year`.

There are no lint, build, or test commands in this repo — verify changes by opening the edited HTML file in a browser.
