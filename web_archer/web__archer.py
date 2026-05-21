import os
import sys
import time
import sqlite3
import argparse
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from curl_cffi import requests

DB_NAME = "scraper_queue.db"
OUTPUT_DIR = "scraped_text"
URL_FILE = "web-list.txt"

def init_db():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_NAME, timeout=30.0)
    cursor = conn.cursor()
    cursor.execute("PRAGMA journal_mode=WAL;")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS web_queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE,
            status TEXT DEFAULT 'pending'
        )
    ''')

    if os.path.exists(URL_FILE):
        target_urls = []
        with open(URL_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    target_urls.append(line)
        for url in target_urls:
            try:
                cursor.execute("INSERT OR IGNORE INTO web_queue (url) VALUES (?)", (url,))
            except sqlite3.Error:
                pass
        conn.commit()
    conn.close()

def get_all_pending():
    conn = sqlite3.connect(DB_NAME, timeout=30.0)
    cursor = conn.cursor()
    cursor.execute("SELECT id, url FROM web_queue WHERE status = 'pending'")
    rows = cursor.fetchall()
    conn.close()
    return rows

def mark_as_done(url_id):
    conn = sqlite3.connect(DB_NAME, timeout=30.0)
    cursor = conn.cursor()
    cursor.execute("UPDATE web_queue SET status = 'done' WHERE id = ?", (url_id,))
    conn.commit()
    conn.close()

def add_discovered_url(url):
    conn = sqlite3.connect(DB_NAME, timeout=30.0)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT OR IGNORE INTO web_queue (url) VALUES (?)", (url,))
        conn.commit()
    except sqlite3.Error:
        pass
    finally:
        conn.close()

def scrape_worker(site_data, crawl_deep):
    url_id, url = site_data
    try:
        print(f"[START] Scraping: {url}")
        response = requests.get(url, impersonate="chrome", timeout=15)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            if crawl_deep:
                base_domain = urlparse(url).netloc
                for link in soup.find_all('a', href=True):
                    href = link.get('href')
                    full_url = urljoin(url, href)
                    if urlparse(full_url).netloc == base_domain:
                        add_discovered_url(full_url)

            for element in soup(["script", "style", "nav", "footer"]):
                element.extract()

            clean_text = soup.get_text(separator='\n', strip=True)
            filename = f"{OUTPUT_DIR}/site_{url_id}.txt"

            with open(filename, "w", encoding="utf-8") as f:
                f.write(clean_text)

            mark_as_done(url_id)
            print(f"[SUCCESS] Saved to {filename}")
        else:
            print(f"[FAIL] HTTP Status {response.status_code} on {url}")
    except Exception as e:
        print(f"[ERROR] Failure on target {url}: {e}")

def run_task(args_and_task):
    task, crawl_deep = args_and_task
    return scrape_worker(task, crawl_deep)

def main():
    parser = argparse.ArgumentParser(description="Web Archer: Multi-Threaded Scraper & Crawler")
    parser.add_argument("-t", "--threads", type=int, default=5, help="Number of concurrent execution threads")
    parser.add_argument("-d", "--deep", action="store_true", help="Enable Deep Crawling of internal links")
    args = parser.parse_args()

    print("\n --- INITIALIZING WEB ARCHER: PARALLEL TEXT SCRAPER v1.4 --- ")
    print("Loading database, checking configuration files, and initializing threads...")
    time.sleep(2)

    init_db()
    pending_tasks = get_all_pending()
    if not pending_tasks:
        print(" No pending items remaining in the tracking database queue.")
        return

    print(f" Processing {len(pending_tasks)} URLs using {args.threads} parallel workers (Deep-Crawl: {args.deep})...")
    bundled_tasks = [(task, args.deep) for task in pending_tasks]

    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        executor.map(run_task, bundled_tasks)

    print(" Scraping batch execution complete!")

if __name__ == "__main__":
    main()
