#!/usr/bin/env python3
"""Debug Myntra scraper - inspect HTML structure"""

import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def debug_myntra():
    """Debug Myntra HTML structure"""
    search_url = "https://www.myntra.com/mens-tshirts"
    
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
                'Accept-Language': 'en-IN,en;q=0.9',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Referer': 'https://www.myntra.com/',
                'DNT': '1'
            }
        )
        
        page = await context.new_page()
        
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
        
        print("Loading page...")
        try:
            await page.goto(search_url, wait_until='domcontentloaded', timeout=45000)
        except:
            print("Initial load timed out, retrying...")
            await page.reload(wait_until='domcontentloaded')
        
        await page.wait_for_timeout(3000)
        
        # Scroll to load products
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await page.wait_for_timeout(1000)
        
        html = await page.content()
        soup = BeautifulSoup(html, 'html.parser')
        
        # Find product containers
        products = soup.select('li.productCardImg')
        print(f"Found {len(products)} products with 'li.productCardImg'")
        
        if products:
            print("\n" + "="*60)
            print("First product HTML:")
            print("="*60)
            print(products[0].prettify()[:800])
        
        # Try other selectors
        print("\n" + "="*60)
        print("Trying other selectors:")
        print("="*60)
        
        selectors = [
            'li.productCardImg',
            'a[href*="/p/"]',
            'div[class*="product"]',
            'article',
            '.productCard',
            '[data-productid]'
        ]
        
        for sel in selectors:
            count = len(soup.select(sel))
            print(f"{sel}: {count} items")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_myntra())
