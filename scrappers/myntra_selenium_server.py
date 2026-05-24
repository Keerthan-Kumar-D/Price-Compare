from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

app = Flask(__name__)
CORS(app)

def setup_driver():
    chrome_options = Options()
    # chrome_options.add_argument('--headless')  # Comment out to see browser
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36')
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
    except Exception as e:
        print(f"Error setting up driver: {e}")
        raise

def scrape_myntra(search_query, max_products=12):
    search_url = f"https://www.myntra.com/{search_query.replace(' ', '-')}"
    
    print(f"\n{'='*60}")
    print(f"Starting scrape for: {search_query}")
    print(f"URL: {search_url}")
    print(f"{'='*60}\n")
    
    driver = None
    products = []
    
    try:
        driver = setup_driver()
        print("✓ Driver setup successful")
        
        print(f"Loading page: {search_url}")
        driver.get(search_url)
        print("✓ Page loaded")
        
        print("Waiting 5 seconds for content to load...")
        time.sleep(5)
        
        print("Scrolling page...")
        for i in range(3):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            print(f"  Scroll {i+1}/3 complete")
        
        print("\nSearching for product elements...")
        product_elements = driver.find_elements(By.CSS_SELECTOR, "li.product-base")
        print(f"✓ Found {len(product_elements)} product elements")
        
        if len(product_elements) == 0:
            print("⚠ No products found! Myntra may have blocked the request or changed structure")
            # Try alternative selectors
            alt_elements = driver.find_elements(By.CSS_SELECTOR, "[class*='product']")
            print(f"Alternative selector found {len(alt_elements)} elements")
            return {"error": "No products found. Myntra may be blocking automated requests."}
        
        for idx, product in enumerate(product_elements[:max_products], 1):
            try:
                print(f"\nExtracting product {idx}...")
                
                brand = "N/A"
                try:
                    brand = product.find_element(By.CSS_SELECTOR, ".product-brand").text
                except:
                    pass
                
                title = "N/A"
                try:
                    title = product.find_element(By.CSS_SELECTOR, ".product-product").text
                except:
                    pass
                
                price = "N/A"
                try:
                    price = product.find_element(By.CSS_SELECTOR, ".product-discountedPrice").text
                except:
                    pass
                
                original_price = None
                try:
                    original_price = product.find_element(By.CSS_SELECTOR, ".product-strike").text
                except:
                    pass
                
                discount = None
                try:
                    discount = product.find_element(By.CSS_SELECTOR, ".product-discountPercentage").text
                except:
                    pass
                
                rating = "N/A"
                try:
                    rating = product.find_element(By.CSS_SELECTOR, ".product-ratingsContainer span").text
                except:
                    pass
                
                reviews = "N/A"
                try:
                    reviews = product.find_element(By.CSS_SELECTOR, ".product-ratingsCount").text
                except:
                    pass
                
                image_url = None
                try:
                    img_element = product.find_element(By.CSS_SELECTOR, "img.img-responsive")
                    image_url = img_element.get_attribute("src") or img_element.get_attribute("data-src")
                    if not image_url or image_url == "N/A":
                        image_url = "https://via.placeholder.com/300x400/667eea/ffffff?text=No+Image"
                except:
                    image_url = "https://via.placeholder.com/300x400/667eea/ffffff?text=No+Image"
                
                product_link = "N/A"
                try:
                    product_link = product.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
                except:
                    pass
                
                product_data = {
                    'brand': brand,
                    'title': title,
                    'price': price,
                    'original_price': original_price,
                    'discount': discount,
                    'rating': rating,
                    'reviews_count': reviews,
                    'image_url': image_url,
                    'product_link': product_link
                }
                
                products.append(product_data)
                print(f"  ✓ {brand} - {title[:30]}...")
                
            except Exception as e:
                print(f"  ✗ Error extracting product {idx}: {e}")
                continue
        
        print(f"\n{'='*60}")
        print(f"✓ Successfully scraped {len(products)} products")
        print(f"{'='*60}\n")
        
    except Exception as e:
        print(f"\n✗ Error during scraping: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}
    
    finally:
        if driver:
            print("Closing browser...")
            driver.quit()
            print("✓ Browser closed")
    
    return products

@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Myntra Scraper API</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            .container {
                background: rgba(255, 255, 255, 0.1);
                padding: 30px;
                border-radius: 15px;
                backdrop-filter: blur(10px);
            }
            h1 { text-align: center; margin-bottom: 30px; }
            .endpoint {
                background: rgba(255, 255, 255, 0.2);
                padding: 15px;
                border-radius: 8px;
                margin: 15px 0;
            }
            code {
                background: rgba(0, 0, 0, 0.3);
                padding: 5px 10px;
                border-radius: 4px;
                display: inline-block;
                margin: 5px 0;
            }
            .method { 
                display: inline-block;
                padding: 5px 10px;
                border-radius: 4px;
                font-weight: bold;
                margin-right: 10px;
            }
            .get { background: #10b981; }
            .post { background: #3b82f6; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🛍️ Myntra Scraper API</h1>
            
            <div class="endpoint">
                <span class="method get">GET</span>
                <strong>/health</strong>
                <p>Check if the server is running</p>
            </div>
            
            <div class="endpoint">
                <span class="method get">GET</span>
                <strong>/search?q={query}</strong>
                <p>Search for products on Myntra</p>
                <code>Example: /search?q=mens-tshirts</code>
            </div>
            
            <div style="margin-top: 30px; text-align: center; opacity: 0.8;">
                <p>Server is running on <code>http://localhost:5000</code></p>
                <p>Using Selenium WebDriver for dynamic content</p>
            </div>
        </div>
    </body>
    </html>
    """

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '')
    
    if not query:
        return jsonify({"error": "Query parameter 'q' is required"}), 400
    
    print(f"\n🔍 Received search request for: {query}")
    
    try:
        products = scrape_myntra(query, max_products=12)
        
        if isinstance(products, dict) and 'error' in products:
            return jsonify(products), 500
        
        return jsonify({
            "query": query,
            "count": len(products),
            "products": products
        })
    
    except Exception as e:
        print(f"Error in search endpoint: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "message": "Server is running"})

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("🚀 Starting Myntra Scraper Server")
    print("=" * 60)
    print("Server: http://localhost:5000")
    print("Browser will open when scraping (for debugging)")
    print("=" * 60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
