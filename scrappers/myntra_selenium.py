"""
Myntra Selenium Scraper Module
Extracts product data from Myntra using Selenium WebDriver
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import logging

logger = logging.getLogger(__name__)

def setup_selenium_driver():
    """Setup Chrome WebDriver with appropriate options"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Run in headless mode for backend
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36')
    chrome_options.add_argument('--log-level=3')  # Suppress logs
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
    except Exception as e:
        logger.error(f"Error setting up Selenium driver: {e}")
        raise

def scrape_myntra_selenium(search_query, max_products=12):
    """
    Scrape Myntra products using Selenium WebDriver
    
    Args:
        search_query (str): Search query for products
        max_products (int): Maximum number of products to return (default: 12)
    
    Returns:
        list: List of product dictionaries or dict with error
    """
    search_url = f"https://www.myntra.com/{search_query.replace(' ', '-')}"
    
    logger.info(f"Starting Selenium scrape for Myntra: {search_query}")
    
    driver = None
    products = []
    
    try:
        driver = setup_selenium_driver()
        logger.info("Selenium driver setup successful")
        
        logger.info(f"Loading Myntra page: {search_url}")
        driver.get(search_url)
        
        # Wait for content to load (minimal wait for 10s target)
        time.sleep(1.5)
        
        # Single scroll for speed (10s target)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.8)
        
        # Find product elements
        product_elements = driver.find_elements(By.CSS_SELECTOR, "li.product-base")
        logger.info(f"Found {len(product_elements)} product elements")
        
        if len(product_elements) == 0:
            logger.warning("No products found on Myntra")
            return []
        
        # Extract product data
        for idx, product in enumerate(product_elements[:max_products], 1):
            try:
                # Extract brand
                brand = "N/A"
                try:
                    brand = product.find_element(By.CSS_SELECTOR, ".product-brand").text
                except:
                    pass
                
                # Extract title
                title = "N/A"
                try:
                    title = product.find_element(By.CSS_SELECTOR, ".product-product").text
                except:
                    pass
                
                # Extract price (discounted price is the current/lowest price)
                price = "N/A"
                try:
                    price_text = product.find_element(By.CSS_SELECTOR, ".product-discountedPrice").text
                    # Clean price: remove 'Rs', 'rs', extra spaces, keep only numbers
                    price_text = price_text.replace('Rs', '').replace('rs', '').replace('.', '').strip()
                    # Remove any remaining spaces
                    price_text = price_text.replace(' ', '')
                    # Format with ₹ symbol
                    price = f"₹{price_text}"
                except:
                    pass
                
                # Extract original price (strike-through price)
                original_price = None
                try:
                    original_price_text = product.find_element(By.CSS_SELECTOR, ".product-strike").text
                    # Clean original price: remove 'Rs', 'rs', extra spaces
                    original_price_text = original_price_text.replace('Rs', '').replace('rs', '').replace('.', '').strip()
                    # Remove any remaining spaces
                    original_price_text = original_price_text.replace(' ', '')
                    original_price = f"₹{original_price_text}"
                except:
                    pass
                
                # Extract discount
                discount = None
                try:
                    discount = product.find_element(By.CSS_SELECTOR, ".product-discountPercentage").text
                except:
                    pass
                
                # Extract rating
                rating = None
                try:
                    rating = product.find_element(By.CSS_SELECTOR, ".product-ratingsContainer span").text
                except:
                    pass
                
                # Extract reviews count
                reviews_count = None
                try:
                    reviews_count = product.find_element(By.CSS_SELECTOR, ".product-ratingsCount").text
                except:
                    pass
                
                # Extract image URL
                image_url = None
                try:
                    img_element = product.find_element(By.CSS_SELECTOR, "img.img-responsive")
                    image_url = img_element.get_attribute("src") or img_element.get_attribute("data-src")
                    if not image_url or image_url == "N/A":
                        image_url = None
                except:
                    pass
                
                # Extract product link
                product_link = None
                try:
                    product_link = product.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
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
        
        logger.info(f"Successfully scraped {len(products)} products from Myntra")
        
    except Exception as e:
        logger.error(f"Error during Myntra Selenium scraping: {e}")
        import traceback
        traceback.print_exc()
        return []
    
    finally:
        if driver:
            driver.quit()
            logger.info("Selenium browser closed")
    
    return products

def search_myntra_product(search_query):
    """Generate Myntra search URL from query"""
    return f"https://www.myntra.com/{search_query.replace(' ', '-')}"

# For backward compatibility with existing code
scrape_myntra = scrape_myntra_selenium
