# Myntra Selenium Scraper

A Flask-based web scraper for Myntra using Selenium WebDriver to handle JavaScript-rendered content.

## 📋 Overview

This scraper uses Selenium with Chrome WebDriver to scrape product data from Myntra, which requires JavaScript rendering. It provides a REST API to search for products.

## 🚀 Setup

### 1. Install Dependencies

```powershell
pip install -r selenium_requirements.txt
```

This will install:
- Flask (web server)
- Flask-CORS (cross-origin support)
- Selenium (browser automation)
- webdriver-manager (automatic ChromeDriver management)
- requests (HTTP client for testing)

### 2. Install Chrome Browser

Make sure Google Chrome is installed on your system. The webdriver-manager will automatically download the appropriate ChromeDriver.

## 📖 Usage

### Starting the Server

Run the server:

```powershell
python myntra_selenium_server.py
```

The server will start on `http://localhost:5000`

You should see:
```
============================================================
🚀 Starting Myntra Scraper Server
============================================================
Server: http://localhost:5000
Browser will open when scraping (for debugging)
============================================================
```

### Testing with the Client

In a separate terminal, run the test client:

```powershell
python test_selenium_client.py
```

This will:
1. Check if the server is running
2. Send a search request for "mens-tshirts"
3. Display the results
4. Save results to a JSON file

### Manual Testing

You can also test the API manually:

#### Check Server Health
```powershell
curl http://localhost:5000/health
```

#### Search for Products
```powershell
curl "http://localhost:5000/search?q=mens-tshirts"
```

Or open in your browser:
```
http://localhost:5000/search?q=mens-tshirts
```

## 🔧 API Endpoints

### GET /
Returns a simple HTML page with API documentation

### GET /health
Check if server is running

**Response:**
```json
{
  "status": "ok",
  "message": "Server is running"
}
```

### GET /search?q={query}
Search for products on Myntra

**Parameters:**
- `q` (required): Search query (e.g., "mens-tshirts", "women-dresses", "shoes")

**Response:**
```json
{
  "query": "mens-tshirts",
  "count": 12,
  "products": [
    {
      "brand": "Nike",
      "title": "Men Printed T-shirt",
      "price": "₹999",
      "original_price": "₹1999",
      "discount": "50% OFF",
      "rating": "4.5",
      "reviews_count": "1.2k",
      "image_url": "https://...",
      "product_link": "https://www.myntra.com/..."
    }
  ]
}
```

## 🎯 Search Query Examples

Common search queries:
- `mens-tshirts`
- `women-dresses`
- `shoes`
- `mens-jeans`
- `womens-tops`
- `kids-wear`
- `watches`
- `bags`

## ⚙️ Configuration

### Headless Mode

By default, the browser opens visibly for debugging. To run in headless mode, edit `myntra_selenium_server.py`:

```python
def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Uncomment this line
    # ... rest of the options
```

### Maximum Products

Change the number of products to scrape (default: 12):

```python
products = scrape_myntra(query, max_products=20)  # Scrape 20 products
```

### Timeout Settings

Adjust wait times in the `scrape_myntra()` function:

```python
time.sleep(5)  # Initial page load wait
time.sleep(2)  # Wait between scrolls
```

## 🐛 Troubleshooting

### "No products found"
- Myntra may be blocking automated requests
- Try disabling headless mode to see what's happening
- Check if the CSS selectors have changed
- Verify your internet connection

### ChromeDriver Issues
- Make sure Chrome browser is installed
- webdriver-manager should auto-download the correct driver
- If issues persist, manually specify ChromeDriver path:
  ```python
  service = Service('/path/to/chromedriver')
  ```

### Connection Refused
- Make sure the server is running on port 5000
- Check if another application is using port 5000
- Change the port in the code if needed:
  ```python
  app.run(debug=True, host='0.0.0.0', port=5001)
  ```

### Slow Performance
- Selenium is slower than requests-based scraping (intentional for JavaScript)
- Each search takes 20-30 seconds
- This is normal behavior for rendering JavaScript content

## 📊 Output Files

The test client saves results to JSON files:
- `selenium_mens-tshirts_results.json`
- `selenium_women-dresses_results.json`
- etc.

Format:
```json
{
  "query": "mens-tshirts",
  "count": 12,
  "products": [...]
}
```

## ⚠️ Important Notes

1. **Rate Limiting**: Don't make too many requests in a short time. Myntra may block your IP.

2. **Legal Compliance**: Ensure your scraping complies with Myntra's Terms of Service and robots.txt.

3. **Dynamic Content**: This scraper handles JavaScript-rendered content, which is why it uses Selenium.

4. **Resource Usage**: Selenium opens a real browser, so it uses more CPU and memory than simple HTTP requests.

5. **Browser Visibility**: The browser opens visibly by default for debugging. Enable headless mode for production.

## 🔄 Comparison with BeautifulSoup Scraper

| Feature | Selenium Scraper | BeautifulSoup Scraper |
|---------|------------------|----------------------|
| JavaScript Support | ✅ Yes | ❌ No |
| Speed | 🐢 Slower (20-30s) | 🚀 Faster (2-3s) |
| Resource Usage | 💾 High | 💾 Low |
| Success Rate | ✅ Higher | ⚠️ Lower for Myntra |
| Browser Required | ✅ Chrome | ❌ None |

## 📝 Files

- `myntra_selenium_server.py` - Flask server with Selenium scraper
- `test_selenium_client.py` - Test client to interact with the server
- `selenium_requirements.txt` - Python dependencies
- `MYNTRA_SELENIUM_README.md` - This file

## 🎓 Next Steps

1. **Integration**: Integrate this scraper into your main application
2. **Caching**: Add Redis caching to avoid repeated scrapes
3. **Queue System**: Use Celery for asynchronous scraping
4. **Proxy Support**: Add proxy rotation to avoid IP blocks
5. **Error Handling**: Add retry logic and better error messages

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section
2. Verify all dependencies are installed
3. Ensure Chrome browser is up to date
4. Check the console output for error messages
