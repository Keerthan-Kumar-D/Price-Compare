from bs4 import BeautifulSoup
from flipkarScrapper import search_flipkart_product, headers
import requests

selectors = ['a._2rpwqI', 'a.IRpwTa', 'a.s1Q9rs', 'a._2fZ6oW', 'a._2UzuFa',
             'a._3dqZjq', 'a._2r_T1I', 'a._2kHMtA', 'a._1fQZEK', 'a.CGtC98']

url = search_flipkart_product('tshirt')
r = requests.get(url, headers=headers, timeout=10)
soup = BeautifulSoup(r.text, 'html.parser')
print('Total anchors:', len(soup.find_all('a')))
for sel in selectors:
    found = soup.select(sel)
    print(sel, len(found))
    if found:
        print('Example href:', found[0].get('href')[:120])

# Check for product-card containers
containers = ['div._2kHMtA', 'div._1xHGtK', 'div._4ddWXP', 'div._1NoI8_','div._1AtVbE']
for c in containers:
    elems = soup.select(c)
    print(c, len(elems))
    if elems:
        el = elems[0]
        a = el.select_one('a')
        print('  example anchor:', a.get('href')[:120] if a else 'no anchor')

# Print first 800 chars of body where product grid often is
body = r.text
start = body.find('<div class="_1YokD2"')
if start!=-1:
    print('\nSnippet around _1YokD2:')
    print(body[start:start+1000])
else:
    print('\n_no _1YokD2 container found_')
