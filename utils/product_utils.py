from database.connection import get_database
from database.models import ProductInDB, ProductPlatforms, AmazonData, FlipkartData, RelianceDigitalData
from datetime import datetime
import logging
import re

logger = logging.getLogger(__name__)

def normalize_title(title: str) -> str:
    """Normalize product title for better matching"""
    # Remove special characters, convert to lowercase, remove extra spaces
    normalized = re.sub(r'[^\w\s]', '', title.lower())
    normalized = ' '.join(normalized.split())
    return normalized

def extract_keywords(title: str) -> list:
    """Extract search keywords from product title"""
    # Split title into words, remove common words, take unique words > 2 chars
    common_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
    words = title.lower().split()
    keywords = [word for word in words if len(word) > 2 and word not in common_words]
    return list(set(keywords))

async def save_scraped_products(search_query: str, scraped_data: dict):
    """Save scraped products to database for caching and reports"""
    db = await get_database()
    
    try:
        platforms_data = scraped_data.get('platforms', {})
        
        # Process products by matching similar titles across platforms
        all_products = {}
        
        # Collect all products from all platforms
        for platform_name, platform_data in platforms_data.items():
            products = platform_data.get('products', [])
            
            for product in products:
                title = product.get('title', '')
                if not title:
                    continue
                
                normalized_title = normalize_title(title)
                
                # Check if similar product already exists
                product_key = None
                for existing_key in all_products.keys():
                    # Simple similarity check - if 70% of words match
                    existing_words = set(existing_key.split())
                    current_words = set(normalized_title.split())
                    
                    if existing_words and current_words:
                        intersection = len(existing_words.intersection(current_words))
                        union = len(existing_words.union(current_words))
                        similarity = intersection / union if union > 0 else 0
                        
                        if similarity > 0.7:
                            product_key = existing_key
                            break
                
                if not product_key:
                    product_key = normalized_title
                    all_products[product_key] = {
                        'title': title,
                        'normalized_title': normalized_title,
                        'platforms': {},
                        'search_keywords': extract_keywords(title)
                    }
                
                # Add platform-specific data
                platform_data_obj = None
                
                if platform_name == 'amazon':
                    platform_data_obj = AmazonData(
                        price=product.get('price'),
                        original_price=product.get('original_price'),
                        product_link=product.get('product_link'),
                        image_url=product.get('image_url'),
                        rating=product.get('rating'),
                        reviews_count=product.get('reviews_count'),
                        delivery=product.get('delivery'),
                        last_updated=datetime.utcnow()
                    )
                elif platform_name == 'flipkart':
                    platform_data_obj = FlipkartData(
                        price=product.get('price'),
                        original_price=product.get('original_price'),
                        discount=product.get('discount'),
                        product_link=product.get('product_link'),
                        image_url=product.get('image_url'),
                        rating=product.get('rating'),
                        reviews_count=product.get('reviews_count'),
                        ratings_count=product.get('ratings_count'),
                        features=product.get('features', []),
                        exchange_offer=product.get('exchange_offer'),
                        last_updated=datetime.utcnow()
                    )
                elif platform_name == 'reliance_digital':
                    platform_data_obj = RelianceDigitalData(
                        price=product.get('price'),
                        mrp=product.get('mrp'),
                        discount=product.get('discount'),
                        savings=product.get('savings'),
                        product_link=product.get('product_link'),
                        image_url=product.get('image_url'),
                        rating=product.get('rating'),
                        brand=product.get('brand'),
                        special_tag=product.get('special_tag'),
                        last_updated=datetime.utcnow()
                    )
                
                if platform_data_obj:
                    all_products[product_key]['platforms'][platform_name] = platform_data_obj
        
        # Save/update products in database
        saved_count = 0
        for product_key, product_data in all_products.items():
            try:
                # Check if product already exists
                existing_product = await db.products.find_one({
                    "normalized_title": product_data['normalized_title']
                })
                
                platforms_obj = ProductPlatforms(
                    amazon=product_data['platforms'].get('amazon'),
                    flipkart=product_data['platforms'].get('flipkart'),
                    reliance_digital=product_data['platforms'].get('reliance_digital')
                )
                
                if existing_product:
                    # Update existing product
                    update_data = {
                        "platforms": platforms_obj.dict(exclude_none=True),
                        "updated_at": datetime.utcnow()
                    }
                    
                    # Merge search keywords
                    existing_keywords = set(existing_product.get('search_keywords', []))
                    new_keywords = set(product_data['search_keywords'])
                    update_data["search_keywords"] = list(existing_keywords.union(new_keywords))
                    
                    await db.products.update_one(
                        {"_id": existing_product["_id"]},
                        {"$set": update_data}
                    )
                else:
                    # Create new product
                    new_product = ProductInDB(
                        title=product_data['title'],
                        normalized_title=product_data['normalized_title'],
                        platforms=platforms_obj,
                        search_keywords=product_data['search_keywords']
                    )
                    
                    await db.products.insert_one(new_product.dict(by_alias=True))
                
                saved_count += 1
                
            except Exception as e:
                logger.error(f"Failed to save product {product_data['title']}: {e}")
                continue
        
        logger.info(f"Saved {saved_count} products for search query: {search_query}")
        
    except Exception as e:
        logger.error(f"Failed to save scraped products: {e}")
        # Don't raise here as this is not critical for the scraping functionality