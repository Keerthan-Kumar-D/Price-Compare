from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import asyncio
import logging
from datetime import datetime
import os
from dotenv import load_dotenv
from contextlib import asynccontextmanager

# Import scrapers
import scrappers.amazonScrapper as amazon_scrapper
import scrappers.flipkarScrapper as flipkart_scrapper
import scrappers.myntra_selenium as myntra_scrapper
# Import Meesho scraper
from scrappers.meeshoscrapper import search_meesho

# Import database and routes
from database.connection import connect_to_mongo, close_mongo_connection
from routes.auth import router as auth_router
from routes.wishlist import router as wishlist_router
from routes.reports import router as reports_router
from utils.product_utils import save_scraped_products
from utils.cache import search_cache

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Lifespan event handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_to_mongo()
    yield
    # Shutdown
    await close_mongo_connection()

# FastAPI app initialization
app = FastAPI(
    title="E-Commerce Scraper API",
    description="REST API for scraping products from Amazon, Flipkart, and Reliance Digital",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware for React frontend
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",") 
print("ALLOWED_ORIGINS =", allowed_origins)
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
from routes.products import router as products_router
app.include_router(auth_router)
app.include_router(wishlist_router)
app.include_router(reports_router)
app.include_router(products_router)

# Pydantic models for API responses
class Product(BaseModel):
    title: str
    price: str
    original_price: Optional[str] = None
    discount: Optional[str] = None
    rating: Optional[str] = None
    reviews_count: Optional[str] = None
    ratings_count: Optional[str] = None
    delivery: Optional[str] = None
    features: Optional[List[str]] = []
    exchange_offer: Optional[str] = None
    mrp: Optional[str] = None
    savings: Optional[str] = None
    special_tag: Optional[str] = None
    brand: Optional[str] = None
    image_url: Optional[str] = None
    product_link: Optional[str] = None
    cod_available: Optional[str] = None  # For Meesho

class ScrapingResponse(BaseModel):
    platform: str
    search_query: str
    total_products: int
    products: List[Product]
    scraped_at: str
    status: str
    message: Optional[str] = None

class ComparisonResponse(BaseModel):
    search_query: str
    platforms: Dict[str, ScrapingResponse]
    total_products_found: int
    scraped_at: str

class HealthResponse(BaseModel):
    status: str
    message: str
    timestamp: str
    version: str

# Helper function to format datetime
def get_current_timestamp():
    return datetime.now().isoformat()

