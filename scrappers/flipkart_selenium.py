from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import re
import logging

logger = logging.getLogger(__name__)

def search_flipkart_selenium(search_query, max_wait=5):
    """
    Scrape Flipkart using Selenium to handle JavaScript-loaded images.
    Returns list of products with images.
    """
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.binary_location = "/usr/bin/google-chrome"
    options.add_argument(
        'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
    )
    
    driver = None
    try:
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
        driver.set_page_load_timeout(15)
        
        url = f"https://www.flipkart.com/search?q={search_query.replace(' ', '+')}"
        driver.get(url)
        
        # Wait for initial load
        time.sleep(3)
        
        # Scroll and wait for images to load using JavaScript
        driver.execute_script("""
            // Scroll to load all images
            window.scrollTo(0, document.body.scrollHeight);
        """)
        time.sleep(1.5)
        
        # Scroll back up
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)
        
        # Wait for images with 'rukminim' in src to be loaded
        try:
            WebDriverWait(driver, 8).until(
                lambda d: len(d.find_elements(By.CSS_SELECTOR, "img[src*='rukminim']")) > 3
            )
        except:
            pass  # Continue even if timeout
        
        # Extract image URLs directly from Selenium before parsing HTML
        image_list = []
        try:
            # Find all product images (exclude banners)
            all_imgs = driver.find_elements(By.CSS_SELECTOR, "img[src*='rukminim']")
            
            for img in all_imgs:
                img_src = img.get_attribute('src')
                if img_src and 'fk-p-flap' not in img_src:  # Exclude banner images
                    image_list.append(img_src)
        except Exception as e:
            pass
        
        # Get page source after JS execution
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        
        products = []
        seen_titles = set()
        image_index = 0  # Track which image to use
        
        # Try fashion layout first (div with class p0C73x)
        containers = soup.find_all('div', class_='p0C73x')
        
        # If no fashion containers, try electronics/laptop layout (div with data-id)
        if not containers:
            containers = soup.find_all('div', {'data-id': True})
        
        for container in containers:
            try:
                # Find title anchor - try multiple selectors
                anchors = container.find_all('a')
                title_anchor = None
                title = None
                
                for a in anchors:
                    # Check title attribute first
                    if a.get('title'):
                        title_text = a.get('title', '').strip()
                        # Skip price/offer anchors
                        if '₹' not in title_text and 'offer' not in title_text.lower() and len(title_text) > 5:
                            title_anchor = a
                            title = title_text
                            break
                
                # If no title attribute, try text content or class-based search
                if not title_anchor:
                    # First try to find title in a child div/span (cleaner for electronics)
                    title_elem = container.find(['div', 'span'], class_=['RG5Slk', 'KzDlHZ', 'wjcEIp'])
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                        # Find the product link
                        for a in anchors:
                            if '/p/itm' in a.get('href', ''):
                                title_anchor = a
                                break
                    
                    # Fallback: extract from anchor text
                    if not title_anchor:
                        for a in anchors:
                            href = a.get('href', '')
                            if '/p/itm' in href:  # Product link pattern
                                # Get text from the anchor or nearby elements
                                text = a.get_text(strip=True)
                                # Clean up common prefixes
                                text = text.replace('Add to Compare', '').strip()
                                # Try to extract just the product name (before ratings/specs)
                                if '₹' in text:
                                    # Split at rupee symbol and take first part
                                    parts = text.split('₹')
                                    text = parts[0].strip()
                                # Remove rating text
                                import re as re_module
                                text = re_module.split(r'\d+\.\d+\d+\s+Ratings', text)[0].strip()
                                
                                if text and len(text) > 10:
                                    title_anchor = a
                                    title = text
                                    break
                
                if not title_anchor or not title or title in seen_titles:
                    continue
                
                # Find price
                price = None
                price_text = container.find(string=re.compile(r'₹\s*[0-9]'))
                if price_text:
                    m = re.search(r'(₹\s*[\d,]+)', str(price_text))
                    price = m.group(1) if m else None
                
                # Find image - use next image from list
                image_url = None
                if image_index < len(image_list):
                    image_url = image_list[image_index]
                    image_index += 1
                
                # Product link
                href = title_anchor.get('href', '')
                product_link = f"https://www.flipkart.com{href}" if href.startswith('/') else href
                
                product_data = {
                    'title': title,
                    'price': price,
                    'original_price': None,
                    'discount': None,
                    'rating': None,
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
                
            except Exception as e:
                continue
        
        return products
        
    finally:
        if driver:
            driver.quit()


if __name__ == "__main__":
    import sys
    import io
    # Fix Windows console encoding
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    print("Testing Selenium-based Flipkart scraper...")
    products = search_flipkart_selenium('tshirt')
    
    print(f"\nFound {len(products)} products:")
    for i, p in enumerate(products[:5], 1):
        print(f"\nProduct {i}:")
        print(f"Title: {p['title'][:60]}...")
        print(f"Price: {p['price']}")
        print(f"Has Image: {'Yes' if p['image_url'] else 'No'}")
        if p['image_url']:
            print(f"Image: {p['image_url'][:80]}...")
