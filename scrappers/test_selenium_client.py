"""
Test client for Myntra Selenium Scraper Server
Run the myntra_selenium_server.py first, then run this file
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_health():
    """Test if server is running"""
    print("\n" + "="*60)
    print("Testing Server Health...")
    print("="*60)
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✓ Server is running!")
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"✗ Server responded with status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ Could not connect to server. Make sure myntra_selenium_server.py is running!")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_search(query):
    """Test search functionality"""
    print("\n" + "="*60)
    print(f"Testing Search for: {query}")
    print("="*60)
    
    try:
        print("\nSending request... (This may take 20-30 seconds)")
        start_time = time.time()
        
        response = requests.get(
            f"{BASE_URL}/search",
            params={"q": query},
            timeout=120  # 2 minutes timeout for Selenium scraping
        )
        
        elapsed = time.time() - start_time
        print(f"✓ Response received in {elapsed:.2f} seconds")
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"\n{'='*60}")
            print(f"SEARCH RESULTS")
            print(f"{'='*60}")
            print(f"Query: {data.get('query', 'N/A')}")
            print(f"Products Found: {data.get('count', 0)}")
            
            products = data.get('products', [])
            
            if products:
                print(f"\n{'='*60}")
                print("PRODUCT DETAILS:")
                print(f"{'='*60}\n")
                
                for i, product in enumerate(products[:5], 1):  # Show first 5
                    print(f"{i}. BRAND: {product.get('brand', 'N/A')}")
                    print(f"   TITLE: {product.get('title', 'N/A')}")
                    print(f"   PRICE: {product.get('price', 'N/A')}")
                    
                    if product.get('original_price'):
                        print(f"   ORIGINAL PRICE: {product['original_price']}")
                    
                    if product.get('discount'):
                        print(f"   DISCOUNT: {product['discount']}")
                    
                    print(f"   RATING: {product.get('rating', 'N/A')}")
                    print(f"   REVIEWS: {product.get('reviews_count', 'N/A')}")
                    print(f"   LINK: {product.get('product_link', 'N/A')}")
                    
                    if i < 5 and i < len(products):
                        print(f"   {'-' * 55}")
                
                # Save to JSON
                output_file = f"selenium_{query.replace(' ', '_')}_results.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                print(f"\n{'='*60}")
                print(f"✓ Full results saved to: {output_file}")
                print(f"{'='*60}")
            else:
                print("\n⚠ No products found in response")
                
        else:
            print(f"\n✗ Error response (Status {response.status_code}):")
            try:
                error_data = response.json()
                print(json.dumps(error_data, indent=2))
            except:
                print(response.text)
    
    except requests.exceptions.Timeout:
        print("✗ Request timed out. Scraping took too long.")
    except requests.exceptions.ConnectionError:
        print("✗ Could not connect to server. Make sure myntra_selenium_server.py is running!")
    except Exception as e:
        print(f"✗ Error: {e}")

def main():
    print("\n" + "="*60)
    print("🧪 MYNTRA SELENIUM SCRAPER TEST CLIENT")
    print("="*60)
    
    # First check if server is running
    if not test_health():
        print("\n⚠ Please start the server first:")
        print("   python myntra_selenium_server.py")
        return
    
    # Test searches
    test_queries = [
        "mens-tshirts",
        # "women-dresses",
        # "shoes"
    ]
    
    for query in test_queries:
        test_search(query)
        print("\n" * 2)

if __name__ == "__main__":
    main()
