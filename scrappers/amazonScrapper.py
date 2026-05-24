from bs4 import BeautifulSoup
import requests
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Referer": "https://www.amazon.in/",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "Cache-Control": "max-age=0",
}


def search_amazon_product(search_query):
    search_url = f"https://www.amazon.in/s?k={search_query.replace(' ', '+')}"
    return search_url

def fetch_amazon_search_results(search_url):
    # Minimal delay to avoid an immediate burst
    time.sleep(random.uniform(0.1, 0.3))

    # User-Agent rotation to reduce chance of blocking
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0",
    ]

    session = requests.Session()

    max_retries = 3
    backoff = 1.0

    for attempt in range(1, max_retries + 1):
        try:
            # rotate User-Agent per attempt
            hdrs = headers.copy()
            hdrs['User-Agent'] = random.choice(user_agents)
            # Try a lightweight GET
            try:
                response = session.get(search_url, headers=hdrs, timeout=8)
            except requests.exceptions.RequestException as e:
                # network error - will be retried below
                response = None

            if response is not None and response.status_code == 200:
                return response.text

            # If Amazon returns 503 or other server error, retry with backoff
            if response is not None and response.status_code in (429, 503, 502, 504):
                print(f"Amazon returned {response.status_code} (attempt {attempt}/{max_retries}), retrying after {backoff}s")
                time.sleep(backoff)
                backoff *= 2
                continue

            # If response is None or non-retriable status, we'll let the outer except handle retries

        except requests.exceptions.RequestException as e:
            # Network-level errors (timeouts, connection errors)
            print(f"Amazon request error (attempt {attempt}/{max_retries}): {e}")
            if attempt < max_retries:
                time.sleep(backoff)
                backoff *= 2
                continue
            # After retries, break to attempt Selenium fallback
            break

    # If all retries fail, attempt Selenium fallback (often bypasses 503 blocks)
    print("Failed to fetch Amazon search results after retries; attempting Selenium fallback")
    try:
        print("Attempting Selenium fallback for Amazon...")
        chrome_options = Options()
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36')
        chrome_options.add_argument('--log-level=3')

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        try:
            driver.set_page_load_timeout(20)
            driver.get(search_url)
            time.sleep(2)
            html = driver.page_source or ''
            if html:
                print('Selenium fallback succeeded for Amazon')
                return html
        finally:
            try:
                driver.quit()
            except:
                pass
    except Exception as se:
        print(f"Selenium fallback failed: {se}")

    return ""


