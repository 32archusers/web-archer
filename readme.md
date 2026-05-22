#### Disclaimer:
This tool is developed and provided strictly for **educational**, research, and personal data-collection purposes (such as assembling custom datasets for local AI/LLM training).
​When utilizing Web Archer, *you* are solely responsible for ensuring that your scraping and crawling activities comply
 **With:**

​The Terms of Service (ToS) of any target websites.
​The rules specified in the host's robots.txt file.
​Applicable local and international data privacy and security laws (including, but not limited to, GDPR and CCPA regarding personal data collection).
​The developer assumes no liability and is not responsible for any misuse, potential IP bans, *rate-limiting* or **legal consequences** resulting from the execution of this software. Use responsibly and ethically.


## Version 1.4
 1.4 is a major stability and reliability release for the Web Archer ecosystem. This update transitions both **web__scout** and **web__archer** from experimental scripts into a robust, production-ready, fault-tolerant dataset pipeline. The focus of this release was completely eliminating database locks, handling edge-case network failures gracefully, and fixing broken project entry points.

## Web Archer v1.4

An open-source, highly efficient command-line toolset built for Arch Linux. It automates web discovery and extracts clean, plain-text datasets for LLMs and AI training. 
A bug-fixed, multi-threaded text scraper and website crawling tool.
Version 1.2.1 features **anti-bot bypassing** via browser TLS fingerprinting, custom **CLI arguments**, and a recursive **deep-scraping crawler**.

---

##  Installation
Install via aur with
"yay -S web-archer-bin"
## If not installing with yay then global install
### Global Installation (Bypassing Virtual Environments)
To register the tools globally on your Arch machine so you can run them from any directory:

1. Install the base core package dependencies:
   ```bash
   sudo pacman -S python-setuptools python-pip python-beautifulsoup4 python-requests python-sqlite
   ```
2. Download the required advanced search and browser-impersonation dependencies [curl_cffi]:
   ```bash
   pip install curl_cffi ddgs --break-system-packages
   ```
3. Navigate to your root project folder and compile:
   ```bash
   pip install . --break-system-packages --upgrade
   ```
4. Ensure your Bash path configuration is updated. If you encounter a "command not found" error, append the following line to the bottom of your `~/.bashrc` file and run `source ~/.bashrc`:
   ```bash
   export PATH="\(HOME/.local/bin:\)PATH"
   ```

---

##  How to Use

Web Archer splits operations into two distinct tools: `web-scout` (to discover websites) and `web-archer` (to extract text content). Both tools dynamically generate their data results inside whatever folder you are currently standing in.

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
* **Output:** Clean links are automatically appended to a file called `web-list.txt`.

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
* **Output:** All raw, clean text files (stripped of HTML tags, scripts, CSS, and navigation menus) are dumped inside a `scraped_text/` directory.

---

##  Database State Tracking

Web Archer uses an internal SQLite database core running in WAL mode to support parallel, cross-thread writes. It tracks completed items so the tool will **never scrape the same URL twice**, even if you run the script multiple times or add identical links to your list.

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
