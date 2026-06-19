#!/usr/bin/env python3
"""Test all scrapers to verify they can find products"""

import scrappers.amazonScrapper as amazon

def test_amazon():
    print("\n" + "="*60)
    print("Testing Amazon Scraper")
    print("="*60)
    
    search_url = amazon.search_amazon_product('laptop')
    print(f"Testing Amazon with URL: {search_url}")
    
    html = amazon.fetch_amazon_search_results(search_url)
    if html:
        products = amazon.parse_amazon_html(html)
        print(f"Found {len(products)} products")
        if products:
            for i, p in enumerate(products[:3], 1):
                print(f"{i}. {p.get('title', 'N/A')[:60]} - {p.get('price', 'N/A')}")
        return len(products) > 0
    else:
        print("Failed to fetch HTML")
        return False

if __name__ == "__main__":
    test_amazon()
