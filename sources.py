import requests
import feedparser
from datetime import datetime, timezone, timedelta
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "mothra-bot"}

# -----------------------------
# BOOLEAN SEARCH QUERY
# -----------------------------
SEARCH_QUERY = '(("Optical Telephoto Hyperspectral Robotic Array" OR MOTHRA OR Gerko) AND (space OR cosmic OR universe OR telescope)) -Godzilla -MACS0416'

# -----------------------------
# Time filter (last 30 days)
# -----------------------------
def is_recent(published_time):
    cutoff = datetime.now(timezone.utc) - timedelta(days=30)
    return published_time >= cutoff


# -----------------------------
# Google News RSS
# -----------------------------
def fetch_google_news():
    items = []

    url = f"https://news.google.com/rss/search?q={SEARCH_QUERY.replace(' ', '+')}+when:30d"
    feed = feedparser.parse(url)

    for entry in feed.entries:
        published = entry.get("published_parsed")

        if published:
            published_dt = datetime(*published[:6], tzinfo=timezone.utc)
            if not is_recent(published_dt):
                continue

        text = entry.title + " " + getattr(entry, "summary", "")
        items.append((text, entry.link))

    return items


# -----------------------------
# DuckDuckGo (general web)
# -----------------------------
def fetch_duckduckgo():
    items = []

    url = f"https://duckduckgo.com/html/?q={SEARCH_QUERY.replace(' ', '+')}"
    r = requests.get(url, headers=HEADERS)

    soup = BeautifulSoup(r.text, "html.parser")

    for result in soup.select(".result"):
        title_tag = result.select_one(".result__a")

        if not title_tag:
            continue

        title = title_tag.get_text(strip=True)
        link = title_tag.get("href")

        if link and link.startswith("http"):
            items.append((title, link))

    return items


# -----------------------------
# BOOLEAN FILTER (FINAL LOGIC)
# -----------------------------
GROUP_A = [
    "optical telephoto hyperspectral robotic array",
    "mothra",
    "gerko"
]

GROUP_B = [
    "space",
    "cosmic",
    "universe",
    "telescope"
]

EXCLUDE = [
    "godzilla",
    "macs0416",
    "movie",
    "film",
    "kaiju"
]


def is_relevant(text):
    t = text.lower()

    include_main = ["mothra", "optical telephoto hyperspectral robotic array", "gerko", "dragonfly"]
    context = ["telescope", "array", "cosmic", "space", "universe"]

    exclude = ["godzilla", "macs0416", "movie", "film", "kaiju"]

    return (
        any(term in t for term in include_main)
        and any(term in t for term in context)
        and not any(term in t for term in exclude)
    )

# -----------------------------
# Deduplication
# -----------------------------
def deduplicate(items):
    seen = set()
    unique = []

    for title, link in items:
        if link not in seen:
            seen.add(link)
            unique.append((title, link))

    return unique


# -----------------------------
# MASTER FUNCTION
# -----------------------------
def fetch_all():
    results = []

    for fn in [fetch_google_news, fetch_duckduckgo]:
        try:
            results.extend(fn())
        except Exception as e:
            print("Error:", fn.__name__, e)

    # Apply Boolean filter
    results = [item for item in results if is_relevant(item[0])]

    # Deduplicate
    results = deduplicate(results)

    return results
