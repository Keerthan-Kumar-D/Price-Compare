from scrappers.meeshoscrapper_fixed import search_meesho

print("Testing headless Meesho scraper...")
products = search_meesho('women kurta', headless=True, scroll_count=2)

print(f"\n{'='*60}")
print(f"Found {len(products)} products")
print(f"{'='*60}\n")

for i, p in enumerate(products[:5], 1):
    print(f"{i}. {p.get('title', 'N/A')[:50]}")
    print(f"   Price: {p.get('price', 'N/A')}")
    print(f"   Link: {p.get('product_link', 'N/A')[:60]}...")
    print()
