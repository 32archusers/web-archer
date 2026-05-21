# Web Archer v1.0.0

An open-source, highly efficient command-line toolset built for Arch Linux. It automates web discovery and extracts clean, plain-text datasets for LLMs and AI training. 

Version 1.0 features **anti-bot bypassing** via browser TLS fingerprinting, **CLI arguments**, and a recursive **deep-scraping crawler**.

---

##  Installation

### Local Installation
To install and register the utilities globally on your Arch machine:

1. Install the core system dependencies:
   ```bash
   sudo pacman -S python-setuptools python-pip
   ```
2. Navigate to your project root folder and compile:
   ```bash
   pip install . --break-system-packages
   ```

---

##  How to Use

Web Archer splits operations into two distinct tools: `web-scout` (to discover websites) and `web-archer` (to extract text content).

### Step 1: Discover Websites Using `web-scout`
Run the scouting tool to search for target links based on your keywords. It automatically filters out e-commerce junk, login walls, ad shops, and massive wiki platforms.

* **Interactive Mode (Asks you questions):**
  ```bash
  web-scout
  ```
* **Fast CLI Mode (No prompts):**
  ```bash
  web-scout --query "Arch Linux server guide" --limit 25
  ```
* **Output:** Clean links are automatically appended to a file called `web-list.txt` in your current directory.

### Step 2: Extract Plain Text Using `web-archer`
Run the scraper to load your list into the local database queue and extract clean textual content. The engine automatically impersonates Google Chrome on Linux to bypass basic Cloudflare or browser-verification walls.

* **Standard Mode (5 parallel threads):**
  ```bash
  web-archer
  ```
* **High-Speed Mode (Run 15 threads simultaneously):**
  ```bash
  web-archer --threads 15
  ```
* **Deep Crawl Mode (Scrapes your list PLUS any internal links found inside those websites):**
  ```bash
  web-archer --threads 10 --deep
  ```
* **Output:** All raw, clean text files (stripped of HTML tags, scripts, CSS, and navigation menus) are dumped inside the `scraped_text/` directory.

---

##  Database State Tracking

Web Archer uses an internal SQLite database core running in WAL mode to support parallel, cross-thread writes. It tracks completed items so the tool will **never scrape the same URL twice**, even if you run the script multiple times.

To check your scraping queue progress from your terminal, use the native `sqlite3` CLI:

```bash
# View all websites successfully completed
sqlite3 scraper_queue.db "SELECT url FROM web_queue WHERE status = 'done';"

# View websites still remaining in your queue
sqlite3 scraper_queue.db "SELECT url FROM web_queue WHERE status = 'pending';"
```

---

##  License
This project is open-source and available under the terms of the [MIT License](LICENSE).
