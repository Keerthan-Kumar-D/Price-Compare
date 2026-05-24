import requests
import json

# Test Flipkart fashion search
url = "http://localhost:8000/api/scrape/flipkart?query=tshirt&limit=5"

print("Testing Flipkart fashion search...")
print(f"URL: {url}\n")

response = requests.get(url, timeout=60)

if response.status_code == 200:
    data = response.json()
    print(f"✓ Success!")
    print(f"Platform: {data['platform']}")
    print(f"Total products: {data['total_products']}")
    print(f"\nProducts:")
    
    for i, product in enumerate(data['products'], 1):
        print(f"\nProduct {i}:")
        print(f"  Title: {product['title'][:60]}...")
        print(f"  Price: {product['price']}")
        print(f"  Image: {product['image_url'][:80] if product.get('image_url') else 'None'}...")
        print(f"  Has Image: {'✓ YES' if product.get('image_url') else '✗ NO'}")
else:
    print(f"✗ Error: {response.status_code}")
    print(response.text)
