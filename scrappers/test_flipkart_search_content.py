import requests
from flipkarScrapper import search_flipkart_product, headers

url = search_flipkart_product('tshirt')
r = requests.get(url, headers=headers, timeout=10)
text = r.text
print('length', len(text))
idx = text.find('₹')
if idx!=-1:
    print('Found ₹ at', idx)
    print(text[idx-200:idx+200])
else:
    print('No rupee symbol found in HTML')

# look for product-card-like attributes
for token in ['data-id','data-product','_2kHMtA','_1YokD2','product','_1ocjZg']:
    print(token, token in text)
