from feedgen.feed import FeedGenerator
from datetime import datetime, timezone
from sources import fetch_all

fg = FeedGenerator()
fg.title("MOTHRA Telescope Monitoring Feed")
fg.link(href="https://github.com/YOUR_USERNAME/mothra-rss")
fg.description("Tracking MOTHRA telescope coverage")

entries = fetch_all()

print("Entries found:", len(entries))

for text, link in entries[:100]:
    fe = fg.add_entry()
    fe.title(text[:200])
    fe.link(href=link)
    fe.pubDate(datetime.now(timezone.utc))

fg.rss_file("feed.xml")
print("Feed generated")
