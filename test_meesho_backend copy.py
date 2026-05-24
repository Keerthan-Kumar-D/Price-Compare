"""
Quick test to verify Meesho backend is working
"""
try:
    import requests
except ImportError:
    print("✗ 'requests' library not installed!")
    print("Install it with: pip install requests")
    exit(1)

import json

# First check if server is running
print("Checking if backend server is running...")
print("=" * 60)

try:
    health_response = requests.get("http://localhost:8000/health", timeout=5)
    if health_response.status_code == 200:
        print("✓ Backend server is running!")
        print(f"  Status: {health_response.json()}")
    else:
        print(f"✗ Server responded with status: {health_response.status_code}")
except requests.exceptions.ConnectionError:
    print("✗ Cannot connect to backend server!")
    print("  Make sure the server is running:")
    print("  cd 'c:\\Users\\keert\\Desktop\\price Compare - Copy'")
    print("  python app.py")
    exit(1)
except Exception as e:
    print(f"✗ Error checking server: {e}")
    exit(1)

print("\n" + "=" * 60)
print("Testing Meesho endpoint...")
print("=" * 60)
print("This will take 10-20 seconds (Selenium scraping)...")

try:
    response = requests.get(
        "http://localhost:8000/api/scrape/meesho",
        params={
            "query": "women kurta",
            "limit": 3,
            "scroll_count": 2
        },
        timeout=60
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Status: {data.get('status')}")
        print(f"✓ Total products: {data.get('total_products')}")
        print(f"✓ Platform: {data.get('platform')}")
        
        if data.get('products'):
            print("\n✓ SUCCESS! Meesho returned products!")
            print(f"\nFirst product:")
            product = data['products'][0]
            print(f"  Title: {product.get('title')}")
            print(f"  Price: {product.get('price')}")
            print(f"  Original Price: {product.get('original_price')}")
            print(f"  Discount: {product.get('discount')}")
            print(f"  Rating: {product.get('rating')}")
            print(f"  Link: {product.get('product_link', 'N/A')[:80]}...")
            print(f"  Image: {product.get('image_url', 'N/A')[:80]}...")
            print(f"  COD: {product.get('cod_available')}")
        else:
            print("\n✗ No products returned")
            print(f"Message: {data.get('message')}")
            print("\nFull response:")
            print(json.dumps(data, indent=2))
    else:
        print(f"✗ Error: {response.status_code}")
        print("Response:")
        print(response.text)
        
except requests.exceptions.Timeout:
    print("✗ Request timed out (took longer than 60 seconds)")
    print("This might mean:")
    print("  - Meesho website is slow")
    print("  - ChromeDriver is not installed")
    print("  - Network issues")
except requests.exceptions.ConnectionError:
    print("✗ Cannot connect to backend!")
    print("Make sure backend is running on port 8000")
        
except Exception as e:
    print(f"✗ Failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("Testing /api/scrape/all endpoint...")
print("=" * 60)
print("This will take 30-60 seconds (scraping all platforms)...")

try:
    response = requests.get(
        "http://localhost:8000/api/scrape/all",
        params={
            "query": "women kurta",
            "limit": 3
        },
        timeout=120
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Total products found: {data.get('total_products_found')}")
        
        # Check all platforms
        platforms = data.get('platforms', {})
        for platform_name, platform_data in platforms.items():
            status = platform_data.get('status')
            count = platform_data.get('total_products')
            print(f"  {platform_name.title()}: {count} products ({status})")
        
        # Check Meesho specifically
        meesho = platforms.get('meesho', {})
        print(f"\n{'='*60}")
        print(f"Meesho Details:")
        print(f"  Status: {meesho.get('status')}")
        print(f"  Products: {meesho.get('total_products')}")
        
        if meesho.get('products'):
            print(f"  ✓ Meesho is returning products in /all endpoint!")
            print(f"\n  First product:")
            product = meesho['products'][0]
            print(f"    Title: {product.get('title')}")
            print(f"    Price: {product.get('price')}")
            print(f"    Link: {product.get('product_link', 'N/A')[:80]}...")
        else:
            print(f"  ✗ Meesho returned 0 products")
            if meesho.get('message'):
                print(f"  Message: {meesho.get('message')}")
            print(f"\n  Full Meesho response:")
            print(f"  {json.dumps(meesho, indent=4)}")
    else:
        print(f"✗ Error: {response.status_code}")
        print(response.text)
        
except requests.exceptions.Timeout:
    print("✗ Request timed out (took longer than 120 seconds)")
except requests.exceptions.ConnectionError:
    print("✗ Cannot connect to backend!")
except Exception as e:
    print(f"✗ Failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("Test complete!")
print("=" * 60)
