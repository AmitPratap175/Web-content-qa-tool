"""
Author: Amit Pratap
5-crawl_recursive_internal_links.py
----------------------------------
Recursively crawls a site starting from a root URL, using Crawl4AI's arun_many and a memory-adaptive dispatcher.
At each depth, all internal links are discovered and crawled in parallel, up to a specified depth, with deduplication.
Usage: Set the start URL and max_depth in main(), then run as a script.
"""

import asyncio
import os
import hashlib
import regex as re
from urllib.parse import urldefrag
from crawl4ai import (
    AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode,
    MemoryAdaptiveDispatcher
)
from app.config import CONFIG
import re
from urllib.parse import urlparse
import hashlib

def url_to_filename(url: str, default="page", ext=".md") -> str:
    parsed = urlparse(url)
    path = parsed.path.strip("/")

    # Use last part of path, or domain if path is empty
    if path:
        base = path.split("/")[-1]
    else:
        base = parsed.netloc.replace(".", "_")

    # Replace non-word characters with underscores
    base = re.sub(r"\W+", "_", base).strip("_")

    # Fallback to hash if empty
    if not base:
        base = hashlib.md5(url.encode()).hexdigest()

    return f"{base}{ext}"

async def crawl_recursive_batch(start_urls, max_depth=3, max_concurrent=10):
    browser_config = BrowserConfig(headless=True, verbose=False)
    run_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        stream=False
    )
    dispatcher = MemoryAdaptiveDispatcher(
        memory_threshold_percent=70.0,      # Don't exceed 70% memory usage
        check_interval=1.0,                 # Check memory every second
        max_session_permit=max_concurrent   # Max parallel browser sessions
    )

    # Track visited URLs to prevent revisiting and infinite loops (ignoring fragments)
    visited = set()
    
    def normalize_url(url):
        return urldefrag(url)[0]  # Remove fragment (part after #)

    current_urls = set([normalize_url(u) for u in start_urls])

    # Create output directory if it doesn't exist
    os.makedirs(CONFIG.SCRAPED_DIR, exist_ok=True)

    async with AsyncWebCrawler(config=browser_config) as crawler:
        for depth in range(max_depth):
            print(f"\n=== Crawling Depth {depth+1} ===")
            urls_to_crawl = [normalize_url(url) for url in current_urls if normalize_url(url) not in visited]
            # print("\n\n\nURLS: \n\n\n\n\n", urls_to_crawl)

            if not urls_to_crawl:
                break

            # Batch-crawl all URLs at this depth in parallel
            results = await crawler.arun_many(
                urls=urls_to_crawl,
                config=run_config,
                dispatcher=dispatcher
            )

            next_level_urls = set()

            for result in results:
                norm_url = normalize_url(result.url)
                visited.add(norm_url)

                print(f"Result: {result.url}")

                if result.success:
                    # print(f"[OK] {result.url} | Markdown: {len(result.markdown) if result.markdown else 0} chars")
                    markdown = result.markdown or ""

                    # Save markdown to file
                    safe_filename = url_to_filename(result.url)  #hashlib.md5(norm_url.encode()).hexdigest() + ".md"
                    file_path = os.path.join(CONFIG.SCRAPED_DIR, safe_filename)
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(markdown)
                    # print(f"Saved markdown to {file_path}")

                    # Split by headers (#, ##)
                    header_pattern = re.compile(r'^(# .+|## .+)$', re.MULTILINE)
                    headers = [m.start() for m in header_pattern.finditer(markdown)] + [len(markdown)]
                    chunks = []
                    for i in range(len(headers)-1):
                        chunk = markdown[headers[i]:headers[i+1]].strip()
                        if chunk:
                            chunks.append(chunk)
                    # print(f"Split into {len(chunks)} chunks:")
                    # for idx, chunk in enumerate(chunks):
                        # print(f"\n--- Chunk {idx+1} ---\n{chunk}\n")

                    # Collect new internal links
                    for link in result.links.get("internal", []):
                        next_url = normalize_url(link["href"])
                        if next_url not in visited:
                            next_level_urls.add(next_url)
                else:
                    print(f"[ERROR] {result.url}: {result.error_message}")
                    

            current_urls = next_level_urls

# if __name__ == "__main__":
#     asyncio.run(crawl_recursive_batch(["https://driveyourway.nl/"], max_depth=2, max_concurrent=10))
#     #https://langchain-ai.github.io/langgraph/tutorials/rag/langgraph_adaptive_rag/"], max_depth=2, max_concurrent=10))
