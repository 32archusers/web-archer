import os
import sys
import time
import sqlite3
import argparse
import threading
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from curl_cffi import requests

DB_NAME = "scraper_queue.db"
OUTPUT_DIR = "scraped_text"
URL_FILE = "web-list.txt"

# Threading Lock to prevent concurrent write collisions on SQLite
db_lock = threading.Lock()

def init_db(reset_db=False):
    """Initializes the database and populates it with links from the source text file."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    with db_lock:
        if reset_db and os.path.exists(DB_NAME):
            try:
                # Clear main database file and any related engine logs
                for ext in ["", "-wal", "-shm"]:
                    if os.path.exists(DB_NAME + ext):
                        os.remove(DB_NAME + ext)
                print("[RESET] Database cache completely cleared.")
            except OSError as e:
                print(f"[RESET ERROR] Failed to remove old database: {e}")

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

