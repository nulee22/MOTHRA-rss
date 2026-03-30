from feedgen.feed import FeedGenerator
from datetime import datetime
from sources import fetch_all

fg = FeedGenerator()
fg.title("MOTHRA Telescope Monitoring Feed")
fg.link(href="https://github.com/YOUR_USERNAME/mothra-rss")
fg.description("Tracking MOTHRA telescope coverage")

entries = fetch_all()

for title, link in entries[:100]:
    fe = fg.add_entry()
    fe.title(title)
    fe.link(href=link)
    fe.pubDate(datetime.utcnow())

fg.rss_file("feed.xml")
