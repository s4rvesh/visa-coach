import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import hashlib
import json
import time

BASE_URL = "https://www.sjsu.edu/isss/index.php"
DOMAIN = "https://www.sjsu.edu"

visited = set()
pages_dir = "data-store/pages"
files_dir = "data-store/files"
os.makedirs(pages_dir, exist_ok=True)
os.makedirs(files_dir, exist_ok=True)

def sanitize_filename(url):
    hashed = hashlib.md5(url.encode()).hexdigest()
    return hashed + ".json"

def is_valid_internal_url(url):
    parsed = urlparse(url)
    return parsed.netloc in ["", "www.sjsu.edu"] and "/isss/" in parsed.path

def should_download_file(url):
    return any(url.lower().endswith(ext) for ext in ['.pdf', '.doc', '.docx'])

def save_page(url, title, text):
    filename = sanitize_filename(url)
    with open(os.path.join(pages_dir, filename), "w") as f:
        json.dump({
            "url": url,
            "title": title,
            "content": text
        }, f, indent=2)
    print(f"📄 Saved: {url}")

def download_file(url):
    local_filename = os.path.join(files_dir, os.path.basename(urlparse(url).path))
    try:
        r = requests.get(url, timeout=10)
        with open(local_filename, 'wb') as f:
            f.write(r.content)
        print(f"📥 Downloaded: {url}")
    except Exception as e:
        print(f"❌ Failed to download {url}: {e}")

def crawl(url):
    if url in visited:
        return
    visited.add(url)

    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.title.string.strip() if soup.title else "No Title"
        main = soup.find('main') or soup.find('body')
        text = main.get_text(separator="\n", strip=True) if main else ""

        save_page(url, title, text)

        for a_tag in soup.find_all("a", href=True):
            link = urljoin(url, a_tag['href'])
            if should_download_file(link):
                download_file(link)
            elif is_valid_internal_url(link):
                crawl(link)

        time.sleep(0.5)  # be polite

    except Exception as e:
        print(f"❌ Error crawling {url}: {e}")

if __name__ == "__main__":
    print("🔍 Starting crawl...")
    crawl(BASE_URL)
    print("✅ Crawl completed. Data saved to /data-store/")
