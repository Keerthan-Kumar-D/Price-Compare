from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time

options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

try:
    driver.get("https://www.flipkart.com/search?q=laptop")
    time.sleep(5)
    
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    
    containers = soup.find_all('div', {'data-id': True})
    print(f"Found {len(containers)} containers with data-id\n")
    
    if containers:
        first = containers[0]
        print("=== First Container ===")
        print(f"data-id: {first.get('data-id')}")
        
        # Look for title div/span
        divs_with_class = first.find_all(['div', 'span'], class_=True)
        print(f"\nFound {len(divs_with_class)} divs/spans with classes")
        
        # Find potential title elements (short text, no rupee, reasonable length)
        print("\n=== Potential Title Elements ===")
        for elem in divs_with_class[:15]:
            text = elem.get_text(strip=True)
            classes = ' '.join(elem.get('class', []))
            if 10 < len(text) < 150 and '₹' not in text:
                print(f"\nClass: {classes[:40]}")
                print(f"Text: {text[:80]}...")
        
        # Find all anchors
        anchors = first.find_all('a')
        print(f"\n\n=== Found {len(anchors)} anchors in first container ===")
        
        for i, a in enumerate(anchors[:3], 1):
            href = a.get('href', '')
            title_attr = a.get('title', '')
            text = a.get_text(strip=True)
            print(f"\nAnchor {i}:")
            print(f"  href: {href[:60]}...")
            print(f"  title attr: {title_attr[:60] if title_attr else 'None'}...")
            print(f"  text length: {len(text)}")
            print(f"  text (first 200 chars): {text[:200]}...")
            print(f"  has /p/itm: {'/p/itm' in href}")
            print(f"  contains rupee: {'₹' in text}")
        
        # Check for price
        price_text = first.find(string=lambda x: x and '₹' in str(x))
        if price_text:
            print(f"\nPrice found: {str(price_text)[:50]}")
        
finally:
    driver.quit()
