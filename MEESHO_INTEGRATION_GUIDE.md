# Meesho Integration Guide

## Overview
The Meesho scraper has been successfully integrated into the Price Comparison application. This document provides information about the integration and how to use it.

## What Was Integrated

### 1. Meesho Scraper (`scrappers/meeshoscrapper.py`)
The core scraper that uses Selenium to scrape products from Meesho.

**Features:**
- Selenium-based web scraping (handles JavaScript rendering)
- Product search functionality
- Scrolling to load more products
- Extracts comprehensive product information:
  - Title
  - Current Price
  - Original Price (MRP)
  - Discount percentage
  - Rating
  - Reviews count
  - Delivery information
  - COD availability
  - Product image URL
  - Product link

### 2. Test Script (`scrappers/test_meesho_scraper.py`)
Comprehensive test suite to validate the Meesho scraper functionality.

**Test Cases:**
- ✅ Basic Search Test (with visual browser)
- ✅ Multiple Search Queries Test
- ✅ Context Manager Test
- ✅ Data Export to JSON Test
- ✅ Edge Cases Test

### 3. API Integration (`app.py`)
The Meesho scraper has been integrated into the FastAPI application.

**New Endpoints:**

#### 1. Scrape Meesho Products
```
GET /api/scrape/meesho
```

**Parameters:**
- `query` (required): Search query for products
- `limit` (optional, default=10): Maximum number of products (1-50)
- `scroll_count` (optional, default=3): Number of scrolls to load more products (1-10)

**Example Request:**
```bash
curl "http://localhost:8000/api/scrape/meesho?query=women%20kurta&limit=10&scroll_count=3"
```

**Example Response:**
```json
{
  "platform": "Meesho",
  "search_query": "women kurta",
  "total_products": 10,
  "products": [
    {
      "title": "Beautiful Women Kurta",
      "price": "₹299",
      "original_price": "₹999",
      "discount": "70% OFF",
      "rating": "4.2",
      "reviews_count": "1.2k",
      "delivery": "Free Delivery",
      "cod_available": "COD Available",
      "image_url": "https://...",
      "product_link": "https://www.meesho.com/..."
    }
  ],
  "scraped_at": "2025-11-12T...",
  "status": "success"
}
```

#### 2. Updated Comparison Endpoint
```
GET /api/scrape/all
```

Now includes **5 platforms**: Amazon, Flipkart, Reliance Digital, Myntra, and **Meesho**

**Example Request:**
```bash
curl "http://localhost:8000/api/scrape/all?query=shoes&limit=5"
```

#### 3. Updated Platforms Info
```
GET /api/platforms
```

Now shows Meesho in the supported platforms list.

## How to Test

### Testing the Scraper Directly

1. **Navigate to the scrappers directory:**
```powershell
cd "c:\Users\keert\Desktop\price Compare - Copy\scrappers"
```

2. **Run the test suite:**
```powershell
python test_meesho_scraper.py
```

3. **Run individual tests** (edit the script):
```python
if __name__ == "__main__":
    test_basic_search()  # Run only basic search test
```

### Testing the API

1. **Start the FastAPI server:**
```powershell
cd "c:\Users\keert\Desktop\price Compare - Copy"
python app.py
```

2. **Access the API documentation:**
Open your browser: `http://localhost:8000/docs`

3. **Test Meesho endpoint:**
   - Navigate to `/api/scrape/meesho`
   - Click "Try it out"
   - Enter a search query (e.g., "women kurta")
   - Set limit and scroll_count
   - Click "Execute"

4. **Test comparison endpoint:**
   - Navigate to `/api/scrape/all`
   - Enter a search query
   - See results from all 5 platforms including Meesho

### Testing with Frontend

If you're using the React frontend:

1. **Start the backend:**
```powershell
python app.py
```

2. **Start the frontend:**
```powershell
cd frontend
npm run dev
```

3. **Search for products:**
   - The frontend will automatically query all platforms including Meesho
   - View results in the "Meesho" section

## Performance Notes

### Scraping Speed
- **Meesho scraping takes 10-20 seconds** per request
- Uses Selenium WebDriver for JavaScript rendering
- Runs in headless mode by default for better performance
- Scrolling increases time: each scroll adds ~2 seconds

