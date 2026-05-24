from bs4 import BeautifulSoup
import requests

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "en-IN,en;q=0.9",
}

url = "https://www.flipkart.com/search?q=tshirt"
r = requests.get(url, headers=headers, timeout=10)
soup = BeautifulSoup(r.text, 'html.parser')

# Find a product container
containers = soup.select('div.p0C73x')
print(f"Found {len(containers)} product containers with class p0C73x")

if containers:
    cont = containers[0]
    print("\n=== First Product Container ===")
    print(cont.prettify()[:2000])
    
    # Look for all anchor tags
    anchors = cont.find_all('a')
    print(f"\n\nFound {len(anchors)} anchors in container")
    for i, a in enumerate(anchors):
        print(f"\nAnchor {i+1}:")
        print(f"  href: {a.get('href', 'None')[:100]}")
        print(f"  text: {a.get_text(strip=True)[:80]}")
        print(f"  title attr: {a.get('title', 'None')[:80]}")
        
    # Look for images
    imgs = cont.find_all('img')
    print(f"\n\nFound {len(imgs)} images in container")
    for i, img in enumerate(imgs):
        print(f"\nImage {i+1}:")
        print(f"  src: {img.get('src', 'None')[:80]}")
        print(f"  data-src: {img.get('data-src', 'None')[:80]}")
        print(f"  alt: {img.get('alt', 'None')[:80]}")
        print(f"  parent tag: {img.parent.name if img.parent else 'None'}")
