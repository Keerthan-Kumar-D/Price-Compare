# 🛒 E-Commerce Scraper REST API

A FastAPI-based REST API for scraping products from major Indian e-commerce platforms including Amazon, Flipkart, Myntra, Meesho, and Reliance Digital. Perfect for React.js frontend integration with structured JSON responses.

## 🚀 Features

- **Multi-Platform Support**: Amazon, Flipkart, Myntra, Meesho, and Reliance Digital
- **RESTful API**: Clean, standardized endpoints
- **JSON Responses**: React.js friendly data format
- **CORS Enabled**: Ready for frontend integration
- **Async Support**: Concurrent scraping for better performance
- **Error Handling**: Comprehensive error management
- **Interactive Docs**: Auto-generated API documentation
- **Type Safety**: Pydantic models for data validation

## 📋 Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [API Endpoints](#api-endpoints)
- [Data Models](#data-models)
- [Authentication](#authentication)
- [Frontend Integration](#frontend-integration)
- [Error Handling](#error-handling)
- [Development](#development)

## 💾 Installation

### Prerequisites
- Python 3.8+
- pip package manager
- Google Chrome browser (for Selenium-based scrapers)

### Setup

1. **Clone/Navigate to project directory**
   ```bash
   cd "mini project - Copy"
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   
   For Selenium-based scrapers (Myntra, Meesho, Flipkart), Chrome WebDriver will be automatically downloaded by webdriver-manager.

3. **Configure Environment Variables**
   Create a `.env` file in the project root:
   ```env
   # MongoDB Configuration
  MONGODB_URI=mongodb://localhost:27017
   MONGODB_DB_NAME=ecommerce_scraper
  # Optional fallback if Atlas SRV resolution fails
  # MONGODB_FALLBACK_URI=mongodb://localhost:27017
   
   # JWT Secret Key (generate a secure random key)
   SECRET_KEY=your-secret-key-here
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   
   # CORS Origins (comma-separated)
   ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
   ```

4. **Run the API server**
   ```bash
   python app.py
   ```
   
   Or using uvicorn directly:
   ```bash
   uvicorn app:app --host 0.0.0.0 --port 8000 --reload
   ```

5. **Access the API**
   - API Base URL: `http://localhost:8000`
   - Interactive Docs: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

## 🚀 Quick Start

### Test the API
```bash
# Health check
curl http://localhost:8000/

# Scrape Amazon for laptops
curl "http://localhost:8000/api/scrape/amazon?query=laptop&limit=5"

# Compare all platforms
curl "http://localhost:8000/api/scrape/all?query=smartphone&limit=3"
```

## 📡 API Endpoints

### Health & Information

#### `GET /` - Health Check
Basic health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "message": "E-Commerce Scraper API is running",
  "timestamp": "2026-02-23T10:30:00.123456",
  "version": "2.0.0"
}
```

#### `GET /health` - Detailed Health Check
Detailed health information.

#### `GET /api/platforms` - Supported Platforms
Get list of all supported platforms and their capabilities.

**Response:**
```json
{
  "platforms": [
    {
      "name": "Amazon",
      "endpoint": "/api/scrape/amazon",
      "status": "fully_supported",
      "features": ["prices", "ratings", "reviews", "delivery_info"]
    }
  ],
  "comparison_endpoint": "/api/scrape/all",
  "total_platforms": 5
}
```

### Scraping Endpoints

#### `GET /api/scrape/amazon` - Amazon Scraper
Scrape products from Amazon.

**Parameters:**
- `query` (required): Search term for products
- `limit` (optional): Max products to return (1-50, default: 10)

**Example:**
```bash
GET /api/scrape/amazon?query=laptop&limit=5
```

**Response:**
```json
{
  "platform": "Amazon",
  "search_query": "laptop",
  "total_products": 5,
  "products": [
    {
      "title": "Apple MacBook Air M2",
      "price": "₹99,900",
      "original_price": "₹1,19,900",
      "rating": "4.5",
      "reviews_count": "1,234",
      "delivery": "FREE delivery by tomorrow",
      "image_url": "https://m.media-amazon.com/images/I/71jG+e7roXL._AC_UY327_FMwebp_QL65_.jpg",
      "product_link": "https://www.amazon.in/dp/B0B3C57R1F"
    }
  ],
  "scraped_at": "2026-02-23T10:30:00.123456",
  "status": "success"
}
```

#### `GET /api/scrape/flipkart` - Flipkart Scraper
Scrape products from Flipkart.

**Parameters:**
- `query` (required): Search term for products
- `limit` (optional): Max products to return (1-50, default: 10)

**Example:**
```bash
GET /api/scrape/flipkart?query=smartphone&limit=3
```

**Response:**
```json
{
  "platform": "Flipkart",
  "search_query": "smartphone",
  "total_products": 3,
  "products": [
    {
      "title": "iPhone 15 Pro Max",
      "price": "₹1,34,900",
      "original_price": "₹1,59,900",
      "discount": "15% off",
      "rating": "4.6",
      "reviews_count": "2,847",
      "ratings_count": "12,534",
      "features": ["256GB Storage", "A17 Pro Chip", "48MP Camera"],
      "exchange_offer": "₹25,000 off on exchange",
      "image_url": "https://rukminim2.flixcart.com/image/312/312/xif0q/mobile/3/5/l/iphone-15-pro-max-mh2q3hn-a-apple-original-imaghx9qygjjg8tg.jpeg",
      "product_link": "https://www.flipkart.com/apple-iphone-15-pro-max-blue-titanium-256-gb/p/itm49de5e9d4d9c6"
    }
  ],
  "scraped_at": "2026-02-23T10:30:00.123456",
  "status": "success"
}
```

#### `GET /api/scrape/myntra` - Myntra Scraper
Scrape products from Myntra using Selenium WebDriver.

**Parameters:**
- `query` (required): Search term for products
- `limit` (optional): Max products to return (1-50, default: 10)

**Example:**
```bash
GET /api/scrape/myntra?query=tshirt&limit=5
```

**Response:**
```json
{
  "platform": "Myntra",
  "search_query": "tshirt",
  "total_products": 5,
  "products": [
    {
      "title": "Roadster Men Solid Casual T-shirt",
      "brand": "Roadster",
      "price": "₹499",
      "original_price": "₹1,299",
      "discount": "62% OFF",
      "rating": "4.2",
      "reviews_count": "12.5k",
      "image_url": "https://assets.myntassets.com/h_720,q_90,w_540/v1/assets/images/2060413/2017/9/14/11505387708574-Roadster-Men-Tshirts-371505387708403-1.jpg",
      "product_link": "https://www.myntra.com/tshirts/roadster/roadster-men-solid-casual-t-shirt/2060413/buy"
    }
  ],
  "scraped_at": "2026-02-23T10:30:00.123456",
  "status": "success"
}
```

**Note:** Uses Selenium to handle JavaScript rendering. Takes 20-30 seconds per request.

#### `GET /api/scrape/meesho` - Meesho Scraper
Scrape products from Meesho using Selenium WebDriver.

**Parameters:**
- `query` (required): Search term for products
- `limit` (optional): Max products to return (1-50, default: 10)
- `scroll_count` (optional): Number of scrolls to load more products (1-10, default: 3)

**Example:**
```bash
GET /api/scrape/meesho?query=saree&limit=5&scroll_count=3
```

**Response:**
```json
{
  "platform": "Meesho",
  "search_query": "saree",
  "total_products": 5,
  "products": [
    {
      "title": "Attractive Banarasi Silk Saree",
      "price": "₹599",
      "original_price": "₹2,999",
      "discount": "80% off",
      "rating": "4.1",
      "reviews_count": "234",
      "delivery": "Free Delivery",
      "cod_available": "Cash on Delivery available",
      "image_url": "https://images.meesho.com/images/products/123456/1_512.jpg",
      "product_link": "https://www.meesho.com/attractive-banarasi-silk-saree/p/123456"
    }
  ],
  "scraped_at": "2026-02-23T10:30:00.123456",
  "status": "success"
}
```

**Note:** Uses Selenium to handle JavaScript rendering. Takes 10-20 seconds per request.

#### `GET /api/scrape/reliance-digital` - Reliance Digital Scraper
Scrape products from Reliance Digital.

**Parameters:**
- `query` (required): Search term for products
- `limit` (optional): Max products to return (1-50, default: 10)

**Note:** This platform uses JavaScript rendering, so results may be limited.

#### `GET /api/scrape/all` - Multi-Platform Comparison
Scrape products from all platforms (Amazon, Flipkart, Myntra, Meesho, Reliance Digital) simultaneously.

**Parameters:**
- `query` (required): Search term for products
- `limit` (optional): Max products per platform (1-20, default: 5)

**Note:** Results are cached for 5 minutes to improve performance.

**Example:**
```bash
GET /api/scrape/all?query=headphones&limit=3
```

**Response:**
```json
{
  "search_query": "headphones",
  "platforms": {
    "amazon": {
      "platform": "Amazon",
      "total_products": 3,
      "products": [...],
      "status": "success"
    },
    "flipkart": {
      "platform": "Flipkart", 
      "total_products": 3,
      "products": [...],
      "status": "success"
    },
    "myntra": {
      "platform": "Myntra",
      "total_products": 2,
      "products": [...],
      "status": "success"
    },
    "meesho": {
      "platform": "Meesho",
      "total_products": 3,
      "products": [...],
      "status": "success"
    },
    "reliance_digital": {
      "platform": "Reliance Digital",
      "total_products": 1,
      "products": [...],
      "status": "partial",
      "message": "This platform uses JavaScript rendering..."
    }
  },
  "total_products_found": 12,
  "scraped_at": "2026-02-23T10:30:00.123456"
}
```

## 📊 Data Models

### Product Model
```typescript
interface Product {
  title: string;                    // Product name
  price: string;                    // Current price
  original_price?: string;          // Original/MRP price
  discount?: string;                // Discount percentage
  rating?: string;                  // Star rating
  reviews_count?: string;           // Number of reviews
  ratings_count?: string;           // Number of ratings
  delivery?: string;                // Delivery information
  features?: string[];              // Product features list
  exchange_offer?: string;          // Exchange offer details
  mrp?: string;                     // Maximum retail price
  savings?: string;                 // Amount saved
  special_tag?: string;             // Special tags/badges
  brand?: string;                   // Brand name
  image_url?: string;               // Product image URL
  product_link?: string;            // Direct link to product page
  cod_available?: string;           // Cash on Delivery status (Meesho)
}
```

### Scraping Response Model
```typescript
interface ScrapingResponse {
  platform: string;                // Platform name
  search_query: string;             // Search term used
  total_products: number;           // Number of products found
  products: Product[];              // Array of products
  scraped_at: string;              // ISO timestamp
  status: "success" | "partial" | "error";
  message?: string;                 // Optional status message
}
```

### Comparison Response Model
```typescript
interface ComparisonResponse {
  search_query: string;             // Search term used
  platforms: {                     // Results from each platform
    amazon: ScrapingResponse;
    flipkart: ScrapingResponse;
    myntra: ScrapingResponse;
    meesho: ScrapingResponse;
    reliance_digital: ScrapingResponse;
  };
  total_products_found: number;     // Total across all platforms
  scraped_at: string;              // ISO timestamp
}
```

## 🔐 Authentication

The API includes JWT-based authentication for user management and protected features.

### Authentication Endpoints

#### Register User
```bash
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123",
  "full_name": "John Doe"
}
```

#### Login
```bash
POST /auth/login
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=securepassword123
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

### Protected Features
- **Wishlist**: Save favorite products
- **Price Tracking**: Monitor product prices
- **Reports**: Generate shopping reports

### Database
- **MongoDB**: Used for storing user data, wishlists, and product history
- **Motor**: Async MongoDB driver for FastAPI

## ⚛️ Frontend Integration (React.js)

### Basic Usage

```javascript
// Fetch products from Amazon
const fetchAmazonProducts = async (query, limit = 10) => {
  try {
    const response = await fetch(
      `http://localhost:8000/api/scrape/amazon?query=${encodeURIComponent(query)}&limit=${limit}`
    );
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching Amazon products:', error);
    throw error;
  }
};

