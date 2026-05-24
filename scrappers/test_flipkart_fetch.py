import requests
from flipkarScrapper import search_flipkart_product, headers

queries = ["tshirt", "laptop"]

for q in queries:
    url = search_flipkart_product(q)
    print(f"Testing: {q} -> {url}")
    try:
        r = requests.get(url, headers=headers, timeout=10)
        print("Status:", r.status_code)
        print(r.text[:800])
    except Exception as e:
        print("Error fetching:", e)
