import requests
import feedparser
from datetime import datetime, timezone, timedelta

HEADERS = {"User-Agent": "mothra-bot"}

# -----------------------------
# SEARCH QUERIES (broad intake)
# -----------------------------
SEARCH_QUERIES = [
    "MOTHRA telescope",
    "Optical Telephoto Hyperspectral Robotic Array",
    "Gerko telescope",
    "van Dokkum telescope",
    "Dragonfly telescope",
    "cosmic web telescope",
    "space telescope array"
]

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

    for q in SEARCH_QUERIES:
        url = f"https://news.google.com/rss/search?q={q.replace(' ', '+')}+when:30d"
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
# DuckDuckGo fallback
# -----------------------------
def fetch_general_web():
    items = []

    from bs4 import BeautifulSoup

    for q in SEARCH_QUERIES:
        url = f"https://duckduckgo.com/html/?q={q.replace(' ', '+')}"
        r = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(r.text, "html.parser")

        for a in soup.select(".result__a"):
            title = a.text
            link = a["href"]
            items.append((title, link))

    return items


# -----------------------------
# BOOLEAN FILTER (YOUR LOGIC)
# -----------------------------
GROUP_A = [
    "mothra",
    "optical telephoto hyperspectral robotic array",
    "gerko"
]

GROUP_B = [
    "telescope",
    "van dokkum",
    "dragonfly",
    "space",
    "cosmic"
]

EXCLUDE = [
    "movie",
    "film",
    "kaiju",
    "godzilla"
]


def is_relevant(text):
    t = text.lower()

    return (
        any(term in t for term in GROUP_A)      # (A OR B OR C)
        and any(term in t for term in GROUP_B)  # AND (X OR Y OR Z...)
        and not any(term in t for term in EXCLUDE)
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

    for fn in [fetch_google_news, fetch_general_web]:
        try:
            results.extend(fn())
        except Exception as e:
            print("Error:", fn.__name__, e)

    # Apply Boolean logic
    results = [item for item in results if is_relevant(item[0])]

    # Deduplicate
    results = deduplicate(results)

    return results
