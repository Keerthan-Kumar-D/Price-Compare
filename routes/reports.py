from fastapi import APIRouter, HTTPException, status
from typing import List
from datetime import datetime
from database.models import LowestPriceReport, LowestPriceItem
from database.connection import get_database
import logging
import re

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/report", tags=["Reports"])

def extract_price_number(price_str: str) -> float:
    """Extract numeric price from price string (e.g., '₹1,299' -> 1299.0)"""
    if not price_str:
        return float('inf')
    
    # Remove currency symbols and commas, extract numbers
    clean_price = re.sub(r'[^\d.]', '', price_str.replace(',', ''))
    
    try:
        return float(clean_price) if clean_price else float('inf')
    except ValueError:
        return float('inf')

def calculate_discount(current_price: str, original_price: str) -> str:
    """Calculate discount percentage"""
    if not current_price or not original_price:
        return None
    
    current = extract_price_number(current_price)
    original = extract_price_number(original_price)
    
    if current == float('inf') or original == float('inf') or original <= current:
        return None
    
    discount_percent = ((original - current) / original) * 100
    return f"{discount_percent:.0f}% OFF"

@router.get("/lowest-prices", response_model=LowestPriceReport)
async def get_lowest_price_report(query: str = "", realtime: bool = False):
    """Generate a report of lowest prices across all platforms for each product"""
    try:
        if query and realtime:
            # Generate real-time report for the search query
            logger.info(f"Generating real-time report for query: {query}")
            products = await get_realtime_lowest_prices(query)
        else:
            # Use stored data as fallback when no query is provided or realtime is False
            logger.info("Using stored data for report")
            products = await get_stored_lowest_prices()
        
        # Sort by price (lowest first)
        products.sort(key=lambda x: extract_price_number(x.lowest_price))
        
        report = LowestPriceReport(
            total_products=len(products),
            report_generated_at=datetime.utcnow(),
            products=products
        )
        
        logger.info(f"Generated lowest price report with {len(products)} products")
        return report
        
    except Exception as e:
        logger.error(f"Failed to generate report: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate lowest price report"
        )

async def get_realtime_lowest_prices(query: str) -> List[LowestPriceItem]:
    """Get real-time lowest prices by scraping all platforms"""
    from scrappers.amazonScrapper import scrape_amazon
    from scrappers.flipkarScrapper import scrape_flipkart
    from scrappers.relianceDigitalScrapper import scrape_reliance_digital
    
    products = []
    
    try:
        # Scrape all platforms concurrently
        import asyncio
        
        async def scrape_platform(scraper_func, platform_name):
            try:
                return await asyncio.get_event_loop().run_in_executor(
                    None, lambda: scraper_func(query)
                )
            except Exception as e:
                logger.error(f"Error scraping {platform_name}: {e}")
                return []
        
        # Run all scrapers concurrently
        amazon_task = scrape_platform(scrape_amazon, "Amazon")
        flipkart_task = scrape_platform(scrape_flipkart, "Flipkart") 
        reliance_task = scrape_platform(scrape_reliance_digital, "Reliance Digital")
        
        amazon_results, flipkart_results, reliance_results = await asyncio.gather(
            amazon_task, flipkart_task, reliance_task, return_exceptions=True
        )
        
        # Process results and find lowest prices for each product
        all_products = {}
        
        # Process Amazon results
        if isinstance(amazon_results, list):
            for product in amazon_results:
                if product.get('price') and 'not available' not in product['price'].lower():
                    price_numeric = extract_price_number(product['price'])
                    if price_numeric != float('inf'):
                        product_key = product['title'].lower().strip()
                        if product_key not in all_products or price_numeric < all_products[product_key]['price_numeric']:
                            all_products[product_key] = {
                                'product_name': product['title'],
                                'lowest_price': product['price'],
                                'platform': 'Amazon',
                                'product_link': product.get('product_link', ''),
                                'image_url': product.get('image_url'),
                                'original_price': product.get('original_price'),
                                'price_numeric': price_numeric
                            }
        
        # Process Flipkart results
        if isinstance(flipkart_results, list):
            for product in flipkart_results:
                if product.get('price') and 'not available' not in product['price'].lower():
                    price_numeric = extract_price_number(product['price'])
                    if price_numeric != float('inf'):
                        product_key = product['title'].lower().strip()
                        if product_key not in all_products or price_numeric < all_products[product_key]['price_numeric']:
                            all_products[product_key] = {
                                'product_name': product['title'],
                                'lowest_price': product['price'],
                                'platform': 'Flipkart',
                                'product_link': product.get('product_link', ''),
                                'image_url': product.get('image_url'),
                                'original_price': product.get('original_price'),
                                'price_numeric': price_numeric
                            }
        
        # Process Reliance Digital results
        if isinstance(reliance_results, list):
            for product in reliance_results:
                if product.get('price') and 'not available' not in product['price'].lower():
                    price_numeric = extract_price_number(product['price'])
                    if price_numeric != float('inf'):
                        product_key = product['title'].lower().strip()
                        if product_key not in all_products or price_numeric < all_products[product_key]['price_numeric']:
                            all_products[product_key] = {
                                'product_name': product['title'],
                                'lowest_price': product['price'],
                                'platform': 'Reliance Digital',
                                'product_link': product.get('product_link', ''),
                                'image_url': product.get('image_url'),
                                'original_price': product.get('mrp'),
                                'price_numeric': price_numeric
                            }
        
        # Convert to LowestPriceItem objects
        for product_data in all_products.values():
            discount = None
            if product_data['original_price']:
                discount = calculate_discount(product_data['lowest_price'], product_data['original_price'])
            
            lowest_price_item = LowestPriceItem(
                product_name=product_data['product_name'],
                lowest_price=product_data['lowest_price'],
                platform=product_data['platform'],
                product_link=product_data['product_link'],
                image_url=product_data['image_url'],
                original_price=product_data['original_price'],
                discount=discount
            )
            products.append(lowest_price_item)
    
    except Exception as e:
        logger.error(f"Error in real-time scraping: {e}")
    
    return products

