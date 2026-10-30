"""Build the static savitas.net site from src/ into docs/ (served by GitHub Pages).

Each page is a content fragment at src/pages/<path>/index.html that starts with a
front-matter comment:

    <!--
    title: Managed Services
    description: One sentence for search results.
    -->

Optional keys: `redirect: /new/path/` (emit a redirect stub instead of a page) and
`full_width: true` (the fragment supplies its own containers, e.g. the home hero).

Usage:  python build.py            build into docs/
        python build.py --check    build, then fail on broken internal links
"""
import datetime
import html
import os
import re
import shutil
import sys
import urllib.parse

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "src")
PAGES = os.path.join(SRC, "pages")
STATIC = os.path.join(SRC, "static")
OUT = os.path.join(ROOT, "docs")
SITE_URL = "https://savitas.net"
SITE_NAME = "Savitas"
# The home page deliberately shows no street address or location.
LOCATION_LABEL = '        <span class="d-none d-sm-inline">Hastings, Florida</span>\n'
FOOTER_ADDRESS = "            4255 Benedict St.<br>\n            Hastings, FL 32145<br>\n"

# (label, url) items; ("-", None) is a divider; ("#Header", None) is a section header.
WHO_WE_ARE = [
    ("Overview", "/Pages/WhoWeAre/"),
    ("Leadership", "/Pages/WhoWeAre/Leadership/"),
    ("Project History", "/Pages/WhoWeAre/ProjectHistory/"),
    ("Partners", "/Pages/WhoWeAre/Partners/"),
    ("News & Events", "/Pages/WhoWeAre/NewsAndEvents/"),
    ("-", None),
    ("Contact Us", "/Pages/Contact/"),
    ("Request Appointment", "/Pages/RequestAppointment/"),
]
WHAT_WE_DO = [  # columns of the mega menu
    [
        ("#Services", "/Pages/WhatWeDo/Services/"),
        ("Consulting", "/Pages/WhatWeDo/Services/Consulting/"),
        ("CIO Services", "/Pages/WhatWeDo/Services/CIOServices/"),
        ("Networking & Telecommunications", "/Pages/WhatWeDo/Services/NetworkingAndTelecommunications/"),
        ("Staff Augmentation", "/Pages/WhatWeDo/Services/StaffAugmentation/"),
        ("Staffing", "/Pages/WhatWeDo/Services/Staffing/"),
        ("Software Asset Management", "/Pages/WhatWeDo/Services/SoftwareAssetManagement/"),
        ("System Maintenance Plans", "/Pages/WhatWeDo/Services/SystemMaintenancePlans/"),
        ("Service Plans", "/Pages/WhatWeDo/Services/ServicePlans/"),
        ("Training", "/Pages/WhatWeDo/Services/Training/"),
        ("Vendor Management", "/Pages/WhatWeDo/Services/VendorManagement/"),
        ("#How We Bill", None),
        ("Hourly", "/Pages/WhatWeDo/Services/Hourly/"),
        ("Flat Fee", "/Pages/WhatWeDo/Services/FlatFee/"),
        ("Service Policies", "/Pages/WhatWeDo/Services/ServicePolicies/"),
    ],
    [
        ("#Solutions", "/Pages/WhatWeDo/Solutions/"),
        ("Managed Services", "/Pages/WhatWeDo/Solutions/ManagedServices/"),
        ("Cloud", "/Pages/WhatWeDo/Solutions/Cloud/"),
        ("Security", "/Pages/WhatWeDo/Solutions/Security/"),
        ("Business Intelligence", "/Pages/WhatWeDo/Solutions/BusinessIntelligence/"),
        ("Document Management", "/Pages/WhatWeDo/Solutions/DocumentManagement/"),
        ("Finance & Accounting", "/Pages/WhatWeDo/Solutions/FinanceAndAccounting/"),
        ("SharePoint", "/Pages/WhatWeDo/Solutions/SharePointSolutions/"),
        ("Systems Integration", "/Pages/WhatWeDo/Solutions/SystemsIntegration/"),
        ("Solution Architecture", "/Pages/WhatWeDo/Solutions/SolutionArchitecture/"),
        ("Advanced Solutions", "/Pages/WhatWeDo/Solutions/AdvancedSolutions/"),
        ("Application Lifecycle Management", "/Pages/WhatWeDo/Solutions/ApplicationLifecycleManagement (ALM)/"),
        ("Hardware as a Service", "/Pages/WhatWeDo/Solutions/HardwareAsAService (HAAS)/"),
        ("Software as a Service", "/Pages/WhatWeDo/Solutions/SoftwareAsAService (SAAS)/"),
        ("System Assessments", "/Pages/WhatWeDo/Solutions/SystemAssessment/"),
        ("Network Assessments", "/Pages/WhatWeDo/Solutions/NetworkAssessments/"),
        ("VoIP & Cloud Phone Systems", "/Pages/WhatWeDo/Solutions/VOIPCloudPhoneSystems/"),
    ],
    [
        ("#Retail Point of Sale", "/Pages/WhatWeDo/Solutions/RetailPointOfSale/"),
        ("Microsoft Dynamics RMS", "/Pages/WhatWeDo/Solutions/RetailPointOfSale/MicrosoftDynamicsRMS/"),
        ("Retail Management Hero", "/Pages/WhatWeDo/Solutions/RetailPointOfSale/RetailManagementHero/"),
        ("#Software Development", "/Pages/WhatWeDo/SoftwareDevelopment/"),
        ("Custom Software", "/Pages/WhatWeDo/SoftwareDevelopment/CustomSoftware/"),
        ("Packaged Software", "/Pages/WhatWeDo/SoftwareDevelopment/PackagedSoftware/"),
        ("Web Development", "/Pages/WhatWeDo/SoftwareDevelopment/WebSoftwareDevelopment/"),
        ("Mobile Development", "/Pages/WhatWeDo/SoftwareDevelopment/Mobile/"),
        ("-", None),
        ("What We Do overview", "/Pages/WhatWeDo/"),
    ],
]
WHO_WE_SERVE = [
    ("Overview", "/Pages/WhoWeServe/"),
    ("#By Size", "/Pages/WhoWeServe/BySize/"),
    ("Small Business", "/Pages/WhoWeServe/BySize/#SmallBusiness"),
    ("Medium Business", "/Pages/WhoWeServe/BySize/#MediumBusiness"),
    ("Large Business", "/Pages/WhoWeServe/BySize/#LargeBusiness"),
    ("#By Industry", "/Pages/WhoWeServe/ByIndustry/"),
    ("Construction", "/Pages/WhoWeServe/ByIndustry/Construction/"),
    ("Education", "/Pages/WhoWeServe/ByIndustry/Education/"),
    ("Financial Services", "/Pages/WhoWeServe/ByIndustry/FinancialServices/"),
    ("Government", "/Pages/WhoWeServe/ByIndustry/Government/"),
    ("Retail", "/Pages/WhoWeServe/ByIndustry/Retail/"),
]

