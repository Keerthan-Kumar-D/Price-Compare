import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from scrappers.flipkart_selenium import search_flipkart_selenium

print("Testing Flipkart Selenium scraper with laptop...")
products = search_flipkart_selenium('laptop')

print(f"\nFound {len(products)} products:")
for i, p in enumerate(products[:5], 1):
    print(f"\n{i}. {p['title'][:60]}...")
    print(f"   Price: {p.get('price', 'N/A')}")
    print(f"   Image: {'✓ Yes' if p.get('image_url') else '✗ No'}")
    if p.get('image_url'):
        print(f"   URL: {p['image_url'][:70]}...")
