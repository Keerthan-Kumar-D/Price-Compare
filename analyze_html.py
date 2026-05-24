from bs4 import BeautifulSoup

# Read the saved HTML
with open('meesho_page_full.html', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

# Check all links
links = soup.find_all('a')
print(f'Total links found: {len(links)}')
print('\nFirst 15 links:')
for i, link in enumerate(links[:15], 1):
    href = link.get('href', 'N/A')
    text = link.get_text(strip=True)[:40]
    print(f'{i}. {href[:70]} - {text}')

# Look for product-related structures
print('\n\nLooking for divs with "product" in class:')
product_divs = soup.find_all('div', class_=lambda x: x and 'product' in x.lower())
print(f'Found {len(product_divs)} divs with "product" in class')

# Look for images from Meesho CDN
print('\n\nLooking for product images:')
images = soup.find_all('img', src=lambda x: x and 'meesho.com/images/products' in x)
print(f'Found {len(images)} product images')
for i, img in enumerate(images[:5], 1):
    print(f'{i}. {img.get("src", "N/A")[:80]}')
