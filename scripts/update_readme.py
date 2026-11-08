"""Replace the 'Recent writing' block in README.md with the latest posts from the site's RSS feed."""

import re
import urllib.request
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

FEED = "https://udayprakash.com/rss.xml"
COUNT = 3

with urllib.request.urlopen(FEED, timeout=30) as response:
    root = ET.fromstring(response.read())

lines = []
for item in root.iter("item"):
    title = (item.findtext("title") or "").strip()
    link = (item.findtext("link") or "").strip()
    date = item.findtext("pubDate")
    day = parsedate_to_datetime(date).strftime("%d %b %Y") if date else ""
    if title and link:
        lines.append(f"- [{title}]({link}) {day}".rstrip())
    if len(lines) == COUNT:
        break

block = "\n".join(lines) if lines else "- Coming soon"
with open("README.md", encoding="utf-8") as f:
    readme = f.read()

updated = re.sub(
    r"(<!-- writing starts -->\n).*?(<!-- writing ends -->)",
    lambda m: m.group(1) + block + "\n" + m.group(2),
    readme,
    flags=re.S,
)

with open("README.md", "w", encoding="utf-8") as f:
    f.write(updated)
