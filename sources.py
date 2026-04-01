import requests
import feedparser
from datetime import datetime, timezone, timedelta
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "mothra-bot"}

# -----------------------------
# SIMPLE SEARCH QUERIES (IMPORTANT)
# -----------------------------
SEARCH_QUERIES = [
    "MOTHRA telescope",
    "MOTHRA Canon lenses telescope",
    "all lens telescope cosmic web",
    "Dragonfly telescope array",
    "van Dokkum telescope",
    "cosmic web telescope"
]

# -----------------------------
# Time filter (30 days)
# -----------------------------
def is_recent(published_time):
    cutoff = datetime.now(timezone.utc) - timedelta(days=30)
    return published_time >= cutoff


# -----------------------------
# Google News RSS (PRIMARY SOURCE)
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
# DuckDuckGo (GENERAL WEB)
# -----------------------------
def fetch_duckduckgo():
    items = []

    for q in SEARCH_QUERIES:

        # 🔁 paginate (first 2 pages)
        for start in [0, 30]:
            url = f"https://duckduckgo.com/html/?q={q.replace(' ', '+')}&s={start}"

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
# BOOLEAN FILTER (CORRECT PLACE)
# -----------------------------
def is_relevant(text):
    t = text.lower()

    group_a = [
        "mothra",
        "optical telephoto hyperspectral robotic array",
        "gerko"
    ]

    group_b = [
        "space",
        "cosmic",
        "universe",
        "telescope",
        "dragonfly",
        "van dokkum"
    ]

    exclude = [
        "godzilla",
        "macs0416",
        "movie",
        "film",
        "kaiju"
    ]

    return (
        any(term in t for term in group_a)
        and any(term in t for term in group_b)
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

    print("RAW results:", len(results))

    # Apply Boolean filtering
    results = [item for item in results if is_relevant(item[0])]

    print("AFTER filter:", len(results))

    # Deduplicate
    results = deduplicate(results)

    return results
