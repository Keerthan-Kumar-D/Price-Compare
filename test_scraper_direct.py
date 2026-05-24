"""
Direct test of Meesho scraper without API
"""
import sys
sys.path.append('scrappers')

try:
    from meeshoscrapper import search_meesho, MeeshoScraper
    print("✓ Successfully imported Meesho scraper")
except ImportError as e:
    print(f"✗ Failed to import scraper: {e}")
    exit(1)

print("\n" + "=" * 60)
print("Testing Meesho Scraper Directly")
print("=" * 60)
print("This will open a browser window and scrape Meesho...")
print("Query: women kurta")
print("Headless: False (visible browser)")
print("Scroll count: 2")
print("\nPlease wait 15-20 seconds...\n")

try:
    # Test with visible browser to see what's happening
    products = search_meesho("women kurta", headless=False, scroll_count=2)
    
    print("\n" + "=" * 60)
    print("RESULTS:")
    print("=" * 60)
    print(f"Total products found: {len(products)}")
    
    if products:
        print("\n✓ SUCCESS! Products were found!")
        print("\nFirst 3 products:")
        for i, product in enumerate(products[:3], 1):
            print(f"\nProduct {i}:")
            print(f"  Title: {product.get('title', 'N/A')}")
            print(f"  Price: {product.get('price', 'N/A')}")
            print(f"  Original Price: {product.get('original_price', 'N/A')}")
            print(f"  Discount: {product.get('discount', 'N/A')}")
            print(f"  Rating: {product.get('rating', 'N/A')}")
            print(f"  Reviews: {product.get('reviews_count', 'N/A')}")
            print(f"  COD: {product.get('cod_available', 'N/A')}")
            print(f"  Delivery: {product.get('delivery', 'N/A')}")
            print(f"  Link: {product.get('product_link', 'N/A')[:80]}...")
            print(f"  Image: {product.get('image_url', 'N/A')[:80]}...")
    else:
        print("\n✗ NO PRODUCTS FOUND!")
        print("\nPossible reasons:")
        print("  1. Meesho website structure changed")
        print("  2. Search returned no results for 'women kurta'")
        print("  3. Products are being filtered out")
        print("  4. Website is blocking Selenium")
        print("\nCheck the browser window to see what happened.")
        
except Exception as e:
    print(f"\n✗ ERROR: {e}")
    import traceback
    traceback.print_exc()
    print("\nCommon issues:")
    print("  1. ChromeDriver not installed: pip install webdriver-manager")
    print("  2. Chrome browser not installed")
    print("  3. Network/firewall blocking Meesho")

print("\n" + "=" * 60)
print("Test Complete!")
print("=" * 60)
