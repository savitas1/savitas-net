# savitas.net — restored static site

Static restoration of the Savitas Strategic Software Solutions website
(savitas.net), recovered from the Internet Archive Wayback Machine on
2026-10-27.

## Provenance

- The original site was an ASP.NET WebForms application, last alive in
  October 2019 (returned 403 by December 2021; the domain was parked by
  September 2024).
- 112 unique archived URLs (pages, images, CSS, JS bundles) were pulled from
  Wayback captures, preferring the 2016–2019 era. The homepage is the
  2019-10-18 capture; most interior pages are 2016–2017 captures (the content
  was stable across that window).
- One partner image (`SelCert2cRGB_94x103.gif`) only existed in a 2011
  capture and was recovered from there. The glyphicons `.woff`/`.woff2` fonts
  were not archived intact and were replaced with the stock Bootstrap 3.3.7
  files.

## What was changed from the originals

- ASP.NET bundle URLs (`/Content/css?v=…`, `/bundles/*?v=…`,
  `*.axd?…`) were flattened into real files under `/_assets/`.
- All internal links were canonicalized to the static directory layout
  (`/Pages/.../` with `index.html`), including old `*.aspx` link variants.
- Google Analytics, Application Insights, and the Facebook SDK snippets were
  removed (dead accounts; they only produced console errors).
- Everything else — markup, copy, images, styling — is as archived.

## Known limitations (inherent to a static restore)

- `Register` / `Log in` / `Request Appointment` / contact forms render but do
  not post anywhere (the WebForms backend is gone).
- The "Customer Portal" nav link (`/fwlink/?linkid=10111`) pointed to an
  external redirect service that no longer exists.

## Serving it

Any static file server works, e.g.:

```
python -m http.server 8123 --directory site
```

The site must be served from the domain root (links are root-absolute).
