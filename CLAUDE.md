# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Static HTML website for otlstudio.com — the portfolio site for Outside The Lines Studio, an architecture firm by Colin Summers and Robert Whitehead. Originally a PHP/MySQL site on NetworkSolutions, converted to static HTML/CSS in 2026. Hosted on Cloudflare Pages.

## Development

There is no build system, package manager, or dev server. The site is pure static HTML/CSS with no JavaScript. Files are served as-is.

To preview locally: `python3 -m http.server`

To regenerate HTML from PHP sources: `python3 _tools/migrate.py` (requires old_otlstudio directory at sibling level)

## Architecture

- **style.css** — Single site-wide stylesheet (CSS variables, flexbox layout, responsive, CSS-only hamburger menu, CSS-only lightbox galleries)
- **Root HTML files** — Main site pages (index.html, mission.html, projects.html, journal.html, about.html, contact.html)
- **mission/** — Mission sub-pages (generating.html, plan.html)
- **projects/** — 52 individual project pages (named by project ID: YYYYMM##.html)
- **code/** — Colin's programming portfolio (index.html, jungle.html, tightcircle.html, ColinSummers.pdf)
- **images/** — All project photography (~710 JPEGs including thumbnails, plus images/big/ for larger versions)
- **_Media/** — Site-level images (logo, headshots, contact image)
- **_tools/** — Migration script (migrate.py)

## Conventions

- HTML5 doctype with UTF-8 encoding
- Responsive viewport (`width=device-width, initial-scale=1.0`)
- Single stylesheet: `style.css` (linked with relative paths based on directory depth)
- All pages share a common navbar and footer template
- No JavaScript is used anywhere on the site
- CSS-only lightbox galleries using `:target` pseudo-selector
- Gallery thumbnails use CSS Grid layout
- Grey/white theme with red accents (firebrick) using CSS custom properties
- Project images named YYYYMM##.jpg; thumbnails end with t (YYYYMM##t.jpg)
- Captions stored as text files in old_otlstudio/captions/ (YYYYMMDD##.txt)

## Project Database

52 projects spanning 1987-2006. Project metadata (name, city, state) is embedded in `_tools/migrate.py`. The projects cover residential and commercial architecture across PA, NY, NJ, RI, AL, NV, CA, IL, SD, and VT. Notable projects include The Slammer (Penn Jillette's Las Vegas residence) and The Castle (Henderson, NV).

## Deployment

Cloudflare Pages — no build step needed. Just serve the root directory as static files.
