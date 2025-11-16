from firecrawl import FirecrawlApp
from rich import print

app = FirecrawlApp(api_url="http://localhost:3002/v2", api_key="a")

doc = app.scrape(
    "https://yenslife.top/2025/08/14/macos-sudo-pam-fix/",
    formats=["markdown", "html"],
)
print(doc)

# Crawl a website
# response = app.crawl(
#     "https://yenslife.top",
#     limit=1,
#     poll_interval=30,
# )
# print(response)
