"""
Quick test script for Myntra integration in app.py
Run this after starting the FastAPI server
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_myntra_endpoint():
    """Test the new Myntra endpoint"""
    print("\n" + "="*60)
    print("Testing Myntra Scraper Endpoint")
    print("="*60)
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/scrape/myntra",
            params={"query": "mens-tshirts", "limit": 5},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Status: {response.status_code}")
            print(f"✓ Platform: {data['platform']}")
            print(f"✓ Query: {data['search_query']}")
            print(f"✓ Products Found: {data['total_products']}")
            print(f"✓ Status: {data['status']}")
            
            if data.get('message'):
                print(f"⚠ Message: {data['message']}")
            
            if data['products']:
                print(f"\n📦 First Product:")
                product = data['products'][0]
                print(f"   Brand: {product.get('brand', 'N/A')}")
                print(f"   Title: {product.get('title', 'N/A')}")
                print(f"   Price: {product.get('price', 'N/A')}")
            
            return True
        else:
            print(f"✗ Error: Status {response.status_code}")
            print(response.text)
            return False
            
    except requests.exceptions.ConnectionError:
        print("✗ Could not connect to server")
        print("   Make sure FastAPI server is running:")
        print("   python app.py")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_all_platforms():
    """Test the updated all platforms endpoint"""
    print("\n" + "="*60)
    print("Testing All Platforms Endpoint (Including Myntra)")
    print("="*60)
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/scrape/all",
            params={"query": "tshirt", "limit": 3},
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Status: {response.status_code}")
            print(f"✓ Query: {data['search_query']}")
            print(f"✓ Total Products: {data['total_products_found']}")
            print(f"\n📊 Platforms:")
            
            for platform_key, platform_data in data['platforms'].items():
                print(f"   • {platform_data['platform']}: {platform_data['total_products']} products ({platform_data['status']})")
            
            # Check if Myntra is included
            if 'myntra' in data['platforms']:
                print("\n✓ Myntra is included in all platforms!")
            else:
                print("\n✗ Myntra NOT found in platforms")
            
            return True
        else:
            print(f"✗ Error: Status {response.status_code}")
            print(response.text)
            return False
            
    except requests.exceptions.ConnectionError:
        print("✗ Could not connect to server")
        print("   Make sure FastAPI server is running:")
        print("   python app.py")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_platforms_endpoint():
    """Test the platforms endpoint"""
    print("\n" + "="*60)
    print("Testing Platforms Information Endpoint")
    print("="*60)
    
    try:
        response = requests.get(f"{BASE_URL}/api/platforms", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Status: {response.status_code}")
            print(f"✓ Total Platforms: {data['total_platforms']}")
            print(f"\n📋 Supported Platforms:")
            
            for platform in data['platforms']:
                print(f"\n   {platform['name']}")
                print(f"   Endpoint: {platform['endpoint']}")
                print(f"   Status: {platform['status']}")
                if platform.get('note'):
                    print(f"   Note: {platform['note']}")
            
            # Check if Myntra is included
            myntra_found = any(p['name'] == 'Myntra' for p in data['platforms'])
            if myntra_found:
                print("\n✓ Myntra is listed in platforms!")
            else:
                print("\n✗ Myntra NOT found in platforms list")
            
            if data['total_platforms'] == 4:
                print("✓ Total platforms updated to 4!")
            
            return True
        else:
            print(f"✗ Error: Status {response.status_code}")
            print(response.text)
            return False
            
    except requests.exceptions.ConnectionError:
        print("✗ Could not connect to server")
        print("   Make sure FastAPI server is running:")
        print("   python app.py")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("🧪 MYNTRA INTEGRATION TEST SUITE")
    print("="*60)
    print("\nMake sure FastAPI server is running before testing:")
    print("   cd 'c:\\Users\\keert\\Desktop\\Scrapper-main - Copy'")
    print("   python app.py")
    print("\nOr:")
    print("   uvicorn app:app --reload --port 8000")
    print("\n" + "="*60)
    
    input("\nPress Enter to start tests...")
    
    results = []
    
    # Test 1: Platforms endpoint
    results.append(("Platforms Endpoint", test_platforms_endpoint()))
    
    # Test 2: Myntra specific endpoint
    results.append(("Myntra Endpoint", test_myntra_endpoint()))
    
    # Test 3: All platforms endpoint
    results.append(("All Platforms Endpoint", test_all_platforms()))
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{status}: {test_name}")
    
    total_passed = sum(1 for _, passed in results if passed)
    total_tests = len(results)
    
    print(f"\nTotal: {total_passed}/{total_tests} tests passed")
    
    if total_passed == total_tests:
        print("\n🎉 All tests passed! Myntra integration is working!")
    else:
        print("\n⚠ Some tests failed. Check the output above for details.")
    
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
