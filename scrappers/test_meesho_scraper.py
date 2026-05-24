"""
Test script for Meesho scraper
Run this to test the scraper functionality
"""

from meeshoscrapper import MeeshoScraper, search_meesho
import json


def test_basic_search():
    """Test basic search functionality"""
    print("=" * 80)
    print("TEST 1: Basic Search Test")
    print("=" * 80)
    
    search_query = "women kurta"
    print(f"\nSearching for: '{search_query}'")
    
    try:
        products = search_meesho(search_query, headless=False, scroll_count=2)
        
        print(f"\n✓ Successfully scraped {len(products)} products")
        
        if products:
            print("\n" + "-" * 80)
            print("Sample Products (First 3):")
            print("-" * 80)
            
            for i, product in enumerate(products[:3], 1):
                print(f"\nProduct {i}:")
                print(f"  Title: {product['title']}")
                print(f"  Price: {product['price']}")
                if product['original_price']:
                    print(f"  Original Price: {product['original_price']}")
                if product['discount']:
                    print(f"  Discount: {product['discount']}")
                if product['rating']:
                    print(f"  Rating: {product['rating']}")
                if product['reviews_count']:
                    print(f"  Reviews: {product['reviews_count']}")
                if product['delivery']:
                    print(f"  Delivery: {product['delivery']}")
                if product['cod_available']:
                    print(f"  COD: {product['cod_available']}")
                if product['product_link']:
                    print(f"  Link: {product['product_link'][:80]}...")
                print()
            
            return True
        else:
            print("\n✗ No products found")
            return False
            
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        return False


def test_multiple_searches():
    """Test multiple search queries"""
    print("\n" + "=" * 80)
    print("TEST 2: Multiple Search Queries Test")
    print("=" * 80)
    
    search_queries = ["saree", "men shirt", "shoes"]
    
    results = {}
    
    for query in search_queries:
        print(f"\nSearching for: '{query}'")
        try:
            products = search_meesho(query, headless=True, scroll_count=1)
            results[query] = len(products)
            print(f"  ✓ Found {len(products)} products")
        except Exception as e:
            print(f"  ✗ Error: {e}")
            results[query] = 0
    
    print("\n" + "-" * 80)
    print("Summary:")
    print("-" * 80)
    for query, count in results.items():
        print(f"  {query}: {count} products")
    
    return all(count > 0 for count in results.values())


def test_context_manager():
    """Test using scraper with context manager"""
    print("\n" + "=" * 80)
    print("TEST 3: Context Manager Test")
    print("=" * 80)
    
    try:
        with MeeshoScraper(headless=True) as scraper:
            products = scraper.scrape("mobile cover", scroll_count=1)
            print(f"\n✓ Context manager worked correctly")
            print(f"  Found {len(products)} products")
            return len(products) > 0
    except Exception as e:
        print(f"\n✗ Context manager test failed: {e}")
        return False


def test_data_export():
    """Test exporting data to JSON"""
    print("\n" + "=" * 80)
    print("TEST 4: Data Export Test")
    print("=" * 80)
    
    try:
        products = search_meesho("backpack", headless=True, scroll_count=1)
        
        # Export to JSON
        output_file = "meesho_products_test.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(products, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ Successfully exported {len(products)} products to {output_file}")
        return True
        
    except Exception as e:
        print(f"\n✗ Export test failed: {e}")
        return False


def test_edge_cases():
    """Test edge cases"""
    print("\n" + "=" * 80)
    print("TEST 5: Edge Cases Test")
    print("=" * 80)
    
    test_cases = [
        ("xyz123impossible", "Non-existent product"),
        ("     ", "Empty/whitespace query"),
        ("a", "Single character query"),
    ]
    
    for query, description in test_cases:
        print(f"\nTesting: {description} ('{query}')")
        try:
            products = search_meesho(query, headless=True, scroll_count=1)
            print(f"  ✓ Handled gracefully, found {len(products)} products")
        except Exception as e:
            print(f"  ! Exception raised: {e}")


def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("MEESHO SCRAPER TEST SUITE")
    print("=" * 80)
    
    tests = [
        ("Basic Search", test_basic_search),
        ("Multiple Searches", test_multiple_searches),
        ("Context Manager", test_context_manager),
        ("Data Export", test_data_export),
        ("Edge Cases", test_edge_cases),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = result if result is not None else True
        except Exception as e:
            print(f"\n✗ {test_name} crashed: {e}")
            results[test_name] = False
    
    # Print summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    for test_name, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{status}: {test_name}")
    
    total_tests = len(results)
    passed_tests = sum(1 for v in results.values() if v)
    
    print("\n" + "-" * 80)
    print(f"Total: {passed_tests}/{total_tests} tests passed")
    print("=" * 80)


if __name__ == "__main__":
    # You can run individual tests or all tests
    
    # Run all tests
    run_all_tests()
    
    # Or run individual test
    # test_basic_search()