def parse_amazon_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    # Extract product information from the soup object
    products = []
    for item in soup.select('.s-result-item'):
        # Try multiple selectors for title
        title_element = (
            item.select_one('h2 a span') or 
            item.select_one('h2 span') or 
            item.select_one('[data-cy="title-recipe-title"] span') or
            item.select_one('h2 a') or
            item.select_one('.s-size-mini span') or
            item.select_one('.a-link-normal .a-text-normal')
        )
        
        # Try multiple selectors for price
        price_element = (
            item.select_one('.a-price .a-offscreen') or
            item.select_one('.a-price-whole') or
            item.select_one('.a-price-range')
        )
        
        # Extract image URL
        image_element = (
            item.select_one('img[data-src]') or
            item.select_one('img.s-image') or
            item.select_one('img[src]')
        )
        
        # Extract rating
        rating_element = (
            item.select_one('[aria-label*="out of 5 stars"]') or
            item.select_one('.a-icon-alt') or
            item.select_one('[data-cy="reviews-ratings-slot"] span')
        )
        
        # Extract number of reviews
        reviews_element = (
            item.select_one('[aria-label*="ratings"]') or
            item.select_one('a[href*="#customerReviews"] span') or
            item.select_one('.a-size-base')
        )
        
        # Extract product link
        link_element = (
            item.select_one('a[href*="/dp/"]') or  # Direct product links
            item.select_one('a[href*="/gp/product/"]') or  # Alternative product links
            item.select_one('h2 a[href]:not([href*="javascript"])') or  # Title links but not javascript
            item.select_one('.s-title-instructions-style a[href]:not([href*="javascript"])') or
            item.select_one('a[data-cy="title-recipe-title"]:not([href*="javascript"])') or
            item.select_one('.a-link-normal[href*="/dp/"]')
        )
        
        # Extract original price (if discounted)
        original_price_element = item.select_one('.a-text-price .a-offscreen')
        
        # Extract delivery info
        delivery_element = (
            item.select_one('[data-cy="delivery-recipe"] span') or
            item.select_one('.a-color-base.a-text-bold')
        )
        
        # Only add products that have at least a title
        if title_element:
            title = title_element.get_text(strip=True)
            
            # Extract price
            price = price_element.get_text(strip=True) if price_element else 'Price not available'
            
            # Extract image URL
            image_url = None
            if image_element:
                image_url = (
                    image_element.get('data-src') or 
                    image_element.get('src') or 
                    'Image not available'
                )
            
            # Extract rating
            rating = None
            if rating_element:
                rating_text = rating_element.get('aria-label') or rating_element.get_text(strip=True)
                if rating_text:
                    # Try to extract rating number from text like "4.5 out of 5 stars"
                    import re
                    rating_match = re.search(r'(\d+\.?\d*)\s*out of', rating_text)
                    rating = rating_match.group(1) if rating_match else rating_text
            
            # Extract number of reviews
            reviews_count = None
            if reviews_element:
                reviews_text = reviews_element.get_text(strip=True)
                # Try to extract number from text like "(1,234)" or "1,234 ratings"
                import re
                reviews_match = re.search(r'[\(\s]?(\d{1,3}(?:,\d{3})*)\s*(?:ratings?|reviews?)?[\)\s]?', reviews_text)
                reviews_count = reviews_match.group(1) if reviews_match else reviews_text
            
            # Extract product link
            product_link = None
            
            # First, try to find ASIN from the item
            asin = item.get('data-asin')
            
            # If no ASIN in data attribute, look for it in URLs
            if not asin:
                all_links = item.select('a[href]')
                for link in all_links:
                    href = link.get('href', '')
                    # Look for ASIN in various URL patterns
                    asin_match = re.search(r'/dp/([A-Z0-9]{10})', href)
                    if not asin_match:
                        asin_match = re.search(r'/gp/product/([A-Z0-9]{10})', href)
                    if not asin_match:
                        asin_match = re.search(r'asin=([A-Z0-9]{10})', href)
                    
                    if asin_match:
                        asin = asin_match.group(1)
                        break
            
            # If we have an ASIN, construct a clean product URL
            if asin and len(asin) == 10:
                # Create a clean URL using the ASIN
                product_link = f"https://www.amazon.in/dp/{asin}"
            else:
                # Fallback: try to find direct product links
                if link_element:
                    href = link_element.get('href')
                    if href and not href.startswith('javascript:') and href != '#':
                        # Handle Amazon's complex redirect URLs
                        if '/dp/' in href:
                            # Extract direct DP link from complex URLs
                            dp_match = re.search(r'([^&]*?/dp/[A-Z0-9]{10})', href)
                            if dp_match:
                                clean_url = dp_match.group(1)
                                if clean_url.startswith('/'):
                                    product_link = f"https://www.amazon.in{clean_url}"
                                else:
                                    product_link = f"https://www.amazon.in/{clean_url}"
                        elif href.startswith('/'):
                            product_link = f"https://www.amazon.in{href}"
                        elif href.startswith('https://www.amazon.in'):
                            product_link = href
            
            # Extract original price
            original_price = None
            if original_price_element:
                original_price = original_price_element.get_text(strip=True)
            
            # Extract delivery info
            delivery = None
            if delivery_element:
                delivery = delivery_element.get_text(strip=True)
            
            product_data = {
                'title': title,
                'price': price,
                'original_price': original_price,
                'rating': rating,
                'reviews_count': reviews_count,
                'image_url': image_url,
                'product_link': product_link,
                'delivery': delivery
            }
            
            products.append(product_data)
    
    return products