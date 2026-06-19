import asyncio
import re
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup


async def search_flipkart_playwright_async(search_query: str, headless: bool = True) -> list:
    """Scrape Flipkart using Playwright to handle JavaScript-loaded content"""
    search_url = f"https://www.flipkart.com/search?q={search_query.replace(' ', '+')}"
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
                    'Accept-Language': 'en-IN,en;q=0.9',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Referer': 'https://www.flipkart.com/',
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
            """)

            try:
                print(f"Loading Flipkart: {search_url}")
                await page.goto(search_url, wait_until='load', timeout=30000)
                await page.wait_for_timeout(2000)

                # Scroll to load images
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await page.wait_for_timeout(1500)
                await page.evaluate("window.scrollTo(0, 0)")

                # Get page content
                html = await page.content()
                soup = BeautifulSoup(html, 'html.parser')
                products = _parse_flipkart_products(soup)
                print(f"[OK] Found {len(products)} products")

            finally:
                await context.close()
                await browser.close()

    except Exception as e:
        print(f"[ERROR] Error scraping Flipkart: {e}")

    return products


def search_flipkart_playwright(search_query: str, headless: bool = True) -> list:
    """Synchronous wrapper for Flipkart scraper"""
    try:
        return asyncio.run(search_flipkart_playwright_async(search_query, headless))
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(search_flipkart_playwright_async(search_query, headless))
        finally:
            loop.close()


def _parse_flipkart_products(soup: BeautifulSoup) -> list:
    """Parse products from BeautifulSoup object"""
    products = []
    seen_titles = set()

    # Find product anchors with multiple fallback selectors
    anchor_selectors = [
        'a._2rpwqI', 'a.IRpwTa', 'a.s1Q9rs', 'a._2fZ6oW', 'a._2UzuFa',
        'a._3dqZjq', 'a._2r_T1I', 'a._2kHMtA', 'a._1fQZEK', 'a.CGtC98'
    ]

    anchors = []
    for sel in anchor_selectors:
        anchors.extend(soup.select(sel))

    if not anchors:
        anchors = soup.select('div._1AtVbE a')

    price_selectors = ['div._30jeq3', 'span._30jeq3', 'div._4b5DiR', 'div.Nx9bqj', 'div._25b18c']
    rating_selectors = ['div._3LWZlK', 'span._3LWZlK', 'div.XQDdHH']

    for a in anchors:
        try:
            if not getattr(a, 'get', None):
                continue

            # Find container
            container = a
            for _ in range(4):
                if container.name in ['li', 'div'] and container.get('class'):
                    break
                if container.parent is None:
                    break
                container = container.parent

            # Extract title
            title = a.get('title') or ''
            if not title and container:
                title_anchors = container.find_all('a', title=True, recursive=True)
                for ta in title_anchors:
                    t = ta.get('title', '')
                    if t and '₹' not in t and '%' not in t and 'off' not in t.lower():
                        title = t
                        break

            if not title:
                img_el = a.select_one('img') or (container.select_one('img') if container else None)
                if img_el:
                    title = img_el.get('alt') or img_el.get('title') or ''

            if not title:
                title = a.get_text(separator=' ', strip=True)

            if not title or title in seen_titles:
                continue

            # Extract price
            price = None
            for ps in price_selectors:
                p_el = container.select_one(ps) if container else None
                if p_el and p_el.get_text(strip=True):
                    price = p_el.get_text(strip=True)
                    break

            if not price:
                txt = a.get_text(' ', strip=True)
                m = re.search(r'(₹\s*[\d,]+)', txt)
                if m:
                    price = m.group(1)

            if not price:
                continue

            # Extract image
            image_url = None
            imgs = a.find_all('img')
            for img in imgs:
                img_src = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
                if img_src and not img_src.startswith('data:image') and '/fk-p-flap/' not in img_src:
                    if not img_src.startswith('http'):
                        img_src = 'https:' + img_src if img_src.startswith('//') else 'https://rukminim2.flixcart.com' + img_src
                    image_url = img_src
                    break

            if not image_url and container:
                imgs = container.find_all('img')
                for img in imgs:
                    img_src = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
                    if img_src and not img_src.startswith('data:image') and '/fk-p-flap/' not in img_src:
                        if not img_src.startswith('http'):
                            img_src = 'https:' + img_src if img_src.startswith('//') else 'https://rukminim2.flixcart.com' + img_src
                        image_url = img_src
                        break

            # Extract rating
            rating = None
            for rs in rating_selectors:
                r_el = container.select_one(rs) if container else None
                if r_el:
                    rating_text = r_el.get_text(strip=True)
                    m = re.search(r"(\d+\.?\d*)", rating_text)
                    rating = m.group(1) if m else rating_text
                    break

            # Extract product link
            href = a.get('href')
            product_link = None
            if href:
                product_link = f"https://www.flipkart.com{href}" if href.startswith('/') else href

            # Clean title
            title = re.sub(r'Add to Compare', '', title, flags=re.IGNORECASE)
            title = re.sub(r'(₹\s*[\d,]+)', '', title)
            title = ' '.join(title.split())

            # Clean price
            if price:
                m = re.search(r'(₹\s*[\d,]+)', price)
                price = m.group(1) if m else price

            product_data = {
                'title': title,
                'price': price,
                'original_price': None,
                'discount': None,
                'rating': rating,
                'ratings_count': None,
                'reviews_count': None,
                'features': [],
                'image_url': image_url,
                'product_link': product_link,
                'exchange_offer': None,
                'delivery': None
            }

            seen_titles.add(title)
            products.append(product_data)

        except Exception:
            continue

    return products


if __name__ == "__main__":
    print("Testing Flipkart Scraper with Playwright...")
    products = search_flipkart_playwright('tshirt', headless=False)

    print(f"\nFound {len(products)} products:")
    for i, p in enumerate(products[:5], 1):
        print(f"\nProduct {i}:")
        print(f"Title: {p['title'][:60]}...")
        print(f"Price: {p['price']}")
        print(f"Has Image: {'Yes' if p['image_url'] else 'No'}")
