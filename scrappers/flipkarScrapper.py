from bs4 import BeautifulSoup
import requests
import re
import time

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-IN,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://www.flipkart.com/",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

def search_flipkart_product(search_query):
    search_url = f"https://www.flipkart.com/search?q={search_query.replace(' ', '+')}"
    return search_url

def fetch_flipkart_search_results(search_url):
    # Retry with exponential backoff to handle transient network/HTTP errors
    max_retries = 3
    backoff = 1.0
    for attempt in range(1, max_retries + 1):
        try:
            # Increase timeout slightly to handle slower responses for some categories
            response = requests.get(search_url, headers=headers, timeout=10)
            if response.status_code == 200:
                return response.text
            else:
                # Treat non-200 as transient and retry a couple of times
                if attempt == max_retries:
                    raise Exception(f"Failed to fetch page, status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            if attempt == max_retries:
                raise
            time_to_sleep = backoff * attempt
            import time
            time.sleep(time_to_sleep)
    raise Exception("Failed to fetch Flipkart page after retries")

def parse_flipkart_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    products = []
    seen_titles = set()
    
    # Try to extract image mapping from JSON-LD if available
    image_map = {}
    try:
        scripts = soup.find_all('script', type='application/ld+json')
        for script in scripts:
            try:
                import json
                data = json.loads(script.string)
                if isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict) and item.get('@type') == 'Product':
                            name = item.get('name', '')
                            image = item.get('image', '')
                            if name and image:
                                # Normalize image URL
                                if image.startswith('http://'):
                                    image = image.replace('http://', 'https://')
                                if not image.startswith('https://'):
                                    image = 'https:' + image if image.startswith('//') else 'https://rukminim2.flixcart.com' + image
                                image_map[name.lower().strip()] = image
            except:
                continue
    except:
        pass

    # Find product anchors directly to better cover category-specific layouts (fashion, electronics, etc.)
    anchor_selectors = [
        'a._2rpwqI', 'a.IRpwTa', 'a.s1Q9rs', 'a._2fZ6oW', 'a._2UzuFa',
        'a._3dqZjq', 'a._2r_T1I', 'a._2kHMtA', 'a._1fQZEK', 'a.CGtC98'
    ]

    anchors = []
    for sel in anchor_selectors:
        anchors.extend(soup.select(sel))

    # If no anchors found, fall back to previous container-based approach
    if not anchors:
        anchors = soup.select('div._1AtVbE a')

    # Additional fallback: for fashion layouts Flipkart often uses product-card containers
    if not anchors:
        container_selectors = ['div._2kHMtA', 'div._1xHGtK', 'div._4ddWXP', 'div._1NoI8_']
        for cs in container_selectors:
            for card in soup.select(cs):
                a = card.select_one('a')
                if a:
                    anchors.append(a)
    
    # Price-based fallback: find any text nodes containing rupee symbol and map to anchor
    if not anchors:
        price_texts = soup.find_all(text=re.compile(r'₹\s*[0-9]'))
        for pt in price_texts:
            try:
                parent = pt.parent
                # climb up to find enclosing anchor (product link)
                a = None
                for _ in range(6):
                    if parent is None:
                        break
                    if parent.name == 'a' and parent.get('href'):
                        a = parent
                        break
                    parent = parent.parent
                if a:
                    anchors.append(a)
            except Exception:
                continue

    price_selectors = ['div._30jeq3', 'span._30jeq3', 'div._4b5DiR', 'div.Nx9bqj', 'div._25b18c']
    rating_selectors = ['div._3LWZlK', 'span._3LWZlK', 'div.XQDdHH']

    for a in anchors:
        try:
            # normalize anchor object
            if not getattr(a, 'get', None):
                continue
            # Find a reasonable container to search for price/rating/etc.
            container = a
            # climb up to a product card parent (li or div)
            for _ in range(4):
                if container.name in ['li', 'div'] and container.get('class'):
                    break
                if container.parent is None:
                    break
                container = container.parent

            # Title from anchor title attribute, or search container for anchors with title
            title = a.get('title') or ''
            if not title and container:
                # For fashion products, title is often in a separate anchor within the container
                title_anchors = container.find_all('a', title=True, recursive=True)
                for ta in title_anchors:
                    t = ta.get('title', '')
                    if t and '₹' not in t and '%' not in t and 'off' not in t.lower():
                        title = t
                        break
            
            if not title:
                # try image alt
                img_alt = None
                img_el = a.select_one('img') or (container.select_one('img') if container else None)
                if img_el:
                    img_alt = img_el.get('alt') or img_el.get('title')
                if img_alt and img_alt.strip():
                    title = img_alt
                else:
                    # try to find a reasonable product title inside the product container
                    title = a.get_text(separator=' ', strip=True)
                    # If the anchor text looks like a price/offer (contains ₹ or %),
                    # search the surrounding container for a better title
                    if '₹' in title or '%' in title or 'off' in title.lower():
                        candidate = None
                        # search for text nodes likely to be titles
                        for elem in container.find_all(['div', 'span', 'a', 'p', 'h3', 'h2'], recursive=True) if container else []:
                            try:
                                txt = elem.get_text(' ', strip=True)
                                if not txt:
                                    continue
                                low = txt.lower()
                                if '₹' in txt or '%' in txt or 'off' in low:
                                    continue
                                if any(k in low for k in ['rating', 'ratings', 'reviews', 'warranty', 'seller', 'offer']):
                                    continue
                                # require at least two words and reasonable length
                                if len(txt.split()) >= 2 and 6 <= len(txt) <= 200:
                                    candidate = txt
                                    break
                            except Exception:
                                continue
                        if candidate:
                            title = candidate
            if not title or title in seen_titles:
                continue

            # Price - try to extract the first rupee amount found nearby
            price = None
            for ps in price_selectors:
                p_el = container.select_one(ps) if container else None
                if p_el and p_el.get_text(strip=True):
                    price = p_el.get_text(strip=True)
                    break
            # If still not found, try finding any rupee text inside the anchor
            if not price:
                txt = a.get_text(' ', strip=True)
                m = re.search(r'(₹\s*[\d,]+)', txt)
                if m:
                    price = m.group(1)

            # Skip if no price found (many fashion placeholders may show price elsewhere)
            if not price:
                # try searching nearby nodes: check parent, next siblings and container
                # 1) immediate parent
                if a.parent:
                    for ps in price_selectors:
                        p_el = a.parent.select_one(ps)
                        if p_el and p_el.get_text(strip=True):
                            price = p_el.get_text(strip=True)
                            break
                # 2) next siblings
                if not price:
                    sibling = a.next_sibling
                    while sibling and not price:
                        try:
                            for ps in price_selectors:
                                if getattr(sibling, 'select_one', None):
                                    p_el = sibling.select_one(ps)
                                    if p_el and p_el.get_text(strip=True):
                                        price = p_el.get_text(strip=True)
                                        break
                        except Exception:
                            pass
                        sibling = sibling.next_sibling if hasattr(sibling, 'next_sibling') else None
                # 3) fallback: search container again with broader selectors
                if not price and container:
                    for tag in ['span', 'div']:
                        candidates = container.find_all(tag)
                        for c in candidates:
                            txt = c.get_text(strip=True)
                            if txt and any(ch.isdigit() for ch in txt) and '₹' in txt:
                                price = txt
                                break
                        if price:
                            break

            if not price:
                continue

            # Image - search container for all images and find first valid one
            image_url = None
            # Try anchor first
            imgs = a.find_all('img')
            for img in imgs:
                img_src = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
                if img_src and not img_src.startswith('data:image') and '/fk-p-flap/' not in img_src and 'fa_' not in img_src:
                    # Valid product image (not placeholder)
                    if not img_src.startswith('http'):
                        img_src = 'https:' + img_src if img_src.startswith('//') else 'https://rukminim2.flixcart.com' + img_src
                    image_url = img_src
                    break
            
            # If no image in anchor, search container
            if not image_url and container:
                imgs = container.find_all('img')
                for img in imgs:
                    img_src = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
                    if img_src and not img_src.startswith('data:image') and '/fk-p-flap/' not in img_src and 'fa_' not in img_src:
                        # Valid product image (not placeholder)
                        if not img_src.startswith('http'):
                            img_src = 'https:' + img_src if img_src.startswith('//') else 'https://rukminim2.flixcart.com' + img_src
                        image_url = img_src
                        break
            
            # Fallback: construct image URL from product link PID (Flipkart pattern)
            if not image_url:
                # Try matching title with JSON-LD image map
                title_key = title.lower().strip()
                if title_key in image_map:
                    image_url = image_map[title_key]
                else:
                    # Partial match - check if any JSON-LD product name is in the title
                    for json_name, json_img in image_map.items():
                        if json_name in title_key or title_key in json_name:
                            image_url = json_img
                            break

            # Rating
            rating = None
            for rs in rating_selectors:
                r_el = container.select_one(rs) if container else None
                if r_el:
                    rating_text = r_el.get_text(strip=True)
                    m = re.search(r"(\d+\.?\d*)", rating_text)
                    rating = m.group(1) if m else rating_text
                    break

            # Product link
            href = a.get('href')
            product_link = None
            if href:
                product_link = f"https://www.flipkart.com{href}" if href.startswith('/') else href

            # Clean title: remove price snippets and redundant prefixes
            try:
                title = re.sub(r'Add to Compare', '', title, flags=re.IGNORECASE)
                title = re.sub(r'(₹\s*[\d,]+)', '', title)
                title = ' '.join(title.split())
            except Exception:
                pass

            # Clean price to first rupee amount
            if price:
                m = re.search(r'(₹\s*[\d,]+)', price)
                price_clean = m.group(1) if m else price
            else:
                price_clean = None

            product_data = {
                'title': title,
                'price': price_clean,
                'original_price': None,
                'discount': None,
                'rating': rating,
                'ratings_count': None,
                'reviews_count': None,
                'features': [],
                'image_url': image_url,
                'product_link': product_link,
                'exchange_offer': None,
                'delivery': None
            }

            seen_titles.add(title)
            products.append(product_data)
        except Exception:
            # Skip individual parse errors
            continue

    return products


# Example usage
if __name__ == "__main__":
    # Test with different categories
    test_queries = ["tshirt", "laptop", "shoes", "mobile phone"]
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"Testing search for: {query}")
        print('='*60)
        
        try:
            search_url = search_flipkart_product(query)
            html = fetch_flipkart_search_results(search_url)
            products = parse_flipkart_html(html)
            
            print(f"Found {len(products)} products")
            
            # Show first 3 products
            for i, product in enumerate(products[:3], 1):
                print(f"\nProduct {i}:")
                print(f"  Title: {product['title'][:60]}...")
                print(f"  Price: {product['price']}")
                print(f"  Rating: {product['rating']}")
                if product['discount']:
                    print(f"  Discount: {product['discount']}")
        
        except Exception as e:
            print(f"Error: {e}")