# Health check endpoint
@app.get("/", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint to verify API is running
    """
    return HealthResponse(
        status="healthy",
        message="E-Commerce Scraper API is running",
        timestamp=get_current_timestamp(),
        version="1.0.0"
    )

@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health():
    """
    Detailed health check endpoint
    """
    return HealthResponse(
        status="healthy",
        message="All scraper services are operational",
        timestamp=get_current_timestamp(),
        version="1.0.0"
    )

# Amazon scraper endpoint
@app.get("/api/scrape/amazon", response_model=ScrapingResponse, tags=["Scrapers"])
async def scrape_amazon(
    query: str = Query(..., description="Search query for products", min_length=1),
    limit: int = Query(10, description="Maximum number of products to return", ge=1, le=50)
):
    """
    Scrape products from Amazon
    
    - **query**: Search term for products (required)
    - **limit**: Maximum number of products to return (1-50, default: 10)
    """
    try:
        logger.info(f"Scraping Amazon for query: {query}")
        
        # Get search URL and fetch results
        search_url = amazon_scrapper.search_amazon_product(query)
        html_content = amazon_scrapper.fetch_amazon_search_results(search_url)
        products_data = amazon_scrapper.parse_amazon_html(html_content)
        
        # Convert to Pydantic models and limit results
        products = []
        for product_data in products_data[:limit]:
            product = Product(
                title=product_data.get('title', ''),
                price=product_data.get('price', ''),
                original_price=product_data.get('original_price'),
                rating=product_data.get('rating'),
                reviews_count=product_data.get('reviews_count'),
                delivery=product_data.get('delivery'),
                image_url=product_data.get('image_url'),
                product_link=product_data.get('product_link')
            )
            products.append(product)
        
        return ScrapingResponse(
            platform="Amazon",
            search_query=query,
            total_products=len(products),
            products=products,
            scraped_at=get_current_timestamp(),
            status="success"
        )
        
    except Exception as e:
        logger.error(f"Amazon scraping failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Amazon scraping failed: {str(e)}")

# Flipkart scraper endpoint
@app.get("/api/scrape/flipkart", response_model=ScrapingResponse, tags=["Scrapers"])
async def scrape_flipkart(
    query: str = Query(..., description="Search query for products", min_length=1),
    limit: int = Query(10, description="Maximum number of products to return", ge=1, le=50)
):
    """
    Scrape products from Flipkart using requests + BeautifulSoup

    - **query**: Search term for products (required)
    - **limit**: Maximum number of products to return (1-50, default: 10)

    Note: Fast scraper (~2-3 seconds) using lightweight HTTP requests.
    """
    try:
        logger.info(f"Scraping Flipkart for query: {query}")

        # Use simple requests-based scraper (works well for Flipkart)
        search_url = flipkart_scrapper.search_flipkart_product(query)
        html_content = flipkart_scrapper.fetch_flipkart_search_results(search_url)
        products_data = flipkart_scrapper.parse_flipkart_html(html_content)
        
        # Limit results
        products_data = products_data[:limit]
        
        # Convert to Pydantic models
        products = []
        for product_data in products_data:
            product = Product(
                title=product_data.get('title', ''),
                price=product_data.get('price', ''),
                original_price=product_data.get('original_price'),
                discount=product_data.get('discount'),
                rating=product_data.get('rating'),
                reviews_count=product_data.get('reviews_count'),
                ratings_count=product_data.get('ratings_count'),
                features=product_data.get('features', []),
                exchange_offer=product_data.get('exchange_offer'),
                image_url=product_data.get('image_url'),
                product_link=product_data.get('product_link'),
                delivery=product_data.get('delivery')
            )
            products.append(product)
        
        logger.info(f"Returning {len(products)} Flipkart products (limit: {limit})")
        
        return ScrapingResponse(
            platform="Flipkart",
            search_query=query,
            total_products=len(products),
            products=products,
            scraped_at=get_current_timestamp(),
            status="success"
        )
        
    except Exception as e:
        logger.error(f"Flipkart scraping failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Flipkart scraping failed: {str(e)}")


    
                
 

# Myntra scraper endpoint (using Playwright)
@app.get("/api/scrape/myntra", response_model=ScrapingResponse, tags=["Scrapers"])
async def scrape_myntra(
    query: str = Query(..., description="Search query for products", min_length=1),
    limit: int = Query(10, description="Maximum number of products to return", ge=1, le=50)
):
    """
    Scrape products from Myntra using Playwright

    - **query**: Search term for products (required)
    - **limit**: Maximum number of products to return (1-50, default: 10)

    Note: Uses Playwright to handle JavaScript rendering. Takes 20-30 seconds per request.
    """
    try:
        logger.info(f"Scraping Myntra with Playwright for query: {query}")

        # Use Playwright scraper (handles JavaScript rendering)
        products_data = myntra_scrapper.scrape_myntra_playwright(query, max_products=limit)
        
        # Convert to Pydantic models
        products = []
        for product_data in products_data:
            product = Product(
                title=product_data.get('title', ''),
                brand=product_data.get('brand'),
                price=product_data.get('price', ''),
                original_price=product_data.get('original_price'),
                discount=product_data.get('discount'),
                rating=product_data.get('rating'),
                reviews_count=product_data.get('reviews_count'),
                image_url=product_data.get('image_url'),
                product_link=product_data.get('product_link')
            )
            products.append(product)
        
        # Set message if no products found
        message = None
        if len(products) == 0:
            message = "No products found. Myntra may be blocking automated requests or the search returned no results."
        
        return ScrapingResponse(
            platform="Myntra",
            search_query=query,
            total_products=len(products),
            products=products,
            scraped_at=get_current_timestamp(),
            status="partial" if len(products) == 0 else "success",
            message=message
        )
        
    except Exception as e:
        logger.error(f"Myntra scraping failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Myntra scraping failed: {str(e)}")

# Meesho scraper endpoint (using Playwright)
@app.get("/api/scrape/meesho", response_model=ScrapingResponse, tags=["Scrapers"])
async def scrape_meesho(
    query: str = Query(..., description="Search query for products", min_length=1),
    limit: int = Query(10, description="Maximum number of products to return", ge=1, le=50),
    scroll_count: int = Query(3, description="Number of scrolls to load more products", ge=1, le=10)
):
    """
    Scrape products from Meesho using Playwright browser automation

    - **query**: Search term for products (required)
    - **limit**: Maximum number of products to return (1-50, default: 10)
    - **scroll_count**: Number of scrolls to load more products (1-10, default: 3)

    Note: This uses Playwright to handle JavaScript rendering. Takes 10-20 seconds per request.
    """
    try:
        logger.info(f"Scraping Meesho with Playwright for query: {query}")
        
        # Use Meesho scraper (handles JavaScript rendering)
        products_data = await asyncio.to_thread(
            search_meesho, 
            query, 
            headless=True, 
            scroll_count=scroll_count
        )
        
        # Handle None or empty results
        if products_data is None:
            products_data = []
            logger.warning("Meesho scraper returned None")
        
        logger.info(f"Meesho scraper returned {len(products_data)} products")
        
        # Log first product for debugging
        if products_data:
            logger.info(f"First Meesho product sample: {products_data[0]}")
        
        # Limit results
        products_data = products_data[:limit]
        
        # Convert to Pydantic models
        products = []
        for product_data in products_data:
            product = Product(
                title=product_data.get('title', ''),
                price=product_data.get('price', ''),
                original_price=product_data.get('original_price'),
                discount=product_data.get('discount'),
                rating=product_data.get('rating'),
                reviews_count=product_data.get('reviews_count'),
                delivery=product_data.get('delivery'),
                cod_available=product_data.get('cod_available'),
                image_url=product_data.get('image_url'),
                product_link=product_data.get('product_link')
            )
            products.append(product)
        
        # Set message if no products found
        message = None
        if len(products) == 0:
            message = "No products found. Meesho may be blocking automated requests or the search returned no results."
        
        return ScrapingResponse(
            platform="Meesho",
            search_query=query,
            total_products=len(products),
            products=products,
            scraped_at=get_current_timestamp(),
            status="partial" if len(products) == 0 else "success",
            message=message
        )
        
    except Exception as e:
        logger.error(f"Meesho scraping failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Meesho scraping failed: {str(e)}")

# Comparison endpoint - scrape all platforms
@app.get("/api/scrape/all", response_model=ComparisonResponse, tags=["Comparison"])
async def scrape_all_platforms(
    query: str = Query(..., description="Search query for products", min_length=1),
    limit: int = Query(5, description="Maximum number of products per platform", ge=1, le=20)
):
    """
    Scrape products from all platforms (Amazon, Flipkart, Reliance Digital, Myntra, Meesho)
    
    - **query**: Search term for products (required)
    - **limit**: Maximum number of products per platform (1-20, default: 5)
    
    Returns comparison data from all five platforms
    Results are cached for 5 minutes to improve performance
    """
    try:
        logger.info(f"Scraping all platforms for query: {query}")
        
        # Check cache first
        cached_result = search_cache.get(query, limit)
        if cached_result:
            logger.info(f"Returning cached results for query: {query}")
            return ComparisonResponse(**cached_result)
        
        # Scrape all platforms concurrently with aggressive timeouts for 10s target
        async def scrape_with_timeout(scraper_func, timeout_seconds=5):
            """Wrapper to add timeout to scraper functions"""
            try:
                return await asyncio.wait_for(scraper_func, timeout=timeout_seconds)
            except asyncio.TimeoutError:
                logger.warning(f"Scraper timed out after {timeout_seconds} seconds")
                return None
            except Exception as e:
                logger.error(f"Scraper error: {e}")
                return None
        
        amazon_task = scrape_with_timeout(scrape_amazon(query, limit), 5)
        flipkart_task = scrape_with_timeout(scrape_flipkart(query, limit), 5)
        myntra_task = scrape_with_timeout(scrape_myntra(query, limit), 8)
        meesho_task = scrape_with_timeout(scrape_meesho(query, limit, scroll_count=1), 25)
        
        # Wait for all tasks to complete
        amazon_response, flipkart_response, myntra_response, meesho_response = await asyncio.gather(
            amazon_task, flipkart_task, myntra_task, meesho_task,
            return_exceptions=True
        )

        reliance_response = None
        
        platforms = {}
        total_products = 0
        
        # Process Amazon results
        if isinstance(amazon_response, ScrapingResponse):
            platforms["amazon"] = amazon_response
            total_products += amazon_response.total_products
        else:
            platforms["amazon"] = ScrapingResponse(
                platform="Amazon",
                search_query=query,
                total_products=0,
                products=[],
                scraped_at=get_current_timestamp(),
                status="error",
                message=str(amazon_response) if amazon_response else "Unknown error"
            )
        
        # Process Flipkart results
        if isinstance(flipkart_response, ScrapingResponse):
            platforms["flipkart"] = flipkart_response
            total_products += flipkart_response.total_products
        else:
            platforms["flipkart"] = ScrapingResponse(
                platform="Flipkart",
                search_query=query,
                total_products=0,
                products=[],
                scraped_at=get_current_timestamp(),
                status="error",
                message=str(flipkart_response) if flipkart_response else "Unknown error"
            )
        
        # Process Reliance Digital results
        if isinstance(reliance_response, ScrapingResponse):
            platforms["reliance_digital"] = reliance_response
            total_products += reliance_response.total_products
        else:
            platforms["reliance_digital"] = ScrapingResponse(
                platform="Reliance Digital",
                search_query=query,
                total_products=0,
                products=[],
                scraped_at=get_current_timestamp(),
                status="error",
                message=str(reliance_response) if reliance_response else "Unknown error"
            )
        
        # Process Myntra results
        if isinstance(myntra_response, ScrapingResponse):
            platforms["myntra"] = myntra_response
            total_products += myntra_response.total_products
        else:
            platforms["myntra"] = ScrapingResponse(
                platform="Myntra",
                search_query=query,
                total_products=0,
                products=[],
                scraped_at=get_current_timestamp(),
                status="error",
                message=str(myntra_response) if myntra_response else "Unknown error"
            )
        
        # Process Meesho results
        if isinstance(meesho_response, ScrapingResponse):
            platforms["meesho"] = meesho_response
            total_products += meesho_response.total_products
            logger.info(f"Meesho returned {meesho_response.total_products} products")
        elif isinstance(meesho_response, Exception):
            logger.error(f"Meesho scraping exception: {type(meesho_response).__name__}: {str(meesho_response)}")
            platforms["meesho"] = ScrapingResponse(
                platform="Meesho",
                search_query=query,
                total_products=0,
                products=[],
                scraped_at=get_current_timestamp(),
                status="error",
                message=f"Scraping error: {str(meesho_response)}"
            )
        else:
            logger.error(f"Meesho scraping returned None or timed out")
            platforms["meesho"] = ScrapingResponse(
                platform="Meesho",
                search_query=query,
                total_products=0,
                products=[],
                scraped_at=get_current_timestamp(),
                status="error",
                message="Scraper timed out or returned no data"
            )
        
        response = ComparisonResponse(
            search_query=query,
            platforms=platforms,
            total_products_found=total_products,
            scraped_at=get_current_timestamp()
        )
        
        # Cache the successful response
        search_cache.set(query, limit, response.dict())
        logger.info(f"Cached results for query: {query}")
        
        # Save products to database for reports (async, don't wait)
        asyncio.create_task(save_scraped_products(query, response.dict()))
        
        return response
        
    except Exception as e:
        logger.error(f"Multi-platform scraping failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Multi-platform scraping failed: {str(e)}")

# Get supported platforms
@app.get("/api/platforms", tags=["Information"])
async def get_platforms():
    """
    Get list of supported e-commerce platforms
    """
    return {
        "platforms": [
            {
                "name": "Amazon",
                "endpoint": "/api/scrape/amazon",
                "status": "fully_supported",
                "features": ["prices", "ratings", "reviews", "delivery_info"]
            },
            {
                "name": "Flipkart", 
                "endpoint": "/api/scrape/flipkart",
                "status": "fully_supported",
                "features": ["prices", "ratings", "reviews", "discounts", "features", "exchange_offers"]
            },
            {
                "name": "Reliance Digital",
                "endpoint": "/api/scrape/reliance-digital", 
                "status": "partial_support",
                "features": ["basic_info"],
                "note": "JavaScript rendering required for complete data"
            },
            {
                "name": "Myntra",
                "endpoint": "/api/scrape/myntra",
                "status": "fully_supported",
                "features": ["brand", "prices", "ratings", "reviews", "discounts"],
                "note": "Uses Playwright browser automation for JavaScript rendering. Optimized to ~3-4 seconds."
            },
            {
                "name": "Meesho",
                "endpoint": "/api/scrape/meesho",
                "status": "fully_supported",
                "features": ["prices", "ratings", "reviews", "discounts", "delivery_info", "cod_available"],
                "note": "Uses Playwright browser automation for JavaScript rendering. Optimized to ~3-4 seconds."
            }
        ],
        "comparison_endpoint": "/api/scrape/all",
        "total_platforms": 5,
        "performance": "Results cached for 5 minutes. First search: ~7-10 seconds, Cached: <1 second"
    }

# Cache statistics endpoint
@app.get("/api/cache/stats", tags=["Information"])
async def get_cache_stats():
    """
    Get cache statistics
    """
    return search_cache.get_stats()

# Clear cache endpoint (for admin/testing)
@app.post("/api/cache/clear", tags=["Information"])
async def clear_cache():
    """
    Clear all cached search results
    """
    search_cache.clear()
    return {"status": "success", "message": "Cache cleared successfully"}

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    
    uvicorn.run(
        "app:app" if debug else app,
        host=host,
        port=port,
        reload=debug
    )