from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
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
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36')
        
        # Anti-detection
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        
        try:
            # Use WebDriver Manager to handle ChromeDriver
            print("Initializing ChromeDriver...")
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Remove webdriver property
            self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    })
                '''
            })
            
            print("✓ ChromeDriver initialized successfully")
            self.driver.set_page_load_timeout(30)
            self.driver.implicitly_wait(5)
        except Exception as e:
            print(f"✗ Error initializing ChromeDriver: {e}")
            raise
        
    def scrape(self, query, scroll_count=3):
        """Main scraping method"""
        search_url = f"https://www.meesho.com/search?q={query.replace(' ', '%20')}"
        print(f"Searching: {search_url}")
        
        try:
            # Load page
            self.driver.get(search_url)
            print("✓ Page loaded, waiting for JavaScript to render...")
            time.sleep(10)  # Increased wait for React/Next.js to render
            
            # Scroll to load more products
            print(f"Scrolling {scroll_count} times...")
            for i in range(scroll_count):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)  # Longer wait between scrolls
                print(f"  ✓ Scroll {i+1}/{scroll_count}")
            
            # Scroll back to top to see all products
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(2)
            
            # Get page source and parse with BeautifulSoup
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Save page source for debugging (full version this time)
            with open('meesho_page_full.html', 'w', encoding='utf-8') as f:
                f.write(page_source)
            print("✓ Full page source saved to meesho_page_full.html")
            
            print("Parsing products...")
            products = self._parse_products(soup)
            print(f"✓ Found {len(products)} products")
            
            return products
            
        except Exception as e:
            print(f"✗ Error during scraping: {e}")
            import traceback
            traceback.print_exc()
            return []
        finally:
            try:
                self.driver.quit()
                print("✓ Browser closed")
            except:
                pass
    
    def _parse_products(self, soup):
        """Parse products from BeautifulSoup object"""
        products = []
        
        # Try to find product links - Meesho uses /p/ pattern
        product_links = soup.select('a[href*="/p/"]')
        print(f"Found {len(product_links)} product links")
        
        for idx, link in enumerate(product_links[:40]):  # Limit to 40 products
            try:
                product = {}
                
                # Get product link
                href = link.get('href', '')
                if href:
                    product['product_link'] = f"https://www.meesho.com{href}" if href.startswith('/') else href
                
                # Get all text from this link's container
                text_content = link.get_text(strip=True, separator='\n')
                lines = [l.strip() for l in text_content.split('\n') if l.strip()]
                
                # Extract title (usually first meaningful line)
                for line in lines:
                    if len(line) > 10 and '₹' not in line and '%' not in line and 'Reviews' not in line and 'Free Delivery' not in line:
                        product['title'] = line
                        break
                
                # Extract price (look for ₹ symbol)
                for line in lines:
                    if '₹' in line:
                        # Clean price
                        price_match = re.search(r'₹\s*[\d,]+', line)
                        if price_match:
                            product['price'] = price_match.group(0).strip()
                            break
                
                # Extract image
                img = link.select_one('img')
                if img:
                    product['image_url'] = img.get('src', '') or img.get('data-src', '')
                
                # Extract rating if available
                rating_text = ' '.join(lines)
                rating_match = re.search(r'(\d+\.?\d*)\s*\d+\s*Reviews', rating_text)
                if rating_match:
                    product['rating'] = rating_match.group(1)
                
                # Extract reviews count
                reviews_match = re.search(r'(\d+)\s*Reviews', rating_text)
                if reviews_match:
                    product['reviews_count'] = reviews_match.group(1)
                
                # Check for COD
                if 'COD' in text_content.upper() or 'CASH ON DELIVERY' in text_content.upper():
                    product['cod_available'] = 'Yes'
                
                # Extract discount
                discount_match = re.search(r'(\d+)%\s*off', text_content, re.IGNORECASE)
                if discount_match:
                    product['discount'] = f"{discount_match.group(1)}%"
                
                # Only add if we have both title and price
                if product.get('title') and product.get('price'):
                    products.append(product)
                    
                    # Show first product as sample
                    if len(products) == 1:
                        print(f"Sample: {product['title'][:40]}... @ {product['price']}")
                
            except Exception as e:
                if idx < 3:
                    print(f"Error parsing product {idx+1}: {e}")
                continue
        
        return products

def search_meesho(query, headless=True, scroll_count=3):
    """Helper function to search Meesho"""
    scraper = MeeshoScraper(headless=headless)
    return scraper.scrape(query, scroll_count=scroll_count)

if __name__ == "__main__":
    # Test the scraper
    print("Testing Meesho Scraper...")
    products = search_meesho("women kurta", headless=False, scroll_count=2)
    
    print(f"\n{'='*60}")
    print(f"RESULTS: {len(products)} products found")
    print(f"{'='*60}")
    
    for i, p in enumerate(products[:5], 1):
        print(f"\n{i}. {p.get('title', 'N/A')}")
        print(f"   Price: {p.get('price', 'N/A')}")
        print(f"   Link: {p.get('product_link', 'N/A')[:60]}...")
