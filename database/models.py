from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional, Dict, List, Any
from datetime import datetime
from bson import ObjectId

# User Models
class UserBase(BaseModel):
    email: EmailStr
    name: str

class UserCreate(UserBase):
    password: str = Field(min_length=6, max_length=72)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserInDB(UserBase):
    id: Optional[str] = Field(default=None, alias="_id")
    password: str
    created_at: datetime
    updated_at: datetime
    is_active: bool = True
    last_login: Optional[datetime] = None

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

class UserResponse(UserBase):
    id: str = Field(alias="_id")
    created_at: datetime
    last_login: Optional[datetime] = None

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

# Product Models  
class PlatformData(BaseModel):
    price: Optional[str] = None
    original_price: Optional[str] = None
    product_link: Optional[str] = None
    image_url: Optional[str] = None
    rating: Optional[str] = None
    reviews_count: Optional[str] = None
    last_updated: datetime = Field(default_factory=datetime.utcnow)

class AmazonData(PlatformData):
    delivery: Optional[str] = None

class FlipkartData(PlatformData):
    discount: Optional[str] = None
    ratings_count: Optional[str] = None
    features: List[str] = []
    exchange_offer: Optional[str] = None

class RelianceDigitalData(PlatformData):
    mrp: Optional[str] = None
    discount: Optional[str] = None
    savings: Optional[str] = None
    brand: Optional[str] = None
    special_tag: Optional[str] = None

class ProductPlatforms(BaseModel):
    amazon: Optional[AmazonData] = None
    flipkart: Optional[FlipkartData] = None
    reliance_digital: Optional[RelianceDigitalData] = None

class ProductInDB(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    title: str
    normalized_title: Optional[str] = None
    platforms: Optional[ProductPlatforms] = None
    search_keywords: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    # Add direct fields for wishlist compatibility
    price: Optional[str] = None
    original_price: Optional[str] = None
    image_url: Optional[str] = None
    product_link: Optional[str] = None
    rating: Optional[str] = None
    discount: Optional[str] = None
    brand: Optional[str] = None
    delivery: Optional[str] = None
    features: List[str] = []

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

# Wishlist Models
class WishlistItemCreate(BaseModel):
    product_id: str
    price_alerts: Optional[Dict[str, Any]] = None

class WishlistItemInDB(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    user_id: str
    product_id: str
    added_at: datetime = Field(default_factory=datetime.utcnow)
    price_alerts: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

class WishlistItemResponse(BaseModel):
    id: str = Field(alias="_id")
    product_id: str
    added_at: datetime
    price_alerts: Optional[Dict[str, Any]] = None
    product: Optional[ProductInDB] = None

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

# Report Models
class LowestPriceItem(BaseModel):
    product_name: str
    lowest_price: str
    platform: str
    product_link: str
    image_url: Optional[str] = None
    original_price: Optional[str] = None
    discount: Optional[str] = None

class LowestPriceReport(BaseModel):
    total_products: int
    report_generated_at: datetime
    products: List[LowestPriceItem]

# Token Models
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None