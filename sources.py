import requests
import feedparser

HEADERS = {"User-Agent": "mothra-bot"}

# -----------------------------
# SEARCH QUERIES (broad intake)
# -----------------------------
SEARCH_QUERIES = [
    "MOTHRA telescope",
    "Optical Telephoto Hyperspectral Robotic Array",
    "Gerko telescope",
    "van Dokkum telescope",
    "Dragonfly telescope array"
]

# -----------------------------
# Google News RSS
# -----------------------------
def fetch_google_news():
    items = []

    for q in SEARCH_QUERIES:
        url = f"https://news.google.com/rss/search?q={q.replace(' ', '+')}"
        feed = feedparser.parse(url)

        for entry in feed.entries:
            text = entry.title + " " + getattr(entry, "summary", "")
            items.append((text, entry.link))

    return items


# -----------------------------
# Reddit (JSON API)
# -----------------------------
def fetch_reddit():
    items = []

    for q in SEARCH_QUERIES:
        url = f"https://www.reddit.com/search.json?q={q}&sort=new"
        r = requests.get(url, headers=HEADERS)

        try:
            data = r.json()
            for post in data["data"]["children"]:
                title = post["data"]["title"]
                link = "https://reddit.com" + post["data"]["permalink"]
                items.append((title, link))
        except:
            pass

    return items


# -----------------------------
# DuckDuckGo (optional)
# -----------------------------
def fetch_general_web():
    items = []

    for q in SEARCH_QUERIES:
        url = f"https://duckduckgo.com/html/?q={q.replace(' ', '+')}"
        r = requests.get(url, headers=HEADERS)

        from bs4 import BeautifulSoup
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
    "dragonfly"
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
        any(term in t for term in GROUP_A)   # (A OR B OR C)
        and any(term in t for term in GROUP_B)  # AND (X OR Y OR Z)
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

    for fn in [fetch_google_news, fetch_reddit, fetch_general_web]:
        try:
            results.extend(fn())
        except Exception as e:
            print("Error:", fn.__name__, e)

    # Apply Boolean logic
    results = [item for item in results if is_relevant(item[0])]

    # Deduplicate
    results = deduplicate(results)

    return results
