"""
Myntra Playwright Scraper Module
Extracts product data from Myntra using Playwright browser automation
"""

import asyncio
import re
import logging
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


async def scrape_myntra_playwright_async(search_query: str, max_products: int = 12, headless: bool = True) -> list:
    """
    Scrape Myntra products using Playwright

    Args:
        search_query (str): Search query for products
        max_products (int): Maximum number of products to return
        headless (bool): Run in headless mode

    Returns:
        list: List of product dictionaries
    """
    search_url = f"https://www.myntra.com/{search_query.replace(' ', '-')}"
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
                    'Referer': 'https://www.myntra.com/',
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
                logger.info(f"Loading Myntra page: {search_url}")
                await page.goto(search_url, wait_until='load', timeout=30000)
                await page.wait_for_timeout(1500)

                # Scroll to load products
                logger.info("Scrolling to load products...")
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await page.wait_for_timeout(800)

                # Get page content
                html = await page.content()
                soup = BeautifulSoup(html, 'html.parser')
                products = _parse_myntra_products(soup, max_products)
                logger.info(f"Successfully scraped {len(products)} products from Myntra")

            finally:
                await context.close()
                await browser.close()

    except Exception as e:
        logger.error(f"Error during Myntra scraping: {e}")

    return products


def scrape_myntra_playwright(search_query: str, max_products: int = 12, headless: bool = True) -> list:
    """Synchronous wrapper for Myntra scraper"""
    try:
        return asyncio.run(scrape_myntra_playwright_async(search_query, max_products, headless))
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(scrape_myntra_playwright_async(search_query, max_products, headless))
        finally:
            loop.close()


def _parse_myntra_products(soup: BeautifulSoup, max_products: int = 12) -> list:
    """Parse products from BeautifulSoup object"""
    products = []

    # Find product elements
    product_items = soup.select('li.product-base')
    logger.info(f"Found {len(product_items)} product elements")

    for idx, product in enumerate(product_items[:max_products], 1):
        try:
            # Extract brand
            brand = "N/A"
            try:
                brand_elem = product.select_one(".product-brand")
                if brand_elem:
                    brand = brand_elem.get_text(strip=True)
            except:
                pass

            # Extract title
            title = "N/A"
            try:
                title_elem = product.select_one(".product-product")
                if title_elem:
                    title = title_elem.get_text(strip=True)
            except:
                pass

            # Extract price (discounted price)
            price = "N/A"
            try:
                price_elem = product.select_one(".product-discountedPrice")
                if price_elem:
                    price_text = price_elem.get_text(strip=True)
                    price_text = price_text.replace('Rs', '').replace('rs', '').replace('.', '').strip()
                    price_text = price_text.replace(' ', '')
                    price = f"₹{price_text}"
            except:
                pass

            # Extract original price
            original_price = None
            try:
                orig_elem = product.select_one(".product-strike")
                if orig_elem:
                    orig_text = orig_elem.get_text(strip=True)
                    orig_text = orig_text.replace('Rs', '').replace('rs', '').replace('.', '').strip()
                    orig_text = orig_text.replace(' ', '')
                    original_price = f"₹{orig_text}"
            except:
                pass

            # Extract discount
            discount = None
            try:
                discount_elem = product.select_one(".product-discountPercentage")
                if discount_elem:
                    discount = discount_elem.get_text(strip=True)
            except:
                pass

            # Extract rating
            rating = None
            try:
                rating_elem = product.select_one(".product-ratingsContainer span")
                if rating_elem:
                    rating = rating_elem.get_text(strip=True)
            except:
                pass

            # Extract reviews count
            reviews_count = None
            try:
                reviews_elem = product.select_one(".product-ratingsCount")
                if reviews_elem:
                    reviews_count = reviews_elem.get_text(strip=True)
            except:
                pass

            # Extract image URL
            image_url = None
            try:
                img_elem = product.select_one("img.img-responsive")
                if img_elem:
                    image_url = img_elem.get_attribute("src") or img_elem.get_attribute("data-src")
                    if not image_url or image_url == "N/A":
                        image_url = None
            except:
                pass

            # Extract product link
            product_link = None
            try:
                link_elem = product.select_one("a")
                if link_elem:
                    product_link = link_elem.get_attribute("href")
            except:
                pass

            # Only add product if it has minimum required data
            if title != "N/A" and price != "N/A" and product_link:
                product_data = {
                    'brand': brand if brand != "N/A" else None,
                    'title': title,
                    'price': price,
                    'original_price': original_price,
                    'discount': discount,
                    'rating': rating,
                    'reviews_count': reviews_count,
                    'image_url': image_url,
                    'product_link': product_link
                }

                products.append(product_data)
                logger.info(f"Extracted product {idx}: {brand} - {title[:30]}...")

        except Exception as e:
            logger.warning(f"Error extracting product {idx}: {e}")
            continue

    return products


def search_myntra_product(search_query: str) -> str:
    """Generate Myntra search URL from query"""
    return f"https://www.myntra.com/{search_query.replace(' ', '-')}"


# For backward compatibility
scrape_myntra = scrape_myntra_playwright


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("Testing Myntra Scraper with Playwright...")
    products = scrape_myntra_playwright("mens-tshirts", headless=False)

    print(f"\nFound {len(products)} products:")
    for i, p in enumerate(products[:5], 1):
        print(f"\n{i}. {p.get('brand', 'N/A')} - {p.get('title', 'N/A')}")
        print(f"   Price: {p.get('price', 'N/A')}")
        if p.get('original_price'):
            print(f"   Original: {p.get('original_price')}")
        if p.get('discount'):
            print(f"   Discount: {p.get('discount')}")
        print(f"   Rating: {p.get('rating', 'N/A')}")
