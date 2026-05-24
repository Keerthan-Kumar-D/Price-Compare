# Quick Start - Meesho Integration

## 🚀 Quick Start Guide

### 1️⃣ Test the Meesho Scraper (Standalone)

```powershell
# Navigate to scrappers directory
cd "c:\Users\keert\Desktop\price Compare - Copy\scrappers"

# Run the test suite
python test_meesho_scraper.py
```

**Expected Output:**
```
================================================================================
MEESHO SCRAPER TEST SUITE
================================================================================
...
✓ PASSED: Basic Search
✓ PASSED: Multiple Searches
✓ PASSED: Context Manager
✓ PASSED: Data Export
✓ PASSED: Edge Cases
--------------------------------------------------------------------------------
Total: 5/5 tests passed
```

---

### 2️⃣ Start the FastAPI Server

```powershell
# Navigate to project root
cd "c:\Users\keert\Desktop\price Compare - Copy"

# Start the server
python app.py
```

**Server should start at:** `http://localhost:8000`

---

### 3️⃣ Test the Meesho API Endpoint

#### Option A: Using Swagger UI (Recommended)
1. Open browser: `http://localhost:8000/docs`
2. Find `/api/scrape/meesho` endpoint
3. Click "Try it out"
4. Enter:
   - **query:** `women kurta`
   - **limit:** `10`
   - **scroll_count:** `3`
5. Click "Execute"
6. View results below

#### Option B: Using cURL
```powershell
curl "http://localhost:8000/api/scrape/meesho?query=women%20kurta&limit=10&scroll_count=3"
```

#### Option C: Using PowerShell
```powershell
$response = Invoke-RestMethod -Uri "http://localhost:8000/api/scrape/meesho?query=women%20kurta&limit=10&scroll_count=3" -Method Get
$response | ConvertTo-Json -Depth 10
```

---

### 4️⃣ Test the All Platforms Comparison

```powershell
# Compare prices across all 5 platforms (including Meesho)
curl "http://localhost:8000/api/scrape/all?query=shoes&limit=5"
```

Or in Swagger UI: `/api/scrape/all`

---

## 📋 Quick API Reference

### Meesho Endpoint
```
GET /api/scrape/meesho
```

**Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| query | string | ✅ Yes | - | Search query |
| limit | integer | ❌ No | 10 | Max products (1-50) |
| scroll_count | integer | ❌ No | 3 | Scrolls to load more (1-10) |

### All Platforms Comparison
```
GET /api/scrape/all
```

**Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| query | string | ✅ Yes | - | Search query |
| limit | integer | ❌ No | 5 | Max products per platform (1-20) |

### Platforms Info
```
GET /api/platforms
```

Returns info about all 5 supported platforms including Meesho.

---

## 🧪 Sample Queries

### Good Test Queries:
- `women kurta` - Good variety of results
- `men shirt` - Popular category
- `shoes` - Lots of products
- `mobile cover` - Electronics accessories
- `saree` - Traditional wear
- `backpack` - Bags category

### Quick Performance Test:
```powershell
# Fast (1 scroll, 5 products)
curl "http://localhost:8000/api/scrape/meesho?query=shoes&limit=5&scroll_count=1"

# Slower but more products (5 scrolls, 20 products)
curl "http://localhost:8000/api/scrape/meesho?query=shoes&limit=20&scroll_count=5"
```

---

## ✅ Verification Checklist

- [ ] Test script runs successfully
- [ ] FastAPI server starts without errors
- [ ] Swagger UI accessible at `/docs`
- [ ] Meesho endpoint returns products
- [ ] All platforms comparison includes Meesho
- [ ] Platforms info shows 5 platforms

---

## 🎯 What's Included

### ✅ Files Created/Modified:
1. **`scrappers/test_meesho_scraper.py`** - New test script
2. **`app.py`** - Updated with Meesho integration
3. **`MEESHO_INTEGRATION_GUIDE.md`** - Full documentation
4. **`MEESHO_QUICKSTART.md`** - This quick start guide

### ✅ Features Added:
- ✅ Meesho scraper endpoint
- ✅ Meesho in all-platforms comparison
- ✅ Meesho in platforms info
- ✅ Comprehensive test suite
- ✅ Support for COD and delivery info
- ✅ Async support for better performance

### ✅ Platforms Supported (5 total):
1. Amazon
2. Flipkart
3. Reliance Digital
4. Myntra
5. **Meesho** ⭐ NEW

---

## 🔥 One-Command Test

Run everything in sequence:

```powershell
# Test scraper, start server, and open docs
cd "c:\Users\keert\Desktop\price Compare - Copy\scrappers" ; python test_meesho_scraper.py ; cd .. ; Start-Process "http://localhost:8000/docs" ; python app.py
```

---

## 💡 Pro Tips

1. **Use headless mode** (already default) for faster scraping
2. **Reduce scroll_count** if you need quick results
3. **Use Swagger UI** for easy API testing
4. **Check logs** in terminal for detailed error messages
5. **Start with small limits** when testing

---

## 🚨 Common Issues

### Issue: ChromeDriver not found
```powershell
pip install selenium webdriver-manager
```

### Issue: Module not found
```powershell
cd "c:\Users\keert\Desktop\price Compare - Copy"
# Make sure you're in the root directory
```

### Issue: Port already in use
```powershell
# Kill the process using port 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

---

## 📚 Next Steps

1. ✅ Test the integration
2. 📱 Update frontend to show Meesho results
3. 🎨 Add Meesho branding/logo
4. 🔄 Implement caching for better performance
5. 📊 Add analytics for Meesho scraping

---

**Ready to go!** 🎉

Start with step 1 (test script) to verify everything works.
