from bs4 import BeautifulSoup
import requests
import json
import re

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "en-IN,en;q=0.9",
}

url = "https://www.flipkart.com/search?q=tshirt"
r = requests.get(url, headers=headers, timeout=10)
soup = BeautifulSoup(r.text, 'html.parser')

# Look for JSON data in script tags
scripts = soup.find_all('script', type='application/ld+json')
print(f"Found {len(scripts)} JSON-LD scripts")

for i, script in enumerate(scripts[:2]):
    try:
        data = json.loads(script.string)
        if 'itemListElement' in data:
            items = data['itemListElement']
            print(f"\nScript {i+1} has {len(items)} items")
            if items:
                item = items[0]
                print("First item:", json.dumps(item, indent=2)[:500])
    except:
        pass

# Look for data attributes with images
cont = soup.select_one('div.p0C73x')
if cont:
    print("\n\n=== Checking first product container for image data ===")
    # Check all elements for data-* attributes
    for elem in cont.find_all(True):
        attrs = elem.attrs
        for attr, val in attrs.items():
            if 'image' in attr.lower() or 'img' in attr.lower() or 'src' in attr.lower():
                print(f"{elem.name}.{attr}: {str(val)[:100]}")
