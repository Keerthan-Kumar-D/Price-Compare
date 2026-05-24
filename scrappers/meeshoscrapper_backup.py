from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import time
import re


class MeeshoScraper:
    def __init__(self, headless=True):
        """Initialize the Meesho scraper with Chrome driver"""
        chrome_options = Options()
        if headless:
            chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-software-rasterizer')
        chrome_options.add_argument('--remote-debugging-port=9222')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36')
        
        # Prevent Chrome from closing
        chrome_options.add_experimental_option("detach", False)
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        try:
            # Use WebDriver Manager to handle ChromeDriver
            print("Initializing ChromeDriver...")
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            print("✓ ChromeDriver initialized successfully")
            self.driver.set_page_load_timeout(30)
            self.driver.implicitly_wait(10)
            if not headless:
                self.driver.maximize_window()
        except Exception as e:
            print(f"✗ Error initializing ChromeDriver: {e}")
            raise
        
    def search_meesho_product(self, search_query):
        """Generate Meesho search URL from query"""
        search_url = f"https://www.meesho.com/search?q={search_query.replace(' ', '%20')}"
        return search_url
    
    def fetch_meesho_search_results(self, search_url, scroll_count=3):
        """Fetch products from Meesho search URL with scrolling"""
        try:
            # Check if driver is still alive
            try:
                _ = self.driver.window_handles
                print(f"✓ Browser session is active")
            except Exception as e:
                print(f"✗ Browser session lost before navigation: {e}")
                return []
            
            print(f"Loading URL: {search_url}")
            self.driver.get(search_url)
            
            # Verify we can still interact with the page
            try:
                print("Waiting for page to load...")
                time.sleep(5)
                
                current_url = self.driver.current_url
                page_title = self.driver.title
                print(f"✓ Current URL: {current_url}")
                print(f"✓ Page title: {page_title}")
            except Exception as e:
                print(f"✗ Lost connection after page load: {e}")
                return []
            
            # Scroll to load more products
            print(f"Scrolling {scroll_count} times to load more products...")
            for i in range(scroll_count):
                try:
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(3)  # Increased wait time
                    print(f"  ✓ Scroll {i+1}/{scroll_count} complete")
                except Exception as e:
                    print(f"  ✗ Error during scroll {i+1}: {e}")
                    break
            
            # Scroll back to top
            try:
                self.driver.execute_script("window.scrollTo(0, 0);")
                time.sleep(2)
            except Exception as e:
                print(f"✗ Error scrolling back to top: {e}")
            
            print("Page loaded and scrolled successfully")
            return True
            
        except Exception as e:
            print(f"Error fetching search results: {e}")
            return False
    
    def parse_meesho_products(self):
        """Parse and extract product information from loaded page"""
        products = []
        
        try:
            print("Attempting to find products with multiple selectors...")
            
            # Try multiple selectors as Meesho may have changed their structure
            selectors = [
                'a[href*="/product/"]',  # Original selector
                'div[class*="ProductCard"]',  # Card container
                'div[class*="product"]',  # Generic product class
                '[data-testid*="product"]',  # Test ID
                'a[href*="/p/"]',  # Short product URL
            ]
            
            product_cards = []
            for selector in selectors:
                try:
                    print(f"  Trying selector: {selector}")
                    cards = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if cards:
                        print(f"    ✓ Found {len(cards)} elements with this selector")
                        product_cards = cards
                        break
                    else:
                        print(f"    ✗ No elements found")
                except Exception as e:
                    print(f"    ✗ Error with selector: {e}")
                    continue
            
            if not product_cards:
                print("\nWARNING: No product cards found with any selector!")
                print(f"Current URL: {self.driver.current_url}")
                
                # Try to get page source for debugging
                print("\nPage source preview (first 500 chars):")
                print(self.driver.page_source[:500])
                
                # Save screenshot
                try:
                    screenshot_path = "meesho_no_products.png"
                    self.driver.save_screenshot(screenshot_path)
                    print(f"\nScreenshot saved: {screenshot_path}")
                except:
                    pass
                
                return []
            
            print(f"\nParsing {len(product_cards)} product cards...")
            
            parsed_count = 0
            for idx, card in enumerate(product_cards):
                try:
                    product_data = self._extract_product_data(card)
                    if product_data and product_data.get('title') and product_data.get('price'):
                        products.append(product_data)
                        parsed_count += 1
                        if parsed_count == 1:
                            print(f"Sample product: {product_data.get('title')[:50]}... @ {product_data.get('price')}")
                except Exception as e:
                    # Skip problematic products
                    continue
            
            print(f"Successfully parsed {parsed_count} products with title and price")
            
            # Remove duplicates based on product_link
            seen_links = set()
            unique_products = []
            for product in products:
                link = product.get('product_link')
                if link and link not in seen_links:
                    seen_links.add(link)
                    unique_products.append(product)
                elif not link:
                    # If no link, add anyway (better than nothing)
                    unique_products.append(product)
            
            print(f"Returning {len(unique_products)} unique products after deduplication")
            return unique_products
            
        except Exception as e:
            print(f"ERROR parsing products: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _extract_product_data(self, card):
        """Extract data from a single product card"""
        product_data = {
            'title': None,
            'price': None,
            'original_price': None,
            'discount': None,
            'rating': None,
            'reviews_count': None,
            'image_url': None,
            'product_link': None,
            'delivery': None,
            'cod_available': None
        }
        
        try:
            # Get all text from card for easier parsing
            card_text = card.text
            
            # Extract product link - try multiple attributes
            try:
                product_data['product_link'] = card.get_attribute('href')
                if not product_data['product_link']:
                    # If card is not a link, try to find link inside it
                    link_element = card.find_element(By.TAG_NAME, 'a')
                    product_data['product_link'] = link_element.get_attribute('href')
            except NoSuchElementException:
                pass
            
            # Extract title - try multiple selectors
            title_selectors = [
                'p[class*="Text"]',
                'p[class*="title"]',
                'h2',
                'h3',
                '.product-title',
                '[class*="ProductName"]'
            ]
            for selector in title_selectors:
                try:
                    title_element = card.find_element(By.CSS_SELECTOR, selector)
                    title_text = title_element.text.strip()
                    if title_text and len(title_text) > 3:  # Valid title
                        product_data['title'] = title_text
                        break
                except NoSuchElementException:
                    continue
            
            # If still no title, try getting from card text
            if not product_data['title'] and card_text:
                lines = card_text.split('\n')
                # Usually the first or second line is the title
                for line in lines[:3]:
                    if line and len(line) > 10 and '₹' not in line:
                        product_data['title'] = line.strip()
                        break
            
            # Extract price - try multiple approaches
            price_selectors = [
                'h5[class*="Text"]',
                'span[class*="price"]',
                '[class*="Price"]',
                'h5',
                'h6'
            ]
            for selector in price_selectors:
                try:
                    price_elements = card.find_elements(By.CSS_SELECTOR, selector)
                    for elem in price_elements:
                        price_text = elem.text.strip()
                        if price_text and '₹' in price_text:
                            product_data['price'] = price_text
                            break
                    if product_data['price']:
                        break
                except NoSuchElementException:
                    continue
            
            # If no price from selectors, search in card text
            if not product_data['price'] and card_text:
                price_match = re.search(r'₹\s*[\d,]+', card_text)
                if price_match:
                    product_data['price'] = price_match.group(0).strip()
            
            # Extract original price (MRP)
            try:
                original_price = card.find_element(By.CSS_SELECTOR, 'span[style*="text-decoration"]')
                product_data['original_price'] = original_price.text.strip()
            except NoSuchElementException:
                # Try to find strikethrough text
                if card_text:
                    lines = card_text.split('\n')
                    for line in lines:
                        if '₹' in line and line != product_data.get('price'):
                            product_data['original_price'] = line.strip()
                            break
            
            # Extract discount
            try:
                discount_match = re.search(r'(\d+%\s*OFF)', card_text, re.IGNORECASE)
                if discount_match:
                    product_data['discount'] = discount_match.group(1)
            except Exception:
                pass
            
            # Extract image URL
            try:
                image_element = card.find_element(By.TAG_NAME, 'img')
                product_data['image_url'] = image_element.get_attribute('src') or image_element.get_attribute('data-src')
            except NoSuchElementException:
                pass
            
            # Extract rating
            try:
                rating_match = re.search(r'(\d+\.?\d*)\s*★', card_text)
                if rating_match:
                    product_data['rating'] = rating_match.group(1)
            except Exception:
                pass
            
            # Extract reviews count
            try:
                reviews_match = re.search(r'(\d+(?:\.\d+)?[kK]?)\s*(?:Reviews?|Ratings?)', card_text, re.IGNORECASE)
                if reviews_match:
                    product_data['reviews_count'] = reviews_match.group(1)
            except Exception:
                pass
            
            # Check for Free Delivery
            try:
                if 'Free Delivery' in card_text or 'FREE' in card_text.upper():
                    product_data['delivery'] = 'Free Delivery'
            except Exception:
                pass
            
            # Check for COD
            try:
                if 'COD' in card_text.upper() or 'Cash on Delivery' in card_text:
                    product_data['cod_available'] = 'COD Available'
            except Exception:
                pass
            
        except Exception as e:
            print(f"Error extracting product data: {e}")
        
        return product_data
    
    def scrape(self, search_query, scroll_count=3):
        """Main method to scrape products for a search query"""
        try:
            search_url = self.search_meesho_product(search_query)
            print(f"Searching: {search_url}")
            
            if self.fetch_meesho_search_results(search_url, scroll_count):
                products = self.parse_meesho_products()
                return products
            else:
                return []
                
        except Exception as e:
            print(f"Error during scraping: {e}")
            return []
    
    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()


# Helper function for simple usage
def search_meesho(search_query, headless=True, scroll_count=3):
    """
    Simple function to search Meesho and get products
    
    Args:
        search_query: Product search term
        headless: Run browser in headless mode
        scroll_count: Number of times to scroll for loading more products
        
    Returns:
        List of product dictionaries
    """
    with MeeshoScraper(headless=headless) as scraper:
        return scraper.scrape(search_query, scroll_count=scroll_count)