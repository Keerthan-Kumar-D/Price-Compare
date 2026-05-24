"""
Simple error check for Meesho scraper
"""
import sys
import traceback

print("=" * 60)
print("CHECKING FOR ERRORS")
print("=" * 60)

# Check if selenium is installed
try:
    import selenium
    print("✓ Selenium installed: version", selenium.__version__)
except ImportError as e:
    print("✗ Selenium not installed!")
    print("  Install with: pip install selenium")
    sys.exit(1)

# Check if we can import from scrappers
try:
    sys.path.insert(0, 'scrappers')
    print("\n✓ Added scrappers to path")
except Exception as e:
    print(f"✗ Error adding path: {e}")

# Try to import the scraper
try:
    from meeshoscrapper import search_meesho, MeeshoScraper
    print("✓ Successfully imported MeeshoScraper")
except ImportError as e:
    print(f"✗ Import error: {e}")
    traceback.print_exc()
    sys.exit(1)
except Exception as e:
    print(f"✗ Unexpected error: {e}")
    traceback.print_exc()
    sys.exit(1)

# Try to create an instance
try:
    print("\nTrying to create MeeshoScraper instance...")
    scraper = MeeshoScraper(headless=True)
    print("✓ MeeshoScraper instance created successfully")
    scraper.close()
    print("✓ Scraper closed successfully")
except Exception as e:
    print(f"✗ Error creating scraper: {e}")
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("ALL CHECKS PASSED!")
print("=" * 60)
print("\nNow you can run: python test_scraper_direct.py")
