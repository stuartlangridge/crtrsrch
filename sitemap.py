#!/usr/bin/env python3

from xml.dom import minidom
import glob
import os
import datetime


dom = minidom.parseString('''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>https://kryogenix.org/crsearch/</loc>
        <changefreq>always</changefreq>
    </url>
    <url>
        <loc>https://kryogenix.org/crsearch/api.html</loc>
        <changefreq>monthly</changefreq>
    </url>
</urlset>
''')
for html in sorted(glob.glob(os.path.join(os.path.dirname(__file__), "html", "*.html"))):
    s = os.stat(html)
    loc = f"https://kryogenix.org/crsearch/{html}"
    lastmod = datetime.datetime.fromtimestamp(s.st_mtime)
    el = dom.createElement("url")
    lel = dom.createElement("loc")
    lel.appendChild(dom.createTextNode(loc))
    el.appendChild(lel)
    dom.documentElement.appendChild(el)

with open(os.path.join(os.path.dirname(__file__), "sitemap.xml"), mode="w", encoding="utf-8") as fp:
    fp.write(dom.toprettyxml())