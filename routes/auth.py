from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime
from database.models import UserCreate, UserLogin, UserResponse, Token, UserInDB
from database.connection import get_database
from auth.security import get_password_hash, verify_password, create_access_token, get_current_active_user
from pymongo.errors import DuplicateKeyError
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(user_data: UserCreate):
    """Create a new user account"""
    db = await get_database()
    
    try:
        # Validate input
        if len(user_data.password) < 6:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 6 characters long"
            )
        
        if len(user_data.password) > 72:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password is too long (max 72 characters)"
            )
        
        # Check if user already exists
        existing_user = await db.users.find_one({"email": user_data.email})
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash password
        hashed_password = get_password_hash(user_data.password)
        
        # Create user document
        user_doc = {
            "email": user_data.email,
            "name": user_data.name,
            "password": hashed_password,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "is_active": True,
            "last_login": None
        }
        
        # Insert user into database
        result = await db.users.insert_one(user_doc)
        
        # Retrieve the created user to return proper response
        created_user = await db.users.find_one({"_id": result.inserted_id})
        if not created_user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="User was created but could not be retrieved"
            )
        
        # Convert ObjectId to string for JSON response
        created_user["_id"] = str(created_user["_id"])
        
        logger.info(f"New user created: {user_data.email}")
        return UserResponse(**created_user)
        
    except HTTPException:
        raise
    except DuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    except Exception as e:
        logger.error(f"Failed to create user: {e}")
        logger.error(f"Error type: {type(e)}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user account: {str(e)}"
        )

@router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin):
    """Authenticate user and return JWT token"""
    db = await get_database()
    
    try:
        # Find user by email
        user = await db.users.find_one({"email": user_credentials.email})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Verify password
        if not verify_password(user_credentials.password, user["password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check if user is active
        if not user.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is disabled"
            )
        
        # Update last login
        await db.users.update_one(
            {"_id": user["_id"]},
            {"$set": {"last_login": datetime.utcnow()}}
        )
        
        # Create access token
        access_token = create_access_token(data={"sub": user["email"]})
        
        logger.info(f"User logged in: {user_credentials.email}")
        return Token(access_token=access_token, token_type="bearer")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: UserInDB = Depends(get_current_active_user)):
    """Get current user's profile information"""
    return UserResponse(**current_user.dict())

@router.post("/logout")
async def logout():
    """Logout user (client should remove token)"""
    # Note: With JWT, actual logout is handled on the client side
    # by removing the token from storage
    return {"message": "Successfully logged out"}

@router.get("/verify-token")
async def verify_token_endpoint(current_user: UserInDB = Depends(get_current_active_user)):
    """Verify if the current token is valid"""
    return {"valid": True, "user": UserResponse(**current_user.dict())}