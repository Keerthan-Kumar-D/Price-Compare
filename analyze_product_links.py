from bs4 import BeautifulSoup

with open('meesho_page_full.html', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

# Find links that contain product info
print("Looking for product links patterns...")
all_links = soup.find_all('a')
product_patterns = []

for link in all_links:
    href = link.get('href', '')
    if '/product' in href.lower():
        product_patterns.append(href)

print(f'\nFound {len(product_patterns)} links with "/product"')
for i, pattern in enumerate(product_patterns[:10], 1):
    print(f'{i}. {pattern}')

# Find parent containers of product images
print('\n\nFinding parent containers of product images...')
images = soup.find_all('img', src=lambda x: x and 'meesho.com/images/products' in x)
for i, img in enumerate(images[:3], 1):
    print(f'\n--- Product {i} ---')
    print(f'Image: {img.get("src", "N/A")[:60]}...')
    
    # Get parent link
    parent_a = img.find_parent('a')
    if parent_a:
        href = parent_a.get('href', 'N/A')
        print(f'Parent link: {href[:80]}')
        print(f'Link text: {parent_a.get_text(strip=True)[:100]}')
