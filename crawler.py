import asyncio
from urllib.parse import urljoin, urlparse, urlunparse, parse_qs
from bs4 import BeautifulSoup
import aiohttp

visited = set()
found_urls = set()
base_domain = ""
semaphore = asyncio.Semaphore(10) 

def dedup_endpoints(urls):
    seen = set()
    unique_urls = []
    
    for url in urls:
        parsed = urlparse(url)
        param_keys = frozenset(parse_qs(parsed.query).keys())
        identifier = (parsed.path, param_keys)
        
        if param_keys and identifier not in seen:
            seen.add(identifier)
            unique_urls.append(url)
            
    return unique_urls

def normalize_domain(domain):
    return domain.lower().removeprefix("www.")

def normalize_url(url):
    parsed = urlparse(url)
    path = parsed.path.rstrip('/') or '/'
    return urlunparse(parsed._replace(path=path, fragment=''))

def is_valid_url(url):
    parsed = urlparse(url)
    
    if '#' in parsed.path:
        return False
    
    return (parsed.netloc == base_domain or parsed.netloc == '') and parsed.scheme in ("http", "https")

def is_media_file(url):
    return url.lower().endswith((
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg',
        '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
        '.zip', '.rar', '.mp3', '.mp4', '.avi', '.mov', '.exe'
    ))

def get_links_from_html(html, base_url):
    soup = BeautifulSoup(html, "lxml")
    links = set()
    
    for tag in soup.find_all("a", href=True):
        full_url = urljoin(base_url, tag["href"])
        norm_url = normalize_url(full_url)
        
        if is_valid_url(norm_url) and not is_media_file(norm_url):
            links.add(norm_url)
            
    return links

async def worker(queue, session, max_depth, delay):
    while True:
        try:
            url, depth = await queue.get()
            if url in visited or depth > max_depth:
                queue.task_done()
                continue

            async with semaphore:
                print(f"[+] Visiting: {url}")
                visited.add(url)

                try:
                    async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                        if resp.status != 200 or "text/html" not in resp.headers.get("Content-Type", ""):
                            queue.task_done()
                            continue
                        
                        html = await resp.text()
                        found_urls.add(url)
                        
                        if depth < max_depth:
                            links = get_links_from_html(html, url)
                            
                            for link in links:
                                if link not in visited:
                                    await queue.put((link, depth + 1))
                                    
                        await asyncio.sleep(delay)
                        
                except Exception as e:
                    print(f"[!] Error: {url} -> {e}")
                    
            queue.task_done()
            
        except asyncio.CancelledError:
            break

async def crawl(start_url, max_depth, delay, headers=None):
    global base_domain, visited, found_urls
    base_domain = normalize_domain(urlparse(start_url).netloc)

    visited.clear()
    found_urls.clear()

    queue = asyncio.Queue()
    await queue.put((start_url, 0))

    async with aiohttp.ClientSession(headers=headers) as session:
        workers = [asyncio.create_task(worker(queue, session, max_depth, delay)) for _ in range(10)]
        
        await queue.join()
        for w in workers:
            w.cancel()
            
        await asyncio.gather(*workers, return_exceptions=True)

    
    filtered_urls = [url for url in found_urls if "?" in url and "=" in url]
    return dedup_endpoints(filtered_urls)