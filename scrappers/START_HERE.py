"""
Quick Start Guide for Myntra Selenium Scraper
==============================================

Follow these simple steps to get started!
"""

print("""
╔══════════════════════════════════════════════════════════════╗
║     MYNTRA SELENIUM SCRAPER - QUICK START GUIDE              ║
╚══════════════════════════════════════════════════════════════╝

📋 Prerequisites:
   ✓ Python installed
   ✓ Google Chrome browser installed
   ✓ All packages installed (already done!)

🚀 STEP 1: Start the Server
   Open a terminal and run:
   
   cd "c:\\Users\\keert\\Desktop\\Scrapper-main - Copy\\scrappers"
   python myntra_selenium_server.py
   
   Wait for: "🚀 Starting Myntra Scraper Server"

🧪 STEP 2: Test the Scraper (in a NEW terminal)
   Open a NEW terminal and run:
   
   cd "c:\\Users\\keert\\Desktop\\Scrapper-main - Copy\\scrappers"
   python test_selenium_client.py
   
   This will:
   - Check server health
   - Search for "mens-tshirts"
   - Display results
   - Save to JSON file

🌐 STEP 3: Try Manual Testing (optional)
   Open your browser and visit:
   
   http://localhost:5000
   
   Or test the search endpoint:
   
   http://localhost:5000/search?q=mens-tshirts

📝 Available Search Queries:
   - mens-tshirts
   - women-dresses
   - shoes
   - mens-jeans
   - womens-tops
   - kids-wear
   - watches
   - bags

⚙️ Important Notes:
   1. Each search takes 20-30 seconds (normal for Selenium)
   2. Chrome browser will open (for debugging)
   3. Don't close the browser manually during scraping
   4. Results are saved to JSON files automatically

🐛 Troubleshooting:
   - If "Connection Refused": Make sure Step 1 is running
   - If "No products found": Myntra may be blocking (try later)
   - If ChromeDriver error: Update Chrome browser

📖 Full Documentation:
   See MYNTRA_SELENIUM_README.md for detailed information

════════════════════════════════════════════════════════════════

Press Enter to start the server now, or Ctrl+C to exit...
""")

try:
    input()
    print("\n🚀 Starting server...\n")
    import subprocess
    subprocess.run(["python", "myntra_selenium_server.py"])
except KeyboardInterrupt:
    print("\n\n👋 Goodbye!")
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nManually run: python myntra_selenium_server.py")