FRONT = re.compile(r"\A\s*<!--\s*\n(.*?)\n\s*-->\s*\n?", re.S)
esc = html.escape


def url_attr(url):
    return esc(url.replace(" ", "%20"), quote=True)


def read_page(path):
    raw = open(path, encoding="utf-8").read()
    meta = {}
    m = FRONT.match(raw)
    if m:
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
        raw = raw[m.end():]
    return meta, raw.strip()


def page_url(rel):
    return "/" if rel in ("", ".") else "/" + rel.strip("/") + "/"


def item_html(label, url, current, indent):
    pad = " " * indent
    if label == "-":
        return f'{pad}<li><hr class="dropdown-divider"></li>'
    if label.startswith("#"):
        text = esc(label[1:])
        if url:
            active = ' active" aria-current="page' if url == current else ""
            return f'{pad}<li><a class="dropdown-header d-block text-decoration-none{active}" href="{url_attr(url)}">{text}</a></li>'
        return f'{pad}<li><h3 class="dropdown-header">{text}</h3></li>'
    active = ' active" aria-current="page' if url == current else ""
    return f'{pad}<li><a class="dropdown-item{active}" href="{url_attr(url)}">{esc(label)}</a></li>'


def section_active(current, items):
    urls = [u for col in (items if items and isinstance(items[0], list) else [items]) for _, u in col if u]
    return any(current == u.split("#")[0] for u in urls)


def render_nav(current):
    out = ['          <ul class="navbar-nav ms-auto align-items-lg-center">']

    def dropdown(label, items, mega=False):
        active = " active" if section_active(current, items) else ""
        li_cls = "nav-item dropdown dropdown-mega" if mega else "nav-item dropdown"
        out.append(f'            <li class="{li_cls}">')
        out.append(f'              <a class="nav-link dropdown-toggle{active}" href="#" role="button" data-bs-toggle="dropdown" aria-expanded="false">{esc(label)}</a>')
        if mega:
            out.append('              <div class="dropdown-menu">')
            out.append('                <div class="row g-0">')
            for col in items:
                out.append('                  <div class="col-lg-4 mega-col">')
                out.append('                    <ul class="list-unstyled mb-0">')
                out.extend(item_html(l, u, current, 22) for l, u in col)
                out.append("                    </ul>")
                out.append("                  </div>")
            out.append("                </div>")
            out.append("              </div>")
        else:
            out.append('              <ul class="dropdown-menu">')
            out.extend(item_html(l, u, current, 16) for l, u in items)
            out.append("              </ul>")
        out.append("            </li>")

    dropdown("Who We Are", WHO_WE_ARE)
    dropdown("What We Do", WHAT_WE_DO, mega=True)
    dropdown("Who We Serve", WHO_WE_SERVE)
    out.append('            <li class="nav-item nav-cta ms-lg-2"><a class="btn btn-accent" href="/Pages/RequestAppointment/">Request Appointment</a></li>')
    out.append("          </ul>")
    return "\n".join(out)


