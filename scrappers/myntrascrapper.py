from bs4 import BeautifulSoup
import requests
import json
import re

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-IN,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://www.myntra.com/",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}


def search_myntra_product(search_query):
    """Generate Myntra search URL from query"""
    search_url = f"https://www.myntra.com/{search_query.replace(' ', '-')}"
    return search_url


def fetch_myntra_search_results(search_url):
    """Fetch HTML content from Myntra search page"""
    response = requests.get(search_url, headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        raise Exception(f"Failed to fetch page, status code: {response.status_code}")


def parse_myntra_html(html_content):
    """Parse Myntra HTML and extract product information"""
    soup = BeautifulSoup(html_content, 'html.parser')
    products = []
    
    # Myntra often loads data via JavaScript, but some info is in script tags
    # Look for product data in script tags
    script_tags = soup.find_all('script', type='text/javascript')
    
    for script in script_tags:
        script_content = script.string
        if script_content and 'searchData' in script_content:
            # Try to extract JSON data from script
            try:
                # Find JSON data in the script
                json_match = re.search(r'window\.__myx\s*=\s*({.*?});', script_content, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group(1))
                    # Navigate through the nested structure to find products
                    if 'searchData' in data and 'results' in data['searchData']:
                        for item in data['searchData']['results']:
                            product_data = extract_product_from_json(item)
                            if product_data:
                                products.append(product_data)
            except (json.JSONDecodeError, KeyError) as e:
                continue
    
    # Fallback: Parse HTML structure if JSON parsing fails
    if not products:
        products = parse_myntra_html_structure(soup)
    
    return products


def extract_product_from_json(item):
    """Extract product information from JSON data"""
    try:
        product_data = {
            'title': item.get('productName', 'N/A'),
            'brand': item.get('brand', 'N/A'),
            'price': f"₹{item.get('price', 'N/A')}",
            'original_price': f"₹{item.get('mrp', 'N/A')}" if item.get('mrp') else None,
            'discount': f"{item.get('discount', 'N/A')}% OFF" if item.get('discount') else None,
            'rating': item.get('rating', 'N/A'),
            'reviews_count': item.get('ratingCount', 'N/A'),
            'image_url': item.get('searchImage', 'N/A'),
            'product_link': f"https://www.myntra.com/{item.get('landingPageUrl', '')}",
            'product_id': item.get('productId', 'N/A')
        }
        return product_data
    except Exception as e:
        return None


def parse_myntra_html_structure(soup):
    """Fallback method to parse HTML structure directly"""
    products = []
    
    # Myntra uses different class names, these may need updating
    product_items = soup.select('li.product-base, .product-productMetaInfo')
    
    for item in product_items:
        # Extract brand
        brand_element = item.select_one('.product-brand')
        brand = brand_element.get_text(strip=True) if brand_element else 'N/A'
        
        # Extract product name
        title_element = item.select_one('.product-product')
        title = title_element.get_text(strip=True) if title_element else 'N/A'
        
        # Extract price
        price_element = item.select_one('.product-discountedPrice')
        price = f"₹{price_element.get_text(strip=True)}" if price_element else 'N/A'
        
        # Extract original price
        original_price_element = item.select_one('.product-strike')
        original_price = f"₹{original_price_element.get_text(strip=True)}" if original_price_element else None
        
        # Extract discount
        discount_element = item.select_one('.product-discountPercentage')
        discount = discount_element.get_text(strip=True) if discount_element else None
        
        # Extract rating
        rating_element = item.select_one('.product-rating')
        rating = rating_element.get_text(strip=True) if rating_element else 'N/A'
        
        # Extract reviews count
        reviews_element = item.select_one('.product-ratingsCount')
        reviews_count = reviews_element.get_text(strip=True) if reviews_element else 'N/A'
        
        # Extract image URL
        image_element = item.select_one('img.img-responsive')
        image_url = image_element.get('src') if image_element else 'N/A'
        
        # Extract product link
        link_element = item.select_one('a')
        product_link = f"https://www.myntra.com{link_element.get('href')}" if link_element and link_element.get('href') else 'N/A'
        
        # Only add if we have at least brand or title
        if brand != 'N/A' or title != 'N/A':
            product_data = {
                'title': title,
                'brand': brand,
                'price': price,
                'original_price': original_price,
                'discount': discount,
                'rating': rating,
                'reviews_count': reviews_count,
                'image_url': image_url,
                'product_link': product_link
            }
            products.append(product_data)
    
    return products


# Example usage
if __name__ == "__main__":
    search_query = "mens-tshirts"
    
    print(f"Searching for: {search_query}")
    search_url = search_myntra_product(search_query)
    print(f"URL: {search_url}\n")
    
    try:
        html_content = fetch_myntra_search_results(search_url)
        products = parse_myntra_html(html_content)
        
        print(f"Found {len(products)} products:\n")
        for i, product in enumerate(products[:5], 1):  # Show first 5
            print(f"{i}. {product['brand']} - {product['title']}")
            print(f"   Price: {product['price']}")
            if product['original_price']:
                print(f"   Original: {product['original_price']}")
            if product['discount']:
                print(f"   Discount: {product['discount']}")
            print(f"   Rating: {product['rating']} ({product['reviews_count']} reviews)")
            print(f"   Link: {product['product_link']}\n")
    except Exception as e:
        print(f"Error: {e}")