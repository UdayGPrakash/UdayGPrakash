"""Replace the 'Recent writing' block in README.md with the latest posts from the site's RSS feed."""

import re
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime

FEED = "https://udayprakash.com/rss.xml"
COUNT = 3
MAX_AGE = timedelta(days=365)  # only show posts from the last year

# Identify this feed client rather than sending urllib's generic User-Agent,
# which the site's edge currently rejects. Do not impersonate a browser.
request = urllib.request.Request(
    FEED,
    headers={
        "User-Agent": "UdayGPrakash-ProfileFeed/1.0 (+https://github.com/UdayGPrakash/UdayGPrakash)",
        "Accept": "application/rss+xml, application/xml;q=0.9",
    },
)
with urllib.request.urlopen(request, timeout=30) as response:
    root = ET.fromstring(response.read())

lines = []
for item in root.iter("item"):
    title = (item.findtext("title") or "").strip()
    link = (item.findtext("link") or "").strip()
    date = item.findtext("pubDate")
    published = parsedate_to_datetime(date) if date else None
    if not published or datetime.now(timezone.utc) - published > MAX_AGE:
        continue
    day = published.strftime("%d %b %Y")
    if title and link:
        lines.append(f"- [{title}]({link}) {day}".rstrip())
    if len(lines) == COUNT:
        break

block = "### Recent writing\n\n" + "\n".join(lines) if lines else ""
with open("README.md", encoding="utf-8") as f:
    readme = f.read()

updated = re.sub(
    r"(<!-- writing starts -->\n).*?(<!-- writing ends -->)",
    lambda m: m.group(1) + (block + "\n" if block else "") + m.group(2),
    readme,
    flags=re.S,
)

with open("README.md", "w", encoding="utf-8") as f:
    f.write(updated)
