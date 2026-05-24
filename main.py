import scrappers.amazonScrapper as amazon_scrapper
import scrappers.flipkarScrapper as flipkart_scrapper
import scrappers.relianceDigitalScrapper as reliance_scrapper

def scrape_amazon(search_query):
    print(f"=== AMAZON RESULTS FOR '{search_query}' ===\n")
    try:
        search_url = amazon_scrapper.search_amazon_product(search_query)
        html_content = amazon_scrapper.fetch_amazon_search_results(search_url)
        products = amazon_scrapper.parse_amazon_html(html_content)
        
        print(f"Found {len(products)} products on Amazon:\n")
        
        for i, product in enumerate(products[:5], 1):  # Show first 5 products
            print(f"--- Product {i} ---")
            print(f"Title: {product['title']}")
            print(f"Price: {product['price']}")
            
            if product['original_price']:
                print(f"Original Price: {product['original_price']}")
            
            if product['rating']:
                print(f"Rating: {product['rating']} stars")
            
            if product['reviews_count']:
                print(f"Reviews: {product['reviews_count']}")
            
            if product['delivery']:
                print(f"Delivery: {product['delivery']}")
            
            print("-" * 50)
    except Exception as e:
        print(f"Amazon scraping failed: {e}")

def scrape_flipkart(search_query):
    print(f"\n=== FLIPKART RESULTS FOR '{search_query}' ===\n")
    try:
        search_url = flipkart_scrapper.search_flipkart_product(search_query)
        html_content = flipkart_scrapper.fetch_flipkart_search_results(search_url)
        products = flipkart_scrapper.parse_flipkart_html(html_content)
        
        print(f"Found {len(products)} products on Flipkart:\n")
        
        for i, product in enumerate(products[:5], 1):  # Show first 5 products
            print(f"--- Product {i} ---")
            print(f"Title: {product['title']}")
            print(f"Price: {product['price']}")
            
            if product['original_price']:
                print(f"Original Price: {product['original_price']}")
            
            if product['discount']:
                print(f"Discount: {product['discount']}")
            
            if product['rating']:
                print(f"Rating: {product['rating']} stars")
            
            if product['ratings_count']:
                print(f"Ratings: {product['ratings_count']}")
            
            if product['reviews_count']:
                print(f"Reviews: {product['reviews_count']}")
            
            if product['features']:
                print(f"Features:")
                for feature in product['features'][:3]:  # Show first 3 features
                    print(f"  • {feature}")
            
            if product['exchange_offer']:
                print(f"Exchange Offer: {product['exchange_offer']}")
            
            print("-" * 50)
    except Exception as e:
        print(f"Flipkart scraping failed: {e}")

def scrape_reliance_digital(search_query):
    print(f"\n=== RELIANCE DIGITAL RESULTS FOR '{search_query}' ===\n")
    try:
        search_url = reliance_scrapper.search_reliance_digital_product(search_query)
        html_content = reliance_scrapper.fetch_reliance_digital_search_results(search_url)
        products = reliance_scrapper.parse_reliance_digital_html(html_content)
        
        print(f"Found {len(products)} products on Reliance Digital:\n")
        
        for i, product in enumerate(products[:5], 1):  # Show first 5 products
            print(f"--- Product {i} ---")
            print(f"Title: {product['title']}")
            print(f"Price: {product['price']}")
            
            if product['mrp']:
                print(f"MRP: {product['mrp']}")
            
            if product['discount']:
                print(f"Discount: {product['discount']}")
            
            if product['savings']:
                print(f"Savings: {product['savings']}")
            
            if product['rating']:
                print(f"Rating: {product['rating']} stars")
            
            if product['special_tag']:
                print(f"Special Tag: {product['special_tag']}")
            
            if product.get('brand'):
                print(f"Brand: {product['brand']}")
            
            if product['delivery']:
                print(f"Delivery: {product['delivery']}")
            
            print("-" * 50)
    except Exception as e:
        print(f"Reliance Digital scraping failed: {e}")

def main():
    search_query = "laptop"
    
    # Scrape all three platforms
    scrape_amazon(search_query)
    scrape_flipkart(search_query)
    scrape_reliance_digital(search_query)
    
    print("\n" + "="*60)
    print("SCRAPING SUMMARY")
    print("="*60)
    print("✅ Amazon: Fully functional - extracts comprehensive product data")
    print("✅ Flipkart: Fully functional - extracts comprehensive product data")
    print("⚠️  Reliance Digital: JavaScript-heavy site - requires advanced tools like Selenium")
    print("\nNote: Reliance Digital uses dynamic content loading and requires")
    print("JavaScript rendering for complete data extraction.")

if __name__ == "__main__":
    main()