import requests
from bs4 import BeautifulSoup
import re

# Fetch one product page directly
product_url = "https://www.flipkart.com/celsius-typography-men-round-neck-multicolor-t-shirt/p/itm55c3c0e93d76c?pid=TSHGKGN7WQYWCQHG"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

print(f"Fetching product page: {product_url}\n")
resp = requests.get(product_url, headers=headers, timeout=10)

soup = BeautifulSoup(resp.content, 'html.parser')

# Find all image sources
print("=== Looking for image URLs ===\n")

# Check img tags
imgs = soup.find_all('img')
print(f"Found {len(imgs)} img tags\n")

product_imgs = []
for img in imgs[:15]:  # Check first 15
    src = img.get('src') or img.get('data-src')
    if src and 'rukminim' in src:
        print(f"Image src: {src}")
        product_imgs.append(src)

# Check JSON-LD
print("\n=== Checking JSON-LD ===\n")
scripts = soup.find_all('script', type='application/ld+json')
for i, script in enumerate(scripts[:2]):
    import json
    try:
        data = json.loads(script.string)
        if 'image' in str(data):
            print(f"Script {i+1} contains 'image' field:")
            print(json.dumps(data, indent=2)[:500])
    except:
        pass
