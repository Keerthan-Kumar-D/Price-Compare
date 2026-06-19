# Price Compare

Price Compare is a full-stack product comparison application built for Indian e-commerce searches. The FastAPI backend scrapes Amazon, Flipkart, Myntra, and Meesho, stores product data in MongoDB, and exposes APIs for authentication, wishlist, reports, and saved products; the React + Vite frontend gives users a single interface to search, compare, and track products instead of opening each marketplace separately.

## Scrapers overview

- Amazon scraper: Uses `requests` + `BeautifulSoup` for fast HTML parsing, with automatic retry on failures.
- Flipkart scraper: Uses HTTP requests + BeautifulSoup to extract product images, links, and pricing fields.
- Myntra scraper: Uses Playwright browser automation with product-card selectors to extract fashion-specific fields like brand, discount, and ratings.
- Meesho scraper: Uses Playwright + BeautifulSoup to parse product cards and extract details such as price, discount, reviews, and COD availability.
- Multi-platform endpoint: `/api/scrape/all` runs scrapers concurrently, combines results, caches responses for 5 minutes, and stores data for reporting.

## Project features

- Cross-platform comparison: Search once and compare products from Amazon, Flipkart, Myntra, and Meesho in one response.
- Wishlist management: Logged-in users can add/remove products, keep saved items, and open direct product links from the wishlist.
- Real-time price report: Generate a live report from multi-platform search results and sort/filter by price ranges.
- Lowest-price reporting: Backend report endpoints identify best-priced products and compute discount percentages where original price is available.
- Authentication and user data: JWT-based auth protects user-specific features such as wishlist and saved product actions.
- Caching for speed: Repeated searches return faster using in-memory cache, reducing scraper load and response time.

## Run the project

1. Install backend dependencies (from project root):
   ```bash
   pip install -r requirements.txt
   ```

2. Create a `.env` file in the project root:
   ```env
   MONGODB_URI=mongodb://localhost:27017
   MONGODB_DB_NAME=scraper_db
   JWT_SECRET_KEY=your-secret-key
   ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
   ```

3. Start backend API:
   ```bash
   python app.py
   ```

4. Start frontend (new terminal):
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

5. Open:
   - Frontend: http://localhost:5173
   - API docs: http://localhost:8000/docs