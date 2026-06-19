import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import re


async def search_meesho_async(query: str, headless: bool = True, scroll_count: int = 3) -> list:
    """Scrape Meesho using Playwright for async browser rendering"""
    search_url = f"https://www.meesho.com/search?q={query.replace(' ', '%20')}"
    products = []

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=headless,
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

            # Add stealth scripts
            await page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en']
                });
            """)

            try:
                print(f"Loading Meesho: {search_url}")
                await page.goto(search_url, wait_until='load', timeout=30000)
                print("[OK] Page loaded")

                await page.wait_for_timeout(3000)  # Wait for JS rendering

                # Scroll to load lazy-loaded products
                for i in range(scroll_count):
                    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    await page.wait_for_timeout(1500)
                    print(f"[OK] Scroll {i+1}/{scroll_count} complete")

                # Get page content
                html = await page.content()
                soup = BeautifulSoup(html, 'html.parser')
                products = _parse_meesho_products(soup)
                print(f"[OK] Found {len(products)} products")

            finally:
                await context.close()
                await browser.close()

    except Exception as e:
        print(f"[ERROR] Error scraping Meesho: {e}")

    return products


def search_meesho(query: str, headless: bool = True, scroll_count: int = 3) -> list:
    """Synchronous wrapper for Meesho scraper"""
    try:
        return asyncio.run(search_meesho_async(query, headless, scroll_count))
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(search_meesho_async(query, headless, scroll_count))
        finally:
            loop.close()


def _parse_meesho_products(soup: BeautifulSoup) -> list:
    """Parse products from BeautifulSoup object"""
    products = []

    # Try multiple selector patterns
    selectors = [
        'a[href*="/p/"]',  # Product links pattern
        'a[href*="product"]',
        'div[data-testid*="product"] a',
        'div.sc-product a'
    ]

    product_links = []
    for selector in selectors:
        links = soup.select(selector)
        if links:
            product_links = links
            print(f"Found {len(links)} products with selector: {selector}")
            break

    if not product_links:
        print("No products found with any selector")
        return []

    for idx, link in enumerate(product_links[:40]):
        try:
            product = {}

            href = link.get('href', '')
            if href:
                product['product_link'] = f"https://www.meesho.com{href}" if href.startswith('/') else href

            text_content = link.get_text(strip=True, separator='\n')
            lines = [l.strip() for l in text_content.split('\n') if l.strip()]

            # Extract title
            for line in lines:
                if len(line) > 10 and '₹' not in line and '%' not in line and 'Reviews' not in line:
                    product['title'] = line
                    break

            # Extract price
            for line in lines:
                if '₹' in line:
                    price_match = re.search(r'₹\s*[\d,]+', line)
                    if price_match:
                        product['price'] = price_match.group(0).strip()
                        break

            # Extract image
            img = link.select_one('img')
            if img:
                product['image_url'] = img.get('src', '') or img.get('data-src', '')

            # Extract rating
            rating_text = ' '.join(lines)
            rating_match = re.search(r'(\d+\.?\d*)\s*\d+\s*Reviews', rating_text)
            if rating_match:
                product['rating'] = rating_match.group(1)

            # Extract reviews count
            reviews_match = re.search(r'(\d+)\s*Reviews', rating_text)
            if reviews_match:
                product['reviews_count'] = reviews_match.group(1)

            # Check for COD
            if 'COD' in text_content.upper():
                product['cod_available'] = 'Yes'

            # Extract discount
            discount_match = re.search(r'(\d+)%\s*off', text_content, re.IGNORECASE)
            if discount_match:
                product['discount'] = f"{discount_match.group(1)}%"

            # Only add if we have title and price
            if product.get('title') and product.get('price'):
                products.append(product)

        except Exception as e:
            continue

    return products


if __name__ == "__main__":
    import sys
    import io

    # Fix Windows console encoding
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    print("Testing Meesho Scraper with Playwright...")
    products = search_meesho("women kurta", headless=False, scroll_count=2)

    print(f"\n{'='*60}")
    print(f"RESULTS: {len(products)} products found")
    print(f"{'='*60}")

    for i, p in enumerate(products[:5], 1):
        print(f"\n{i}. {p.get('title', 'N/A')[:50]}")
        print(f"   Price: {p.get('price', 'N/A')}")
