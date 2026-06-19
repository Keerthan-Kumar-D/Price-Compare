#!/usr/bin/env python3
"""Debug Meesho HTML structure"""

import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

async def debug_meesho():
    """Debug Meesho HTML structure"""
    search_url = "https://www.meesho.com/search?q=women%20kurta"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-dev-shm-usage'
            ]
        )
        
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            extra_http_headers={
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Referer': 'https://www.meesho.com/',
                'DNT': '1'
            }
        )
        
        page = await context.new_page()
        
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
        """)
        
        print("Loading page...")
        await page.goto(search_url, wait_until='load', timeout=30000)
        
        # Scroll to load products
        print("Scrolling...")
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await page.wait_for_timeout(2000)
        
        html = await page.content()
        soup = BeautifulSoup(html, 'html.parser')
        
        # Try different selectors
        selectors = [
            'a[href*="/p/"]',
            'a[href*="product"]',
            'div[class*="product"]',
            '[data-testid*="product"]',
            'article',
            'li',
            'div.col'
        ]
        
        print("\n" + "="*60)
        print("Selector Results:")
        print("="*60)
        
        for sel in selectors:
            count = len(soup.select(sel))
            print(f"{sel}: {count} items")
        
        # Try to find any links
        all_links = soup.select('a')
        print(f"\nTotal links: {len(all_links)}")
        
        # Show some links
        print("\nFirst 10 links:")
        for i, link in enumerate(all_links[:10], 1):
            href = link.get('href', '')
            text = link.get_text(strip=True)[:50]
            print(f"{i}. href={href[:60]}... text={text}...")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_meesho())