def render_breadcrumb(url, titles):
    if url == "/":
        return ""
    parts = [p for p in url.strip("/").split("/")]
    crumbs = [("Home", "/")]
    for i in range(1, len(parts)):
        anc = "/" + "/".join(parts[:i]) + "/"
        if anc in titles:
            crumbs.append((titles[anc], anc))
    items = [f'<li class="breadcrumb-item"><a href="{url_attr(u)}">{esc(t)}</a></li>' for t, u in crumbs]
    items.append(f'<li class="breadcrumb-item active" aria-current="page">{esc(titles.get(url, ""))}</li>')
    return (
        '  <nav class="crumb-bar" aria-label="Breadcrumb">\n'
        '    <div class="container"><ol class="breadcrumb">' + "".join(items) + "</ol></div>\n"
        "  </nav>\n"
    )


def render_redirect(target):
    t = url_attr(target)
    return (
        "<!doctype html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n"
        f"<title>Redirecting…</title>\n<link rel=\"canonical\" href=\"{SITE_URL}{t}\">\n"
        f"<meta http-equiv=\"refresh\" content=\"0; url={t}\">\n<meta name=\"robots\" content=\"noindex\">\n"
        f"</head>\n<body><p>This page has moved to <a href=\"{t}\">{esc(target)}</a>.</p></body>\n</html>\n"
    )


def render_page(layout, meta, body, url, titles):
    title = meta.get("title", "Savitas")
    page_title = meta.get("page_title") or (f"{title} | {SITE_NAME}" if url != "/" else "Savitas Strategic Software Solutions | IT Consulting, Managed Services & Software")
    if meta.get("full_width") == "true":
        main = body
    else:
        main = '    <div class="container">\n' + body + "\n    </div>"
    values = {
        "page_title": esc(page_title),
        "description": esc(meta.get("description", ""), quote=True),
        "canonical": SITE_URL + url_attr(url),
        "robots": '\n  <meta name="robots" content="noindex">' if meta.get("noindex") == "true" else "",
        "nav": render_nav(url),
        "breadcrumb": render_breadcrumb(url, titles),
        "main": main,
        "year": str(datetime.date.today().year),
        "location_label": "" if url == "/" else LOCATION_LABEL,
        "footer_address": "" if url == "/" else FOOTER_ADDRESS,
    }
    return re.sub(r"\{\{(\w+)\}\}", lambda m: values[m.group(1)], layout)


def clean_out():
    os.makedirs(OUT, exist_ok=True)
    for child in os.listdir(OUT):
        p = os.path.join(OUT, child)
        shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)


def check_links():
    """Return internal href/src targets in docs/ that don't resolve to a file."""
    broken = []
    for root, _, files in os.walk(OUT):
        for f in files:
            if not f.endswith(".html"):
                continue
            src = os.path.join(root, f)
            text = open(src, encoding="utf-8").read()
            for ref in re.findall(r'(?:href|src)="(/[^"#?]*)', text):
                path = urllib.parse.unquote(html.unescape(ref))
                target = os.path.join(OUT, path.lstrip("/"))
                if path.endswith("/"):
                    target = os.path.join(target, "index.html")
                if not os.path.exists(target):
                    broken.append((os.path.relpath(src, OUT), ref))
    return broken


def main():
    layout = open(os.path.join(SRC, "layout.html"), encoding="utf-8").read()
    pages = []
    for root, _, files in os.walk(PAGES):
        if "index.html" in files:
            rel = os.path.relpath(root, PAGES).replace("\\", "/")
            meta, body = read_page(os.path.join(root, "index.html"))
            pages.append((page_url(rel), meta, body))
    titles = {u: m["title"] for u, m, _ in pages if "title" in m}

    clean_out()
    shutil.copytree(STATIC, OUT, dirs_exist_ok=True)

    sitemap = []
    for url, meta, body in sorted(pages):
        dest = os.path.join(OUT, url.strip("/"), "index.html") if url != "/" else os.path.join(OUT, "index.html")
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        if "redirect" in meta:
            out = render_redirect(meta["redirect"])
        else:
            out = render_page(layout, meta, body, url, titles)
            if meta.get("noindex") != "true":
                sitemap.append(url)
        open(dest, "w", encoding="utf-8", newline="\n").write(out)

    nf_meta, nf_body = read_page(os.path.join(SRC, "404.html"))
    open(os.path.join(OUT, "404.html"), "w", encoding="utf-8", newline="\n").write(
        render_page(layout, nf_meta, nf_body, "/404.html", titles)
    )

    today = datetime.date.today().isoformat()
    xml = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    xml += [f"  <url><loc>{SITE_URL}{url_attr(u)}</loc><lastmod>{today}</lastmod></url>" for u in sitemap]
    xml.append("</urlset>")
    open(os.path.join(OUT, "sitemap.xml"), "w", encoding="utf-8", newline="\n").write("\n".join(xml) + "\n")

    print(f"built {len(pages)} pages ({len(sitemap)} in sitemap) into {OUT}")
    broken = check_links()
    for src, ref in broken:
        print(f"BROKEN LINK  {src} -> {ref}")
    if "--check" in sys.argv and broken:
        sys.exit(1)


if __name__ == "__main__":
    main()