### Optimization Tips

1. **Reduce scroll_count** for faster results:
```python
# Faster (1 scroll)
GET /api/scrape/meesho?query=shoes&scroll_count=1

# More products but slower (5 scrolls)
GET /api/scrape/meesho?query=shoes&scroll_count=5
```

2. **Use headless mode** (already default):
```python
search_meesho("query", headless=True)  # Faster
```

3. **Set appropriate limits**:
```python
# Get only what you need
GET /api/scrape/meesho?query=shoes&limit=5
```

## Code Examples

### Using the Scraper Directly

```python
from scrappers.meeshoscrapper import search_meesho, MeeshoScraper

# Method 1: Simple function
products = search_meesho("women kurta", headless=True, scroll_count=3)
print(f"Found {len(products)} products")

# Method 2: Using class with context manager
with MeeshoScraper(headless=True) as scraper:
    products = scraper.scrape("men shirt", scroll_count=2)
    print(f"Found {len(products)} products")
```

### Using the API (Python)

```python
import requests

# Search Meesho
response = requests.get(
    "http://localhost:8000/api/scrape/meesho",
    params={
        "query": "women kurta",
        "limit": 10,
        "scroll_count": 3
    }
)
data = response.json()
print(f"Found {data['total_products']} products")

# Compare all platforms
response = requests.get(
    "http://localhost:8000/api/scrape/all",
    params={
        "query": "shoes",
        "limit": 5
    }
)
comparison = response.json()
print(f"Total products across all platforms: {comparison['total_products_found']}")
```

### Using the API (JavaScript/React)

```javascript
// Search Meesho
const searchMeesho = async (query) => {
  const response = await fetch(
    `http://localhost:8000/api/scrape/meesho?query=${encodeURIComponent(query)}&limit=10&scroll_count=3`
  );
  const data = await response.json();
  console.log(`Found ${data.total_products} products`);
  return data.products;
};

// Compare all platforms
const compareAllPlatforms = async (query) => {
  const response = await fetch(
    `http://localhost:8000/api/scrape/all?query=${encodeURIComponent(query)}&limit=5`
  );
  const data = await response.json();
  console.log(`Total: ${data.total_products_found} products`);
  return data.platforms;
};
```

## Troubleshooting

### Common Issues

1. **"No products found" error**
   - Check if the search query is valid
   - Try a different search term
   - Meesho might be blocking automated requests
   - Check your internet connection

2. **ChromeDriver not found**
   ```powershell
   pip install selenium webdriver-manager
   ```

3. **Slow performance**
   - Reduce `scroll_count` parameter
   - Reduce `limit` parameter
   - Use headless mode (already default)

4. **Import errors**
   - Make sure you're in the correct directory
   - Check that `meeshoscrapper.py` exists in the `scrappers/` folder

## File Structure

```
price Compare - Copy/
├── app.py                              # ✅ Updated with Meesho integration
├── scrappers/
│   ├── meeshoscrapper.py              # ✅ Meesho scraper (already existed)
│   └── test_meesho_scraper.py         # ✅ New test script
└── MEESHO_INTEGRATION_GUIDE.md        # ✅ This file
```

## API Documentation

After starting the server, visit these URLs for interactive API documentation:

- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

Both provide interactive testing interfaces where you can try the Meesho endpoints.

## Next Steps

1. **Test the integration:**
   - Run the test script: `python scrappers/test_meesho_scraper.py`
   - Test the API endpoints in the Swagger UI

2. **Update the frontend:**
   - Add Meesho to the platform selector
   - Update the UI to display Meesho results
   - Add Meesho logo/branding

3. **Monitor performance:**
   - Track scraping times
   - Optimize scroll_count based on results
   - Consider caching frequently searched queries

4. **Handle edge cases:**
   - Add retry logic for failed requests
   - Implement rate limiting
   - Add better error messages

## Support

For issues or questions:
1. Check the test script output for detailed error messages
2. Review the API logs in the terminal
3. Check the Swagger UI documentation at `/docs`

---

**Integration Date:** November 12, 2025  
**Meesho Scraper Version:** 1.0.0  
**API Version:** 1.0.0
