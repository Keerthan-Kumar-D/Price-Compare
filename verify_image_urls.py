import requests

test_urls = [
    "https://rukminim2.flixcart.com/image/312/312/xif0q/TSHGKGN7WQYWCQHG.jpg",
    "https://rukminim2.flixcart.com/image/312/312/xif0q/TSHHAM86EZREVJZZ.jpg"
]

for url in test_urls:
    try:
        resp = requests.head(url, timeout=5)
        print(f"\n{url}")
        print(f"Status: {resp.status_code}")
        print(f"Content-Type: {resp.headers.get('Content-Type', 'N/A')}")
        if resp.status_code == 200:
            print("✓ Image exists and is accessible!")
        else:
            print("✗ Image URL returned error")
    except Exception as e:
        print(f"\n{url}")
        print(f"✗ Error: {e}")