async def get_stored_lowest_prices() -> List[LowestPriceItem]:
    """Get lowest prices from stored database data"""
    db = await get_database()
    products = []
    
    async for product in db.products.find({}).limit(10):  # Limit for performance
        platforms = product.get('platforms', {})
        
        # Extract prices from all platforms
        platform_prices = []
        
        # Amazon
        amazon = platforms.get('amazon')
        if amazon and amazon.get('price') and 'not available' not in amazon['price'].lower():
            price_numeric = extract_price_number(amazon['price'])
            if price_numeric != float('inf'):
                platform_prices.append({
                    'platform': 'Amazon',
                    'price': amazon['price'],
                    'original_price': amazon.get('original_price'),
                    'link': amazon.get('product_link', ''),
                    'image': amazon.get('image_url'),
                    'price_numeric': price_numeric
                })
        
        # Flipkart  
        flipkart = platforms.get('flipkart')
        if flipkart and flipkart.get('price') and 'not available' not in flipkart['price'].lower():
            price_numeric = extract_price_number(flipkart['price'])
            if price_numeric != float('inf'):
                platform_prices.append({
                    'platform': 'Flipkart',
                    'price': flipkart['price'],
                    'original_price': flipkart.get('original_price'),
                    'link': flipkart.get('product_link', ''),
                    'image': flipkart.get('image_url'),
                    'price_numeric': price_numeric
                })
        
        # Reliance Digital
        reliance = platforms.get('reliance_digital')
        if reliance and reliance.get('price') and 'not available' not in reliance['price'].lower():
            price_numeric = extract_price_number(reliance['price'])
            if price_numeric != float('inf'):
                platform_prices.append({
                    'platform': 'Reliance Digital',
                    'price': reliance['price'],
                    'original_price': reliance.get('mrp'),  # Use MRP as original price
                    'link': reliance.get('product_link', ''),
                    'image': reliance.get('image_url'),
                    'price_numeric': price_numeric
                })
        
        # Find the platform with lowest price
        if platform_prices:
            lowest = min(platform_prices, key=lambda x: x['price_numeric'])
            
            # Calculate discount if original price exists
            discount = None
            if lowest['original_price']:
                discount = calculate_discount(lowest['price'], lowest['original_price'])
            
            lowest_price_item = LowestPriceItem(
                product_name=product['title'],
                lowest_price=lowest['price'],
                platform=lowest['platform'],
                product_link=lowest['link'],
                image_url=lowest['image'],
                original_price=lowest['original_price'],
                discount=discount
            )
            products.append(lowest_price_item)
    
    return products

@router.get("/platform-comparison/{product_id}")
async def get_platform_comparison(product_id: str):
    """Get price comparison across all platforms for a specific product"""
    from bson import ObjectId
    
    db = await get_database()
    
    try:
        # Validate ObjectId
        if not ObjectId.is_valid(product_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid product ID"
            )
        
        # Get product
        product = await db.products.find_one({"_id": ObjectId(product_id)})
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        platforms = product.get('platforms', {})
        comparison = {
            'product_name': product['title'],
            'platforms': []
        }
        
        # Add platform data
        for platform_name, platform_data in platforms.items():
            if platform_data and platform_data.get('price'):
                platform_info = {
                    'name': platform_name.replace('_', ' ').title(),
                    'price': platform_data['price'],
                    'original_price': platform_data.get('original_price') or platform_data.get('mrp'),
                    'product_link': platform_data.get('product_link', ''),
                    'rating': platform_data.get('rating'),
                    'availability': 'Available'
                }
                
                # Calculate discount
                if platform_info['original_price']:
                    platform_info['discount'] = calculate_discount(
                        platform_info['price'], 
                        platform_info['original_price']
                    )
                
                comparison['platforms'].append(platform_info)
        
        # Sort by price
        comparison['platforms'].sort(
            key=lambda x: extract_price_number(x['price'])
        )
        
        return comparison
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get platform comparison: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get platform comparison"
        )