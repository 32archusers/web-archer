import argparse
import sqlite3
from pathlib import Path
from urllib.parse import urlparse

try:
    from duckduckgo_search import DDGS
except ImportError:
    print("[ERROR] duckduckgo_search not installed. Install with: pip install duckduckgo-search")
    exit(1)

URL_FILE = Path("web-list.txt")
DB_NAME = Path("scraper_queue.db")

MAX_LIMIT = 50
DEFAULT_LIMIT = 10

DOMAIN_BLACKLIST = {
    "wikipedia.org",
    "ebay.com",
    "amazon.com",
    "facebook.com",
    "instagram.com",
    "twitter.com",
    "reddit.com",
}

TITLE_BLACKLIST = {
    "login",
    "sign up",
    "subscribe",
    "buy now",
    "cart",
    "checkout",
    "price",
}


def normalize_url(url: str) -> str:
    parsed = urlparse(url.strip())

    scheme = parsed.scheme.lower() or "https"
    netloc = parsed.netloc.lower().replace("www.", "")
    path = parsed.path.rstrip("/")

    return f"{scheme}://{netloc}{path}"


def get_domain(url: str) -> str:
    return urlparse(url).netloc.lower().replace("www.", "")


def load_existing_urls() -> set[str]:
    known_urls = set()

    if DB_NAME.exists():
        try:
            with sqlite3.connect(DB_NAME, timeout=30) as conn:
                cursor = conn.cursor()

                cursor.execute("""
                    SELECT name FROM sqlite_master
                    WHERE type='table' AND name='web_queue'
                """)

                if cursor.fetchone():
                    cursor.execute("SELECT url FROM web_queue")

                    known_urls.update(
                        normalize_url(row[0])
                        for row in cursor.fetchall()
                        if row[0]
                    )

        except sqlite3.Error as e:
            print(f"[DB WARNING] {e}")

    if URL_FILE.exists():
        try:
            with URL_FILE.open("r", encoding="utf-8") as f:
                known_urls.update(
                    normalize_url(line.strip())
                    for line in f
                    if line.strip() and not line.startswith("#")
                )
        except OSError as e:
            print(f"[FILE WARNING] {e}")

    return known_urls


def is_blacklisted(url: str, title: str) -> bool:
    domain = get_domain(url)

    if domain in DOMAIN_BLACKLIST:
        return True

    title = title.lower()

    return any(keyword in title for keyword in TITLE_BLACKLIST)


def search_duckduckgo(query: str, limit: int) -> list[str]:
    existing_urls = load_existing_urls()
    new_urls = []

    try:
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=limit)

            for result in results:
                url = result.get("href")
                title = result.get("title", "")

                if not url:
                    continue

                normalized = normalize_url(url)

                if is_blacklisted(normalized, title):
                    continue

                if normalized in existing_urls:
                    continue

                existing_urls.add(normalized)
                new_urls.append(normalized)

    except Exception as e:
        print(f"[SEARCH ERROR] {e}")

    return new_urls


def save_urls(urls: list[str]) -> None:
    if not urls:
        print("No new unique websites found.")
        return

    file_empty = not URL_FILE.exists() or URL_FILE.stat().st_size == 0

    try:
        with URL_FILE.open("a", encoding="utf-8") as f:

            if file_empty:
                f.write("# Paste your URLs here, one per line\n")

            for url in urls:
                print(f"-> Adding: {url}")
                f.write(f"{url}\n")

        print(f"\nSaved {len(urls)} URLs to '{URL_FILE}'")

    except OSError as e:
        print(f"[FILE ERROR] {e}")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Web Archer Scout - Automated URL Hunter"
    )

    parser.add_argument(
        "-q",
        "--query",
        type=str,
        help="Search query",
    )

    parser.add_argument(
        "-l",
        "--limit",
        type=int,
        default=DEFAULT_LIMIT,
        help=f"Maximum links to extract (1-{MAX_LIMIT})",
    )

    return parser.parse_args()


def get_user_input(args):
    query = args.query or input("Enter search keywords: ").strip()

    if not query:
        raise ValueError("Search query cannot be empty.")

    limit = max(1, min(args.limit, MAX_LIMIT))

    return query, limit


def main():
    args = parse_args()

    try:
        query, limit = get_user_input(args)

        print(f"\nSearching DuckDuckGo for: '{query}' (Limit: {limit})...\n")

        urls = search_duckduckgo(query, limit)

        save_urls(urls)

    except KeyboardInterrupt:
        print("\nInterrupted by user.")

    except Exception as e:
        print(f"[ERROR] {e}")


if __name__ == "__main__":
    main()
