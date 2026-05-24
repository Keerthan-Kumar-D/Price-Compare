from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from datetime import datetime
from bson import ObjectId
from database.models import WishlistItemCreate, WishlistItemResponse, WishlistItemInDB, UserInDB, ProductInDB
from database.connection import get_database
from auth.security import get_current_active_user
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/wishlist", tags=["Wishlist"])

@router.post("/add", response_model=WishlistItemResponse, status_code=status.HTTP_201_CREATED)
async def add_to_wishlist(
    item: WishlistItemCreate,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Add a product to user's wishlist"""
    db = await get_database()
    
    try:
        # Check if product exists
        product = await db.products.find_one({"_id": ObjectId(item.product_id)})
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        # Check if already in wishlist  
        user_object_id = ObjectId(current_user.id) if current_user.id else None
        if not user_object_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user ID"
            )
            
        existing_item = await db.wishlists.find_one({
            "user_id": user_object_id,
            "product_id": ObjectId(item.product_id)
        })
        
        if existing_item:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product already in wishlist"
            )
        
        # Create wishlist item
        wishlist_doc = {
            "user_id": user_object_id,
            "product_id": ObjectId(item.product_id),
            "added_at": datetime.utcnow(),
            "price_alerts": item.price_alerts or {}
        }
        
        result = await db.wishlists.insert_one(wishlist_doc)
        
        # Prepare the response with complete product data
        wishlist_response = {
            "_id": str(result.inserted_id),
            "product_id": str(wishlist_doc["product_id"]),
            "added_at": wishlist_doc["added_at"],
            "price_alerts": wishlist_doc["price_alerts"]
        }
        
        # Convert ObjectId in product and prepare complete product data
        if product and "_id" in product:
            product["_id"] = str(product["_id"])
            
            # Extract data using same logic as get_user_wishlist
            direct_price = product.get("price")
            direct_image_url = product.get("image_url")
            direct_product_link = product.get("product_link")
            direct_original_price = product.get("original_price")
            direct_discount = product.get("discount")
            direct_rating = product.get("rating")
            direct_brand = product.get("brand")
            direct_delivery = product.get("delivery")
            direct_features = product.get("features", [])
            
            # If direct fields are not available, try to extract from platforms
            best_price = direct_price
            best_image_url = direct_image_url
            best_product_link = direct_product_link
            best_original_price = direct_original_price
            best_discount = direct_discount
            best_rating = direct_rating
            best_brand = direct_brand
            best_delivery = direct_delivery
            best_features = direct_features
            
            if not best_price or not best_image_url or not best_product_link:
                platforms = product.get("platforms", {})
                if platforms:
                    for platform_name, platform_data in platforms.items():
                        if platform_data and isinstance(platform_data, dict):
                            if platform_data.get("price") and not best_price:
                                best_price = platform_data.get("price")
                            if platform_data.get("image_url") and not best_image_url:
                                best_image_url = platform_data.get("image_url")
                            if platform_data.get("product_link") and not best_product_link:
                                best_product_link = platform_data.get("product_link")
                            if platform_data.get("original_price") and not best_original_price:
                                best_original_price = platform_data.get("original_price")
                            if platform_data.get("discount") and not best_discount:
                                best_discount = platform_data.get("discount")
                            if platform_data.get("rating") and not best_rating:
                                best_rating = platform_data.get("rating")
                            if platform_data.get("brand") and not best_brand:
                                best_brand = platform_data.get("brand")
                            if platform_data.get("delivery") and not best_delivery:
                                best_delivery = platform_data.get("delivery")
                            if platform_data.get("features") and not best_features:
                                best_features = platform_data.get("features", [])

            # Create complete product data
            product_data = {
                "id": str(product["_id"]),
                "title": product.get("title", "Unknown Product"),
                "normalized_title": product.get("normalized_title", product.get("title", "").lower()),
                "platforms": product.get("platforms", {}),
                "search_keywords": product.get("search_keywords", []),
                "created_at": product.get("created_at", datetime.utcnow()),
                "updated_at": product.get("updated_at", datetime.utcnow()),
                "price": best_price or "Price not available",
                "original_price": best_original_price,
                "image_url": best_image_url or "",
                "product_link": best_product_link or "",
                "rating": best_rating,
                "discount": best_discount,
                "brand": best_brand,
                "delivery": best_delivery,
                "features": best_features or [],
            }
            
            wishlist_response["product"] = ProductInDB(**product_data)
        
        logger.info(f"Product added to wishlist: user={current_user.email}, product={item.product_id}")
        return WishlistItemResponse(**wishlist_response)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to add to wishlist: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add product to wishlist"
        )

@router.delete("/remove/{product_id}")
async def remove_from_wishlist(
    product_id: str,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Remove a product from user's wishlist"""
    db = await get_database()
    
    try:
        # Validate ObjectId
        if not ObjectId.is_valid(product_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid product ID"
            )
        
        # Remove from wishlist
        user_object_id = ObjectId(current_user.id) if current_user.id else None
        if not user_object_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user ID"
            )
            
        result = await db.wishlists.delete_one({
            "user_id": user_object_id,
            "product_id": ObjectId(product_id)
        })
        
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found in wishlist"
            )
        
        logger.info(f"Product removed from wishlist: user={current_user.email}, product={product_id}")
        return {"message": "Product removed from wishlist"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to remove from wishlist: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to remove product from wishlist"
        )

