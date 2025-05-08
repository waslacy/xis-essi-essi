import requests
from urllib.parse import urljoin, urlparse, urlunparse
from bs4 import BeautifulSoup
import time

base_domain = ""


def normalize_url(url):
    parsed = urlparse(url)
    path = parsed.path.rstrip('/') or '/'
    normalized = urlunparse(parsed._replace(path=path))
    return normalized


def is_valid_url(url):
    global base_domain
    parsed = urlparse(url)

    if parsed.scheme not in ("http", "https", ""):
        return False

    return parsed.netloc == base_domain or parsed.netloc == ''


def is_media_file(url):
    return url.lower().endswith((
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg',
        '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
        '.zip', '.rar', '.mp3', '.mp4', '.avi', '.mov', '.exe'
    ))


def get_links_from_html(html, base_url):
    soup = BeautifulSoup(html, "html.parser")
    links = set()

    for tag in soup.find_all("a", href=True):
        full_url = urljoin(base_url, tag["href"])
        normalized_url = normalize_url(full_url)

        if is_valid_url(normalized_url) and not is_media_file(normalized_url):
            links.add(normalized_url)

    return links

# ========== CRAWLER ==========
def crawl_site(start_url, max_depth, delay, headers=None):
    visited = set()
    to_visit = [(start_url, 0)]
    found_urls = set()

    global base_domain
    base_domain = urlparse(start_url).netloc
    print(f"base domain: {base_domain}")

    while to_visit:
        current_url, depth = to_visit.pop(0)
        normalized_current = normalize_url(current_url)

        if normalized_current in visited or depth > max_depth:
            continue

        visited.add(normalized_current)

        try:
            print(f"[+] Visitando: {current_url}")
            response = requests.get(current_url, headers=headers, timeout=10)

            if "text/html" not in response.headers.get("Content-Type", ""):
                continue

            links = get_links_from_html(response.text, current_url)
            for link in links:
                next_depth = depth + 1
                if (
                    link not in visited and
                    next_depth <= max_depth and
                    (link, next_depth) not in to_visit
                ):
                    to_visit.append((link, next_depth))

            time.sleep(delay)

        except Exception as e:
            print(f"[!] Erro ao acessar {current_url}: {e}")

        found_urls.add(normalized_current)

    # Retorna apenas URLs com parâmetros e sem comportamento suspeito
    return [url for url in found_urls if "?" in url and "=" in url]
