import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from flipkarScrapper import search_flipkart_product, fetch_flipkart_search_results, parse_flipkart_html

query = "tshirt"
url = search_flipkart_product(query)
html = fetch_flipkart_search_results(url)
products = parse_flipkart_html(html)

print(f"Found {len(products)} products for '{query}'\n")

for i, p in enumerate(products[:3], 1):
    print(f"Product {i}:")
    print(f"  Title: {p['title'][:80]}")
    print(f"  Price: {p['price']}")
    print(f"  Image: {p['image_url'][:100] if p['image_url'] else 'None'}")
    print(f"  Link: {p['product_link'][:100] if p['product_link'] else 'None'}")
    print()
