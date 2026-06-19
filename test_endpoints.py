#!/usr/bin/env python3
"""Test API endpoints for Flipkart and Meesho"""

import scrappers.flipkarScrapper as flipkart
from scrappers.meeshoscrapper import search_meesho

def test_flipkart_limit():
    print("\n" + "="*60)
    print("Testing Flipkart Limit (should return 5 products)")
    print("="*60)
    
    search_url = flipkart.search_flipkart_product('laptop')
    html_content = flipkart.fetch_flipkart_search_results(search_url)
    products_data = flipkart.parse_flipkart_html(html_content)
    
    print(f"Total products scraped: {len(products_data)}")
    
    # Simulate limit of 5
    limited = products_data[:5]
    print(f"After applying limit=5: {len(limited)}")
    
    for i, p in enumerate(limited, 1):
        print(f"{i}. {p.get('title', 'N/A')[:60]} - {p.get('price', 'N/A')}")

def test_meesho():
    print("\n" + "="*60)
    print("Testing Meesho (should return products)")
    print("="*60)
    
    products_data = search_meesho('women kurta', headless=True, scroll_count=1)
    
    print(f"Total products found: {len(products_data)}")
    
    if products_data:
        for i, p in enumerate(products_data[:5], 1):
            print(f"{i}. {p.get('title', 'N/A')[:60]} - {p.get('price', 'N/A')}")
    else:
        print("No products found!")

if __name__ == "__main__":
    test_flipkart_limit()
    test_meesho()
