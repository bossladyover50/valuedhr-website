#!/usr/bin/env python3
"""Apply repeatable SEO, privacy, sharing, and performance updates."""
from pathlib import Path
from datetime import datetime
import html, json, re

ROOT = Path(__file__).resolve().parents[1]
DOMAIN = "https://valuedhr.com"
OG = f"{DOMAIN}/assets/valuedhr-social-card.png"

def add_social_meta(text, title, desc, url, kind="website"):
    block = f'''\n<meta property="og:title" content="{html.escape(title, quote=True)}"/>\n<meta property="og:description" content="{html.escape(desc, quote=True)}"/>\n<meta property="og:url" content="{url}"/>\n<meta property="og:type" content="{kind}"/>\n<meta property="og:image" content="{OG}"/>\n<meta property="og:image:width" content="1200"/>\n<meta property="og:image:height" content="630"/>\n<meta property="og:image:alt" content="ValuedHR — Experience Valued Here"/>\n<meta name="twitter:card" content="summary_large_image"/>\n<meta name="twitter:title" content="{html.escape(title, quote=True)}"/>\n<meta name="twitter:description" content="{html.escape(desc, quote=True)}"/>\n<meta name="twitter:image" content="{OG}"/>\n<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml"/>\n<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png"/>'''
    text = re.sub(r'\s*<meta property="og:(?:title|description|url|type|image(?:\:[^"]+)?)"[^>]*?/?>', '', text)
    text = re.sub(r'\s*<meta name="twitter:[^"]+"[^>]*?/?>', '', text)
    text = re.sub(r'\s*<link rel="(?:icon|apple-touch-icon)"[^>]*?/?>', '', text)
    marker = re.search(r'<link rel="canonical"[^>]*?/?>', text)
    if marker:
        text = text[:marker.end()] + block + text[marker.end():]
    return text

def clean_third_party(text):
    text = re.sub(r'<script>window\.\$zoho=.*?</script>\s*', '', text, flags=re.S)
    text = re.sub(r'<script[^>]+(?:salesiq\.zohopublic\.com|cdn\.pagesense\.io)[^>]*></script>\s*', '', text)
    return text

def article_date(text):
    m = re.search(r'([A-Z][a-z]+ \d{1,2}, 20\d{2})', text)
    if not m: return None
    try: return datetime.strptime(m.group(1), "%B %d, %Y").date().isoformat()
    except ValueError: return None

def optimize_article(path):
    text = path.read_text()
    title = html.unescape(re.search(r'<title>(.*?)</title>', text, re.S).group(1)).replace(' | ValuedHR','')
    desc = html.unescape(re.search(r'<meta name="description" content="(.*?)"\s*/?>', text, re.S).group(1))
    url = f"{DOMAIN}/articles/{path.name}"
    text = add_social_meta(text, f"{title} | ValuedHR", desc, url, "article")
    text = re.sub(r'<link rel="preconnect"[^>]*?/?>', '', text)
    text = re.sub(r'<link href="https://fonts\.googleapis\.com[^>]*?/?>', '', text)
    text = re.sub(r'<style>.*?</style>', '<link rel="stylesheet" href="/assets/article.css"/>', text, count=1, flags=re.S)
    date = article_date(text) or "2026-01-01"
    schema = {"@context":"https://schema.org","@type":"Article","headline":title,
      "description":desc,"mainEntityOfPage":url,"image":OG,
      "author":{"@type":"Person","name":"Michelle Mendez","url":f"{DOMAIN}/#about"},
      "publisher":{"@type":"Organization","name":"ValuedHR","url":DOMAIN,"logo":{"@type":"ImageObject","url":f"{DOMAIN}/assets/valuedhr-social-card.png"}},
      "datePublished":date,"dateModified":date}
    replacement = '<script type="application/ld+json">'+json.dumps(schema,separators=(',',':'))+'</script>'
    text = re.sub(r'<script type="application/ld\+json">.*?</script>', lambda _m: replacement, text, count=1, flags=re.S)
    text = clean_third_party(text)
    if '/services/hr-consulting.html' not in text:
        text = text.replace('<div class="cta">', '<p><strong>Need hands-on support?</strong> Explore <a href="/services/hr-consulting.html" style="color:#2563eb;text-decoration:underline">fractional HR consulting for growing businesses</a>.</p><div class="cta">', 1)
    text = text.replace('</body>', '<script src="/assets/site.js" defer></script></body>')
    path.write_text(text)

def optimize_standard(path):
    text = path.read_text()
    tm = re.search(r'<title>(.*?)</title>', text, re.S)
    dm = re.search(r'<meta name="description" content="(.*?)"\s*/?>', text, re.S)
    cm = re.search(r'<link rel="canonical" href="(.*?)"\s*/?>', text)
    if tm and dm and cm:
        text = add_social_meta(text, html.unescape(tm.group(1)), html.unescape(dm.group(1)), cm.group(1))
    text = clean_third_party(text)
    if '/assets/site.js' not in text:
        text = text.replace('</body>', '<script src="/assets/site.js" defer></script></body>')
    path.write_text(text)

for p in sorted((ROOT/'articles').glob('*.html')): optimize_article(p)
for name in ('index.html','blog.html','use-cases.html','privacy.html','terms.html','services/hr-consulting.html','services/encore-coaching.html'):
    optimize_standard(ROOT/name)

# Complete sitemap for intentionally public pages.
pages = ['/', '/blog.html', '/use-cases.html', '/services/hr-consulting.html',
         '/services/encore-coaching.html', '/privacy.html', '/terms.html']
pages += [f'/articles/{p.name}' for p in sorted((ROOT/'articles').glob('*.html'))]
today = datetime.now().date().isoformat()
urls = '\n'.join(f'  <url><loc>{DOMAIN}{p}</loc><lastmod>{today}</lastmod></url>' for p in pages)
(ROOT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+urls+'\n</urlset>\n')
