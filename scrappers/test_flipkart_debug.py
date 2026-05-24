from bs4 import BeautifulSoup
from flipkarScrapper import search_flipkart_product, headers
import requests

url = search_flipkart_product('tshirt')
r = requests.get(url, headers=headers, timeout=10)
soup = BeautifulSoup(r.text, 'html.parser')
price_texts = soup.find_all(text=True)

for t in price_texts:
    if '38% off' in t:
        el = t.parent
        print('FOUND text in element:', el.name, el.get('class'))
        # climb to nearest product anchor
        p = el
        for _ in range(6):
            if p is None:
                break
            if p.name == 'a' and p.get('href'):
                print('\n--- Anchor HTML ---')
                print(str(p)[:2000])
                raise SystemExit
            p = p.parent
print('not found')
