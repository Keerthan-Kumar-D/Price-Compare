from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import IndexModel, TEXT
from pymongo.uri_parser import parse_uri
import os
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger(__name__)

DEFAULT_LOCAL_MONGO_URI = "mongodb://localhost:27017"
DEFAULT_DATABASE_NAME = "scraper_db"

class Database:
    client: AsyncIOMotorClient = None
    database = None

db = Database()

async def get_database():
    return db.database


def _get_env_value(*names: str) -> str | None:
    for name in names:
        value = os.getenv(name)
        if value:
            return value.strip()
    return None


def _resolve_database_name(mongodb_uri: str) -> str:
    configured_name = _get_env_value("MONGODB_DB_NAME")
    if configured_name:
        return configured_name

    try:
        parsed_uri = parse_uri(mongodb_uri)
        database_name = parsed_uri.get("database")
        if database_name:
            return database_name
    except Exception as parse_error:
        logger.debug("Could not parse MongoDB URI for database name: %s", parse_error)

    return DEFAULT_DATABASE_NAME


async def _connect_with_uri(mongodb_uri: str, database_name: str):
    client = AsyncIOMotorClient(mongodb_uri, serverSelectionTimeoutMS=5000)
    await client.admin.command("ping")
    return client, client[database_name]

async def connect_to_mongo():
    """Create database connection"""
    try:
        mongodb_uri = _get_env_value("MONGODB_URI", "MONGODB_URL")

        print("========== MONGO DEBUG ==========")
        print("MONGODB_URI =", mongodb_uri)
        print("=================================")

        mongodb_uri = mongodb_uri or DEFAULT_LOCAL_MONGO_URI
        if not mongodb_uri:
            raise ValueError("MongoDB connection string is not configured")

        database_name = _resolve_database_name(mongodb_uri)

        try:
            db.client, db.database = await _connect_with_uri(mongodb_uri, database_name)
            logger.info("Successfully connected to MongoDB")
        except Exception as primary_error:
            fallback_uri = _get_env_value("MONGODB_FALLBACK_URI") or (
                DEFAULT_LOCAL_MONGO_URI if mongodb_uri != DEFAULT_LOCAL_MONGO_URI else None
            )

            if not fallback_uri:
                raise primary_error

            logger.warning(
                "Primary MongoDB connection failed (%s). Falling back to %s",
                primary_error,
                fallback_uri,
            )
            db.client, db.database = await _connect_with_uri(fallback_uri, database_name)
            logger.info("Successfully connected to fallback MongoDB")

        # Create indexes
        await create_indexes()
        
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise

async def close_mongo_connection():
    """Close database connection"""
    if db.client:
        db.client.close()
        logger.info("Disconnected from MongoDB")

async def create_indexes():
    """Create database indexes for optimal performance"""
    try:
        # Users collection indexes
        await db.database.users.create_index("email", unique=True)
        
        # Products collection indexes
        await db.database.products.create_index([
            ("normalized_title", TEXT),
            ("search_keywords", TEXT)
        ])
        await db.database.products.create_index("platforms.amazon.price")
        await db.database.products.create_index("platforms.flipkart.price")
        await db.database.products.create_index("platforms.reliance_digital.price")
        
        # Wishlists collection indexes
        await db.database.wishlists.create_index([
            ("user_id", 1),
            ("product_id", 1)
        ], unique=True)
        await db.database.wishlists.create_index("user_id")
        
        # Search history collection indexes
        await db.database.search_history.create_index([
            ("user_id", 1),
            ("searched_at", -1)
        ])
        
        logger.info("Database indexes created successfully")
        
    except Exception as e:
        logger.error(f"Failed to create indexes: {e}")
        # Don't raise here as indexes might already exist