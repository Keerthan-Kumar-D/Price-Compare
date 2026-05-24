from fastapi import APIRouter, HTTPException, status, Depends
from typing import Dict, Any
from datetime import datetime
from bson import ObjectId
from database.models import ProductInDB, UserInDB
from database.connection import get_database
from auth.security import get_current_active_user
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/products", tags=["Products"])

@router.post("/save")
async def save_product(
    product_data: Dict[str, Any],
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Save a product to the database and return its ID"""
    db = await get_database()
    
    try:
        # Check if product already exists by temp_id or title+price combination
        temp_id = product_data.get('temp_id')
        title = product_data.get('title')
        price = product_data.get('price')
        product_link = product_data.get('product_link')
        
        # Try to find existing product
        existing_product = None
        if product_link:
            existing_product = await db.products.find_one({"product_link": product_link})
        
        if not existing_product and title and price:
            existing_product = await db.products.find_one({
                "title": title,
                "price": price
            })
        
        if existing_product:
            logger.info(f"Product already exists with ID: {existing_product['_id']}")
            return {"_id": str(existing_product["_id"])}
        
        # Create new product document
        product_doc = {
            "title": title,
            "normalized_title": title.lower().strip() if title else "",
            "price": price,
            "original_price": product_data.get('original_price'),
            "rating": product_data.get('rating'),
            "reviews_count": product_data.get('reviews_count'),
            "ratings_count": product_data.get('ratings_count'),
            "image_url": product_data.get('image_url'),
            "product_link": product_link,
            "delivery": product_data.get('delivery'),
            "discount": product_data.get('discount'),
            "features": product_data.get('features', []),
            "exchange_offer": product_data.get('exchange_offer'),
            "brand": product_data.get('brand'),
            "special_tag": product_data.get('special_tag'),
            "temp_id": temp_id,
            "created_at": datetime.utcnow(),
            "created_by": ObjectId(current_user.id),
            "platforms": {}  # Will be populated with platform-specific data
        }
        
        # Remove None values
        product_doc = {k: v for k, v in product_doc.items() if v is not None}
        
        # Insert product
        result = await db.products.insert_one(product_doc)
        
        logger.info(f"Product saved with ID: {result.inserted_id}")
        return {"_id": str(result.inserted_id)}
        
    except Exception as e:
        logger.error(f"Failed to save product: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save product"
        )

@router.get("/{product_id}")
async def get_product(product_id: str):
    """Get a product by ID"""
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
        
        # Convert ObjectId to string
        product["_id"] = str(product["_id"])
        if "created_by" in product:
            product["created_by"] = str(product["created_by"])
        
        return product
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get product: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve product"
        )