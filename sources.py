import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0"}

KEYWORDS = [
    "MOTHRA",
    "Optical Telephoto Hyperspectral Robotic Array",
]

def fetch_google_news():
    items = []
    for kw in KEYWORDS:
        url = f"https://news.google.com/search?q={kw.replace(' ', '+')}"
        r = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(r.text, "html.parser")

        for a in soup.select("article h3 a"):
            title = a.text
            link = "https://news.google.com" + a["href"][1:]
            items.append((title, link))
    return items

def fetch_reddit():
    items = []
    for kw in KEYWORDS:
        url = f"https://www.reddit.com/search/?q={kw.replace(' ', '%20')}"
        r = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(r.text, "html.parser")

        for a in soup.select("a[data-click-id='body']"):
            title = a.text
            link = "https://reddit.com" + a["href"]
            items.append((title, link))
    return items

def fetch_general_web():
    items = []
    for kw in KEYWORDS:
        url = f"https://duckduckgo.com/html/?q={kw.replace(' ', '+')}"
        r = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(r.text, "html.parser")

        for a in soup.select(".result__a"):
            title = a.text
            link = a["href"]
            items.append((title, link))
    return items

def fetch_all():
    results = []
    for fn in [fetch_google_news, fetch_reddit, fetch_general_web]:
        try:
            results.extend(fn())
        except Exception as e:
            print("Error:", fn.__name__, e)

    seen = set()
    unique = []
    for title, link in results:
        if link not in seen:
            seen.add(link)
            unique.append((title, link))

    return unique