// Compare all platforms
const compareAllPlatforms = async (query, limit = 5) => {
  try {
    const response = await fetch(
      `http://localhost:8000/api/scrape/all?query=${encodeURIComponent(query)}&limit=${limit}`
    );
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error comparing platforms:', error);
    throw error;
  }
};
```

### React Component Example

```jsx
import React, { useState, useEffect } from 'react';

const ProductSearch = () => {
  const [query, setQuery] = useState('');
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [platform, setPlatform] = useState('amazon');

  const searchProducts = async () => {
    setLoading(true);
    try {
      const response = await fetch(
        `http://localhost:8000/api/scrape/${platform}?query=${encodeURIComponent(query)}&limit=10`
      );
      const data = await response.json();
      setProducts(data.products);
    } catch (error) {
      console.error('Search failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div>
        <input 
          type="text" 
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search products..."
        />
        <select value={platform} onChange={(e) => setPlatform(e.target.value)}>
          <option value="amazon">Amazon</option>
          <option value="flipkart">Flipkart</option>
          <option value="myntra">Myntra</option>
          <option value="meesho">Meesho</option>
          <option value="reliance-digital">Reliance Digital</option>
        </select>
        <button onClick={searchProducts} disabled={loading}>
          {loading ? 'Searching...' : 'Search'}
        </button>
      </div>
      
      <div>
        {products.map((product, index) => (
          <div key={index} style={{ border: '1px solid #ccc', margin: '10px', padding: '10px' }}>
            {product.image_url && (
              <img 
                src={product.image_url} 
                alt={product.title}
                style={{ width: '100px', height: '100px', objectFit: 'cover' }}
              />
            )}
            <h3>
              {product.product_link ? (
                <a href={product.product_link} target="_blank" rel="noopener noreferrer">
                  {product.title}
                </a>
              ) : (
                product.title
              )}
            </h3>
            <p>Price: {product.price}</p>
            {product.original_price && <p>Original: {product.original_price}</p>}
            {product.rating && <p>Rating: {product.rating} ⭐</p>}
            {product.discount && <p>Discount: {product.discount}</p>}
            {product.exchange_offer && <p>Exchange: {product.exchange_offer}</p>}
            {product.delivery && <p>Delivery: {product.delivery}</p>}
          </div>
        ))}
      </div>
    </div>
  );
};

export default ProductSearch;
```

### TypeScript Interfaces

```typescript
// types/api.ts
export interface Product {
  title: string;
  price: string;
  original_price?: string;
  discount?: string;
  rating?: string;
  reviews_count?: string;
  ratings_count?: string;
  delivery?: string;
  features?: string[];
  exchange_offer?: string;
  mrp?: string;
  savings?: string;
  special_tag?: string;
  brand?: string;
  image_url?: string;
  product_link?: string;
  cod_available?: string;  // For Meesho
}

export interface ScrapingResponse {
  platform: string;
  search_query: string;
  total_products: number;
  products: Product[];
  scraped_at: string;
  status: 'success' | 'partial' | 'error';
  message?: string;
}

export interface ComparisonResponse {
  search_query: string;
  platforms: {
    amazon: ScrapingResponse;
    flipkart: ScrapingResponse;
    myntra: ScrapingResponse;
    meesho: ScrapingResponse;
    reliance_digital: ScrapingResponse;
  };
  total_products_found: number;
  scraped_at: string;
}
```

## ❌ Error Handling

### HTTP Status Codes
- `200` - Success
- `422` - Validation Error (invalid parameters)
- `500` - Internal Server Error (scraping failed)

### Error Response Format
```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common Errors
1. **Invalid Query**: Empty or too short search query
2. **Limit Out of Range**: Limit parameter outside allowed range
3. **Scraping Failed**: Network issues or website changes
4. **Timeout**: Request took too long to complete

## 🔧 Development

### Project Structure
```
mini project - Copy/
├── app.py                          # FastAPI application
├── main.py                         # Original CLI script
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── auth/                           # Authentication modules
├── database/                       # MongoDB connection and models
├── routes/                         # API routes (auth, wishlist, reports)
├── utils/                          # Utility functions (cache, product_utils)
├── frontend/                       # React.js frontend application
└── scrappers/
    ├── __init__.py                 # Package initialization
    ├── amazonScrapper.py          # Amazon scraper logic
    ├── flipkarScrapper.py         # Flipkart scraper (basic)
    ├── flipkart_selenium.py       # Flipkart scraper (Selenium)
    ├── myntra_selenium.py         # Myntra scraper (Selenium)
    ├── meeshoscrapper.py          # Meesho scraper (Selenium)
    ├── relianceDigitalScrapper.py # Reliance Digital scraper logic
    └── selenium_requirements.txt  # Selenium-specific dependencies
```

### Running in Development Mode
```bash
# With auto-reload
uvicorn app:app --reload --host 0.0.0.0 --port 8000

# With specific log level
uvicorn app:app --reload --log-level debug
```

### Testing Endpoints
Use the interactive documentation at `http://localhost:8000/docs` to test all endpoints directly in the browser.

### Adding New Platforms
1. Create a new scraper in `scrappers/` directory
2. Add import in `app.py`
3. Create new endpoint following the existing pattern
4. Update the `/api/platforms` endpoint
5. Add platform to comparison endpoint

## 📝 API Response Examples

### Successful Amazon Response
```json
{
  "platform": "Amazon",
  "search_query": "wireless mouse",
  "total_products": 3,
  "products": [
    {
      "title": "Logitech MX Master 3S",
      "price": "₹8,995",
      "original_price": "₹10,995",
      "rating": "4.4",
      "reviews_count": "2,847",
      "delivery": "FREE delivery tomorrow",
      "image_url": "https://m.media-amazon.com/images/I/61ni3t1ryQL._AC_UY327_FMwebp_QL65_.jpg",
      "product_link": "https://www.amazon.in/dp/B09HM94VXP"
    }
  ],
  "scraped_at": "2026-02-23T15:30:45.123456",
  "status": "success"
}
```

### Error Response
```json
{
  "detail": "Amazon scraping failed: Connection timeout"
}
```

## 🚦 Rate Limiting & Best Practices

### Recommendations
- **Implement Caching**: Cache responses for frequently searched terms
- **Rate Limiting**: Add rate limiting to prevent abuse
- **Retry Logic**: Implement exponential backoff for failed requests
- **Monitoring**: Add logging and monitoring for production use
- **CORS**: Configure CORS origins for production deployment

### Production Considerations
```python
# Add rate limiting
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.get("/api/scrape/amazon")
@limiter.limit("10/minute")
async def scrape_amazon(request: Request, ...):
    # Implementation
```

## 📞 Support & Contributing

### Platform Status
- ✅ **Amazon**: Fully functional with comprehensive data extraction
- ✅ **Flipkart**: Fully functional with Selenium support for consistent image loading
- ✅ **Myntra**: Fully functional using Selenium WebDriver for JavaScript rendering
- ✅ **Meesho**: Fully functional using Selenium WebDriver with dynamic scrolling
- ⚠️ **Reliance Digital**: Basic functionality, JavaScript rendering required for complete data

### Known Limitations
- Reliance Digital requires JavaScript rendering tools for full functionality
- Some platforms may have anti-bot measures
- Product availability and structure may change
- Selenium-based scrapers (Myntra, Meesho, Flipkart) take longer (10-30 seconds) due to browser automation

## \ud83d\ude80 Performance & Caching

### Response Times
- **Amazon**: ~2-3 seconds (BeautifulSoup)
- **Flipkart**: ~10-15 seconds (Selenium)
- **Myntra**: ~20-30 seconds (Selenium)
- **Meesho**: ~10-20 seconds (Selenium)
- **Reliance Digital**: ~2-3 seconds (BeautifulSoup, limited data)
- **Multi-Platform (All)**: ~30-40 seconds (cached for 5 minutes)

### Caching
Results from `/api/scrape/all` are automatically cached for 5 minutes to improve performance for repeated queries.

## \ud83d\udd27 Selenium Setup

The project uses Selenium for platforms that heavily rely on JavaScript rendering (Myntra, Meesho, Flipkart images).

### Requirements
- Google Chrome browser must be installed
- ChromeDriver is automatically managed by `webdriver-manager`
- No manual driver setup needed

### Headless Mode
All Selenium scrapers run in headless mode by default for better performance and server compatibility.

### Future Enhancements
- Add more e-commerce platforms
- Implement caching layer
- Add user authentication
- Create rate limiting
- Add product tracking and alerts
- WebSocket support for real-time updates

---

**🚀 Ready to integrate with your React.js frontend!** 

Use the comprehensive JSON API to build powerful e-commerce comparison applications with real-time product data from multiple platforms.