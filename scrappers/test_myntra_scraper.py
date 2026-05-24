"""
Test script for Myntra scraper
Save the myntra_scraper.py in the same directory and run this file
"""

from myntrascrapper import search_myntra_product, fetch_myntra_search_results, parse_myntra_html
import json

def test_scraper(search_query):
    """Test the Myntra scraper with a search query"""
    print(f"=" * 60)
    print(f"Searching Myntra for: {search_query}")
    print(f"=" * 60)
    
    # Generate search URL
    search_url = search_myntra_product(search_query)
    print(f"\nSearch URL: {search_url}\n")
    
    try:
        # Fetch the page
        print("Fetching page content...")
        html_content = fetch_myntra_search_results(search_url)
        print(f"✓ Page fetched successfully ({len(html_content)} characters)\n")
        
        # Parse the HTML
        print("Parsing products...")
        products = parse_myntra_html(html_content)
        print(f"✓ Found {len(products)} products\n")
        
        if products:
            print("=" * 60)
            print("PRODUCT RESULTS:")
            print("=" * 60)
            
            for i, product in enumerate(products[:10], 1):  # Show first 10
                print(f"\n{i}. BRAND: {product['brand']}")
                print(f"   TITLE: {product['title']}")
                print(f"   PRICE: {product['price']}")
                
                if product.get('original_price'):
                    print(f"   ORIGINAL PRICE: {product['original_price']}")
                
                if product.get('discount'):
                    print(f"   DISCOUNT: {product['discount']}")
                
                print(f"   RATING: {product['rating']}")
                print(f"   REVIEWS: {product['reviews_count']}")
                print(f"   LINK: {product['product_link']}")
                
                if i < 10 and i < len(products):
                    print(f"   {'-' * 55}")
            
            # Save to JSON file
            output_file = f"{search_query.replace(' ', '_')}_results.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(products, f, indent=2, ensure_ascii=False)
            print(f"\n{'=' * 60}")
            print(f"✓ Results saved to: {output_file}")
            print(f"{'=' * 60}")
            
        else:
            print("⚠ No products found. This could mean:")
            print("   - Myntra's page structure has changed")
            print("   - The search query returned no results")
            print("   - JavaScript rendering is required (try Selenium)")
            
    except Exception as e:
        print(f"✗ Error occurred: {e}")
        print(f"\nTroubleshooting tips:")
        print("   1. Check your internet connection")
        print("   2. Verify the search query is valid")
        print("   3. Myntra might be blocking requests (try Selenium)")
        print("   4. The website structure may have changed")


if __name__ == "__main__":
    # Test with different queries
    test_queries = [
        "mens-tshirts",
        "women-dresses",
        "shoes"
    ]
    
    # Run first query by default
    test_scraper(test_queries[0])
    
    # Uncomment to test multiple queries:
    # for query in test_queries:
    #     test_scraper(query)
    #     print("\n" * 3)
