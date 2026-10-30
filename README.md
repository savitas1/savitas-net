# savitas.net

Website of Savitas Strategic Software Solutions LLC, served by GitHub Pages
from the `docs/` folder on `main` at https://savitas.net.

## Editing the site

The site is generated. Edit files under `src/`, never `docs/` directly.

| Path | What it is |
|------|------------|
| `src/pages/<url path>/index.html` | Page content: a front-matter comment followed by the HTML that goes inside `<main>` |
| `src/layout.html` | Shared page shell: header, navigation, breadcrumb, footer |
| `src/404.html` | Not-found page (written to `docs/404.html`) |
| `src/static/` | Copied verbatim: CSS, JS, images, vendored Bootstrap, `CNAME`, `.nojekyll`, `robots.txt` |
| `build.py` | Generator; the main navigation menu is defined at the top of this file |

Front matter at the top of each page:

```html
<!--
title: Managed Services
description: One sentence for search results (120–155 characters).
-->
```

Optional keys: `redirect: /new/path/` turns the page into a redirect stub,
`full_width: true` lets the page supply its own containers (used by the home
page hero), `noindex: true` hides it from search engines and the sitemap, and
`page_title:` overrides the browser tab title.

Build, check for broken internal links, and preview:

```
python build.py --check
python -m http.server 8123 --directory docs
```

Then commit `src/` and `docs/` together and push to `main`. GitHub Pages
rebuilds within a minute or two. The build stamps the footer copyright with
the current year, so rebuilding in a new year updates it.

The stack is Bootstrap 5.3.3 (vendored in `src/static/vendor/bootstrap`, no
CDN), one small script for the appointment form, and no other dependencies.
`build.py` uses only the Python standard library.

## History

- The original site was an ASP.NET WebForms application (Bootstrap 3, jQuery)
  online from at least 2002 until October 2019. It was recovered from the
  Internet Archive Wayback Machine on 2026-10-27, then rebuilt on this static
  generator and its content refreshed for 2026 on 2026-10-29.
- The old customer portal (log in / register) is retired; those URLs show a
  notice. The appointment form composes an email in the visitor's own mail
  app because there is no server.
- Old URLs are preserved, including duplicate variants such as
  `ApplicationLifecycleManagement+(ALM)`, which now redirect to the canonical
  page.
