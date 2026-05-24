import requests
from bs4 import BeautifulSoup
import json

url = "https://www.flipkart.com/search?q=tshirt"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

resp = requests.get(url, headers=headers, timeout=10)
soup = BeautifulSoup(resp.content, 'html.parser')

print("=== Checking for JSON-LD with Product type ===\n")
scripts = soup.find_all('script', type='application/ld+json')
print(f"Found {len(scripts)} JSON-LD scripts\n")

for i, script in enumerate(scripts):
    try:
        data = json.loads(script.string)
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict) and item.get('@type') == 'Product':
                    print(f"Script {i+1} has Product with image:")
                    print(f"Name: {item.get('name', 'N/A')}")
                    print(f"Image: {item.get('image', 'N/A')}\n")
                    break
    except:
        continue
