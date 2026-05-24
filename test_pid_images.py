import sys
sys.path.append('scrappers')
from flipkarScrapper import search_flipkart_product, fetch_flipkart_search_results, parse_flipkart_html

print("Testing PID-based image URLs for fashion products...")
search_url = search_flipkart_product('tshirt')
html = fetch_flipkart_search_results(search_url)
products = parse_flipkart_html(html)

print(f"\nFound {len(products)} products:")
for i, product in enumerate(products[:5], 1):
    print(f"\nProduct {i}:")
    print(f"Title: {product['title']}")
    print(f"Price: {product['price']}")
    print(f"Image: {product.get('image_url', 'None')}")
    if product.get('product_link'):
        print(f"Link: {product['product_link'][:80]}...")
