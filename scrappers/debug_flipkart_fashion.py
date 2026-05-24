from bs4 import BeautifulSoup
import requests
import re

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "en-IN,en;q=0.9",
}

url = "https://www.flipkart.com/search?q=tshirt"
r = requests.get(url, headers=headers, timeout=10)
soup = BeautifulSoup(r.text, 'html.parser')

# Find price-based anchors
price_texts = soup.find_all(string=re.compile(r'₹\s*[0-9]'))
print(f"Found {len(price_texts)} price text nodes")

anchors = []
for pt in price_texts[:5]:  # Check first 5
    parent = pt.parent
    for _ in range(6):
        if parent is None:
            break
        if parent.name == 'a' and parent.get('href'):
            print(f"\n=== Product Anchor ===")
            print(f"Href: {parent.get('href')[:80]}")
            
            # Check title attribute
            print(f"Title attr: {parent.get('title') or 'None'}")
            
            # Check for images
            imgs = parent.find_all('img')
            print(f"Images in anchor: {len(imgs)}")
            if imgs:
                for i, img in enumerate(imgs[:2]):
                    print(f"  Img {i+1} src: {img.get('src', 'None')[:80]}")
                    print(f"  Img {i+1} data-src: {img.get('data-src', 'None')[:80]}")
                    print(f"  Img {i+1} alt: {img.get('alt', 'None')[:80]}")
            
            # Check parent for images
            if parent.parent:
                nearby_imgs = parent.parent.find_all('img', recursive=False)
                if nearby_imgs:
                    print(f"Images near anchor: {len(nearby_imgs)}")
            
            # Look for container with class
            cont = parent
            for _ in range(4):
                if cont.parent and cont.parent.name in ['div', 'li']:
                    if cont.parent.get('class'):
                        print(f"Container classes: {cont.parent.get('class')}")
                        container_imgs = cont.parent.find_all('img')
                        print(f"Images in container: {len(container_imgs)}")
                        if container_imgs:
                            img = container_imgs[0]
                            print(f"  Container img src: {img.get('src', 'None')[:80]}")
                            print(f"  Container img alt: {img.get('alt', 'None')[:80]}")
                        break
                cont = cont.parent
                if cont is None:
                    break
            
            break
        parent = parent.parent
