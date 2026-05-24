from bs4 import BeautifulSoup
import requests
import re
import json

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-IN,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://www.reliancedigital.in/",
    "DNT": "1",  # Do Not Track
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

def search_reliance_digital_product(search_query):
    search_url = f"https://www.reliancedigital.in/search?searchTerm={search_query.replace(' ', '%20')}"
    return search_url

def fetch_reliance_digital_search_results(search_url):
    response = requests.get(search_url, headers=headers, timeout=3)
    if response.status_code == 200:
        return response.text
    else:
        raise Exception(f"Failed to fetch page, status code: {response.status_code}")

def parse_reliance_digital_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    products = []

    # First, try to extract data from JavaScript/JSON in script tags
    # Reliance Digital uses client-side rendering with data in window.__INITIAL_STATE__
    scripts = soup.find_all('script')
    
    for script in scripts:
        if script.string and 'window.__INITIAL_STATE__' in script.string:
            try:
                # Extract the JSON data from the script
                script_content = script.string
                
                # The site uses dynamic loading, so the initial state might not contain products
                # We can detect if products are still loading
                if '"loading":true' in script_content:
                    print("Reliance Digital: Products are still loading (JavaScript-rendered content)")
                    # In a real-world scenario, we'd use Selenium or similar to wait for JavaScript to load
                    return [{
                        'title': 'JavaScript-rendered content detected',
                        'price': 'Reliance Digital uses dynamic loading',
                        'mrp': None,
                        'discount': None,
                        'savings': None,
                        'rating': None,
                        'special_tag': 'Note: This site requires JavaScript rendering',
                        'image_url': None,
                        'product_link': None,
                        'delivery': None,
                        'brand': None,
                        'description': 'To scrape this site effectively, use Selenium or Playwright for JavaScript rendering'
                    }]
                
                # Find the JSON object - more robust pattern
                json_match = re.search(r'window\.__INITIAL_STATE__\s*=\s*(\{.*?\});?\s*(?=window\.|$)', script_content, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                    
                    # Try to parse the JSON in chunks since it might be very large
                    # Look for product listing data specifically
                    product_match = re.search(r'"productListingPage":\s*\{[^}]*"productlists":\s*\{[^}]*"items":\s*(\[.*?\])', json_str, re.DOTALL)
                    if product_match:
                        products_json_str = product_match.group(1)
                        
                        try:
                            products_data = json.loads(products_json_str)
                            
                            for item in products_data:
                                if isinstance(item, dict):
                                    # Extract product information from the JSON structure
                                    title = item.get('name', 'Title not available')
                                    
                                    # Extract price information
                                    price_info = item.get('price', {})
                                    if isinstance(price_info, dict):
                                        effective_price = price_info.get('effective', {}).get('currency_value')
                                        marked_price = price_info.get('marked', {}).get('currency_value')
                                        
                                        price = f"₹{effective_price:,.2f}" if effective_price else 'Price not available'
                                        mrp = f"₹{marked_price:,.2f}" if marked_price else None
                                    else:
                                        price = 'Price not available'
                                        mrp = None
                                    
                                    # Extract discount
                                    discount = None
                                    if price_info and isinstance(price_info, dict):
                                        marked_price = price_info.get('marked', {}).get('currency_value', 0)
                                        effective_price = price_info.get('effective', {}).get('currency_value', 0)
                                        if marked_price and effective_price and marked_price > effective_price:
                                            discount_percent = ((marked_price - effective_price) / marked_price) * 100
                                            discount = f"{discount_percent:.0f}% OFF"
                                    
                                    # Extract image
                                    image_url = None
                                    medias = item.get('medias', [])
                                    if medias and len(medias) > 0:
                                        image_url = medias[0].get('url')
                                    
                                    # Extract product link
                                    product_link = None
                                    slug = item.get('slug')
                                    if slug:
                                        product_link = f"https://www.reliancedigital.in/product/{slug}"
                                    
                                    # Extract brand and other details
                                    brand = item.get('brand', {}).get('name', '')
                                    short_description = item.get('short_description', '')
                                    
                                    # Extract rating if available
                                    rating = None
                                    rating_info = item.get('rating')
                                    if rating_info:
                                        rating = str(rating_info)
                                    
                                    # Calculate savings
                                    savings = None
                                    if price != 'Price not available' and mrp:
                                        try:
                                            price_num = float(re.sub(r'[^\d.]', '', price.replace(',', '')))
                                            mrp_num = float(re.sub(r'[^\d.]', '', mrp.replace(',', '')))
                                            if mrp_num > price_num:
                                                savings = f"₹{mrp_num - price_num:,.2f}"
                                        except:
                                            pass
                                    
                                    product_data = {
                                        'title': title,
                                        'price': price,
                                        'mrp': mrp,
                                        'discount': discount,
                                        'savings': savings,
                                        'rating': rating,
                                        'special_tag': None,
                                        'image_url': image_url,
                                        'product_link': product_link,
                                        'delivery': None,
                                        'brand': brand,
                                        'description': short_description
                                    }
                                    
                                    products.append(product_data)
                                    
                        except json.JSONDecodeError as e:
                            print(f"Failed to parse products JSON: {e}")
                        except Exception as e:
                            print(f"Error processing products data: {e}")
                
            except Exception as e:
                print(f"Error extracting from script: {e}")
                
    # If we found products from JSON, return them
    if products:
        return products

    # Fallback: Since this is a JavaScript-heavy site, provide a helpful message
    return [{
        'title': 'Reliance Digital - JavaScript Required',
        'price': 'This site uses dynamic content loading',
        'mrp': None,
        'discount': None,
        'savings': None,
        'rating': None,
        'special_tag': 'JavaScript Framework Detected',
        'image_url': None,
        'product_link': 'https://www.reliancedigital.in',
        'delivery': None,
        'brand': None,
        'description': 'This site requires JavaScript rendering tools like Selenium or Playwright for full data extraction'
    }]