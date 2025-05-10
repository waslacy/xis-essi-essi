import asyncio
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
import aiohttp

semaphore = asyncio.Semaphore(20)

def inject_payload(url, payload):
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query, keep_blank_values=True)
    
    injected_params = {k: [payload] for k in query_params}
    
    new_query = urlencode(injected_params, doseq=True)
    injected_url = parsed_url._replace(query=new_query)
    
    return urlunparse(injected_url)
    
async def test_url(session, url, payload):
    async with semaphore:
        test_url = inject_payload(url, payload)
        
        try:
            async with session.get(test_url, timeout=10) as resp:
                text = await resp.text()
                
                if payload in text:
                    print(f"[!] POSSIBLE XSS: {test_url} [!]")
                    return test_url
                
        except Exception as e:
            print(f"[!] Error testing {url} using payload {payload}: {e}")
            
    return False
    
    
async def injector(urls, payloads, delay, headers):
    vulnerable_urls = []
    
    async with aiohttp.ClientSession(headers=headers) as session:
        tasks = []
        
        for url in urls:
            for payload in payloads:
                tasks.append(test_url(session, url, payload))
                
        results = await asyncio.gather(*tasks, return_exceptions=True)
    
    for result in results:
        if result:
            vulnerable_urls.append(result)
            
    return results