@router.get("/", response_model=List[WishlistItemResponse])
async def get_user_wishlist(
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Get user's complete wishlist with product details"""
    db = await get_database()
    
    try:
        # Get wishlist items with product details using aggregation
        user_object_id = ObjectId(current_user.id) if current_user.id else None
        if not user_object_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user ID"
            )
            
        pipeline = [
            {"$match": {"user_id": user_object_id}},
            {"$lookup": {
                "from": "products",
                "localField": "product_id",
                "foreignField": "_id",
                "as": "product"
            }},
            {"$unwind": "$product"},
            {"$sort": {"added_at": -1}}
        ]
        
        wishlist_items = []
        async for item in db.wishlists.aggregate(pipeline):
            # Convert ObjectIds to strings
            item_response = {
                "_id": str(item["_id"]),
                "product_id": str(item["product_id"]),
                "added_at": item["added_at"],
                "price_alerts": item.get("price_alerts", {}),
            }
            
            # Convert ObjectId in product and handle missing fields
            product = item["product"]
            if product and "_id" in product:
                product["_id"] = str(product["_id"])
                
                # First, try to get data from direct fields (saved from frontend)
                direct_price = product.get("price")
                direct_image_url = product.get("image_url")
                direct_product_link = product.get("product_link")
                direct_original_price = product.get("original_price")
                direct_discount = product.get("discount")
                direct_rating = product.get("rating")
                direct_brand = product.get("brand")
                direct_delivery = product.get("delivery")
                direct_features = product.get("features", [])
                
                # If direct fields are not available, try to extract from platforms
                best_price = direct_price
                best_image_url = direct_image_url
                best_product_link = direct_product_link
                best_original_price = direct_original_price
                best_discount = direct_discount
                best_rating = direct_rating
                best_brand = direct_brand
                best_delivery = direct_delivery
                best_features = direct_features
                
                # Only extract from platforms if direct fields are not available
                if not best_price or not best_image_url or not best_product_link:
                    platforms = product.get("platforms", {})
                    if platforms:
                        # Try each platform to find the best available data
                        for platform_name, platform_data in platforms.items():
                            if platform_data and isinstance(platform_data, dict):
                                # Get price (prioritize first available)
                                if platform_data.get("price") and not best_price:
                                    best_price = platform_data.get("price")
                                # Get image URL (prioritize first available)
                                if platform_data.get("image_url") and not best_image_url:
                                    best_image_url = platform_data.get("image_url")
                                # Get product link (prioritize first available)
                                if platform_data.get("product_link") and not best_product_link:
                                    best_product_link = platform_data.get("product_link")
                                # Get other fields if not already set
                                if platform_data.get("original_price") and not best_original_price:
                                    best_original_price = platform_data.get("original_price")
                                if platform_data.get("discount") and not best_discount:
                                    best_discount = platform_data.get("discount")
                                if platform_data.get("rating") and not best_rating:
                                    best_rating = platform_data.get("rating")
                                if platform_data.get("brand") and not best_brand:
                                    best_brand = platform_data.get("brand")
                                if platform_data.get("delivery") and not best_delivery:
                                    best_delivery = platform_data.get("delivery")
                                # For Flipkart features
                                if platform_data.get("features") and not best_features:
                                    best_features = platform_data.get("features", [])

                # Ensure required fields exist with defaults
                product_data = {
                    "id": str(product["_id"]),
                    "title": product.get("title", "Unknown Product"),
                    "normalized_title": product.get("normalized_title", product.get("title", "").lower()),
                    "platforms": product.get("platforms", {}),
                    "search_keywords": product.get("search_keywords", []),
                    "created_at": product.get("created_at", datetime.utcnow()),
                    "updated_at": product.get("updated_at", datetime.utcnow()),
                    # Use best available data with fallbacks
                    "price": best_price or "Price not available",
                    "original_price": best_original_price, 
                    "image_url": best_image_url or "",
                    "product_link": best_product_link or "",
                    "rating": best_rating,
                    "discount": best_discount,
                    "brand": best_brand,
                    "delivery": best_delivery,
                    "features": best_features or [],
                }
                
                item_response["product"] = ProductInDB(**product_data)
            else:
                # Create a minimal product if none exists
                item_response["product"] = ProductInDB(
                    title="Product not found",
                    normalized_title="product not found",
                    price="Price not available",
                    image_url="",
                    product_link=""
                )
            
            wishlist_items.append(WishlistItemResponse(**item_response))
        
        logger.info(f"Retrieved wishlist: user={current_user.email}, items={len(wishlist_items)}")
        
        # Debug logging removed for cleaner logs
        
        return wishlist_items
        
    except Exception as e:
        logger.error(f"Failed to get wishlist: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve wishlist"
        )

@router.get("/check/{product_id}")
async def check_in_wishlist(
    product_id: str,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Check if a product is in user's wishlist"""
    db = await get_database()
    
    try:
        # Validate ObjectId
        if not ObjectId.is_valid(product_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid product ID"
            )
        
        # Check if in wishlist
        user_object_id = ObjectId(current_user.id) if current_user.id else None
        if not user_object_id:
            return {"in_wishlist": False}
            
        item = await db.wishlists.find_one({
            "user_id": user_object_id,
            "product_id": ObjectId(product_id)
        })
        
        return {"in_wishlist": item is not None}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to check wishlist: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check wishlist status"
        )