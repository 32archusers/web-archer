import os
import sqlite3
import argparse
from urllib.parse import urlparse
from duckduckgo_search import DDGS

URL_FILE = "web-list.txt"
DB_NAME = "scraper_queue.db"

DOMAIN_BLACKLIST = {"amazon.com", "facebook.com", "instagram.com", "pinterest.com", "twitter.com", "youtube.com"}
TITLE_BLACKLIST = ["cart", "checkout", "login", "product", "shop", "sign up", "signin", "store"]

def get_already_known_urls():
    known = set()
    if os.path.exists(DB_NAME):
        try:
            conn = sqlite3.connect(DB_NAME, timeout=30.0)
            cursor = conn.cursor()
            cursor.execute("SELECT url FROM web_queue")
            for row in cursor.fetchall():
                known.add(row[0])
            conn.close()
        except Exception:
            pass
    return known

def scout_websites():
    parser = argparse.ArgumentParser(description="Web Archer Scout: Automated URL Hunter")
    parser.add_argument("-q", "--query", type=str, help="Search terms/keywords inside quotation marks")
    parser.add_argument("-l", "--limit", type=int, default=10, help="Maximum links to extract (Max 50)")
    args = parser.parse_args()

    query = args.query if args.query else input("Enter search keywords: ").strip()

    if args.query:
        limit = min(args.limit, 50)
    else:
        try:
            limit = int(input("How many website links do you want to find? (Max 50): "))
            limit = min(limit, 50)
        except ValueError:
            limit = 10

    if not query:
        print("Error: Search query cannot be empty.")
        return

    print(f"\nSearching DuckDuckGo for: '{query}' (Limit: {limit})...")
    existing_urls = get_already_known_urls()

    if os.path.exists(URL_FILE):
        with open(URL_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    existing_urls.add(line)

    new_urls = []

    # Instantiate the search object cleanly outside a context manager
    with ddgs = DDGS()
    try:
        # Pull list payload using explicit keyword syntax required by modern versions
        results = [r for r in ddgs.text(keywords=query, max_results=limit)]
        if results:
            for r in results:
                url = r.get('href')
                title = r.get('title', '').lower()

                if url:
                    domain = urlparse(url).netloc.lower().replace("www.", "")
                    if domain in DOMAIN_BLACKLIST or any(kw in title for kw in TITLE_BLACKLIST):
                        continue
                    if url not in existing_urls:
                        new_urls.append(url)
    except Exception as e:
        print(f" Error linking to search engine: {e}")
        return

    if not new_urls:
        print(" No new unique websites found after applying filters.")
        return

    with open(URL_FILE, "a", encoding="utf-8") as f:
        if os.path.getsize(URL_FILE) == 0 if os.path.exists(URL_FILE) else True:
            f.write("# Paste your URLs here, one per line\n")
        for url in new_urls:
            print(f" -> Adding: {url}")
            f.write(f"{url}\n")
    print(f" Appended {len(new_urls)} clean links to '{URL_FILE}'!")

if __name__ == "__main__":
    scout_websites()
