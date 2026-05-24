from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

try:
    driver.get("https://www.flipkart.com/search?q=tshirt")
    time.sleep(5)
    
    # Try to find images
    imgs_with_rukminim = driver.find_elements(By.CSS_SELECTOR, "img[src*='rukminim']")
    print(f"Found {len(imgs_with_rukminim)} images with 'rukminim' in src")
    
    if imgs_with_rukminim:
        for i, img in enumerate(imgs_with_rukminim[:5]):
            src = img.get_attribute('src')
            parent = img.find_element(By.XPATH, "..")
            parent_class = parent.get_attribute('class')
            print(f"\nImage {i+1}:")
            print(f"  Src: {src[:80]}...")
            print(f"  Parent class: {parent_class}")
    
    # Find all product links with titles
    links_with_title = driver.find_elements(By.CSS_SELECTOR, "a[title]")
    print(f"\n\nFound {len(links_with_title)} links with title attribute")
    if links_with_title:
        for i, link in enumerate(links_with_title[:3]):
            title = link.get_attribute('title')
            if 'shirt' in title.lower():
                print(f"\nLink {i+1}: {title[:60]}...")
                
finally:
    driver.quit()
