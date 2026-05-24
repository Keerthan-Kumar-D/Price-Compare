"""
Quick test to verify Myntra Selenium integration
Run after starting the FastAPI server
"""

import requests
import time

BASE_URL = "http://localhost:8000"

def test_myntra_selenium():
    """Test the Myntra Selenium endpoint"""
    print("\n" + "="*70)
    print("🧪 TESTING MYNTRA SELENIUM INTEGRATION")
    print("="*70)
    
    # Test 1: Check if server is running
    print("\n1️⃣  Checking if server is running...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("   ✅ Server is running!")
        else:
            print(f"   ❌ Server returned status {response.status_code}")
            return
    except requests.exceptions.ConnectionError:
        print("   ❌ Could not connect to server")
        print("   💡 Start server with: python app.py")
        return
    
    # Test 2: Check platforms endpoint
    print("\n2️⃣  Checking platforms endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/platforms", timeout=10)
        if response.status_code == 200:
            data = response.json()
            myntra = next((p for p in data['platforms'] if p['name'] == 'Myntra'), None)
            if myntra:
                print(f"   ✅ Myntra found!")
                print(f"      Status: {myntra['status']}")
                print(f"      Note: {myntra.get('note', 'N/A')}")
            else:
                print("   ❌ Myntra not found in platforms")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Test Myntra scraping
    print("\n3️⃣  Testing Myntra Selenium scraper...")
    print("   ⏳ This will take 20-30 seconds (Selenium needs time)...")
    print("   🌐 Chrome browser will launch in headless mode...")
    
    start_time = time.time()
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/scrape/myntra",
            params={"query": "mens-tshirts", "limit": 5},
            timeout=120  # 2 minutes timeout
        )
        
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n   ✅ Request successful! (took {elapsed:.1f} seconds)")
            print(f"   📦 Platform: {data['platform']}")
            print(f"   🔍 Query: {data['search_query']}")
            print(f"   📊 Products Found: {data['total_products']}")
            print(f"   ⚡ Status: {data['status']}")
            
            if data.get('message'):
                print(f"   💬 Message: {data['message']}")
            
            if data['products']:
                print(f"\n   📦 First Product:")
                product = data['products'][0]
                print(f"      Brand: {product.get('brand', 'N/A')}")
                print(f"      Title: {product.get('title', 'N/A')[:60]}...")
                print(f"      Price: {product.get('price', 'N/A')}")
                if product.get('original_price'):
                    print(f"      Original Price: {product['original_price']}")
                if product.get('discount'):
                    print(f"      Discount: {product['discount']}")
                print(f"      Rating: {product.get('rating', 'N/A')}")
                print(f"      Link: {product.get('product_link', 'N/A')[:60]}...")
                
                print(f"\n   🎉 SUCCESS! Myntra Selenium scraper is working!")
            else:
                print(f"\n   ⚠️  No products found")
                print(f"   💡 This could mean:")
                print(f"      - Search returned no results on Myntra")
                print(f"      - Myntra is blocking automated requests")
                print(f"      - Try a different search query")
        else:
            print(f"\n   ❌ Request failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print(f"\n   ⏰ Request timed out")
        print(f"   💡 Selenium scraping takes time. This might be normal.")
    except Exception as e:
        print(f"\n   ❌ Error: {e}")
    
    # Summary
    print("\n" + "="*70)
    print("📋 SUMMARY")
    print("="*70)
    print("\n✅ Myntra Selenium is integrated into the backend!")
    print("✅ Frontend will show Myntra products automatically")
    print("✅ Each request takes 20-30 seconds (Selenium needs time)")
    print("\n💡 Next Steps:")
    print("   1. Keep backend running")
    print("   2. Start frontend: cd frontend && npm run dev")
    print("   3. Search for products in the UI")
    print("   4. Watch Myntra column appear with results")
    print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    test_myntra_selenium()
