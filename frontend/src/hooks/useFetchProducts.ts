import { useState } from 'react';
import { ApiResponse, Product, LowestPriceItem } from '../types/product';

const API_BASE_URL = import.meta.env.VITE_API_URL;

const isValidProduct = (product: Product): boolean => {
  // More lenient validation - only require title and price
  const isValid = !!(
    product.title &&
    product.price &&
    product.title.trim() !== '' &&
    product.price.trim() !== ''
  );
  
  // Debug log for filtering
  if (!isValid) {
    console.log('Product filtered out:', {
      title: product.title,
      price: product.price,
      link: product.product_link
    });
  }
  
  return isValid;
};

export const useFetchProducts = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<ApiResponse | null>(null);
  const [report, setReport] = useState<LowestPriceItem[]>([]);

  const extractPriceNumber = (price: string): number => {
    const cleanPrice = price.replace(/[^\d.]/g, '').replace(',', '');
    return parseFloat(cleanPrice) || Infinity;
  };

  const generateReport = (apiData: ApiResponse): LowestPriceItem[] => {
    const productMap = new Map<string, LowestPriceItem>();

    Object.entries(apiData.platforms).forEach(([platformName, platformData]) => {
      if (platformData.status === 'success' && platformData.products) {
        platformData.products.forEach(product => {
          const price = product.price;
          
          if (!price || price.toLowerCase().includes('not available')) {
            return;
          }

          const priceNumeric = extractPriceNumber(price);
          if (priceNumeric === Infinity) {
            return;
          }

          const productKey = product.title.toLowerCase().trim();
          const platformDisplayName = platformName === 'reliance_digital' 
            ? 'Reliance Digital'
            : platformName === 'meesho'
            ? 'Meesho'
            : platformName.charAt(0).toUpperCase() + platformName.slice(1);

          const existingProduct = productMap.get(productKey);
          if (!existingProduct || priceNumeric < extractPriceNumber(existingProduct.lowest_price)) {
            productMap.set(productKey, {
              product_name: product.title,
              lowest_price: price,
              platform: platformDisplayName,
              product_link: product.product_link || '',
              image_url: product.image_url,
              original_price: product.original_price,
              discount: product.discount || undefined
            });
          }
        });
      }
    });

    return Array.from(productMap.values())
      .sort((a, b) => extractPriceNumber(a.lowest_price) - extractPriceNumber(b.lowest_price));
  };

  const fetchProducts = async (query: string) => {
    if (!query.trim()) {
      setError('Please enter a search query');
      return;
    }

    setLoading(true);
    setError(null);
    setData(null);

    try {
      const response = await fetch(
        `${API_BASE_URL}/api/scrape/all?query=${encodeURIComponent(query)}&limit=5`
      );

      if (!response.ok) {
        throw new Error(`Failed to fetch products: ${response.statusText}`);
      }

      const result: ApiResponse = await response.json();

      console.log('API Response:', result); // Debug log
      console.log('Meesho raw data:', result.platforms?.meesho); // Debug Meesho specifically
      console.log('Meesho products array:', result.platforms?.meesho?.products); // Debug products array

      // Filter out invalid products from each platform
      const filteredResults: ApiResponse = {
        ...result,
        platforms: {
          amazon: {
            ...result.platforms.amazon,
            products: (result.platforms.amazon?.products || []).filter(isValidProduct)
          },
          flipkart: {
            ...result.platforms.flipkart,
            products: (result.platforms.flipkart?.products || []).filter(isValidProduct)
          },
          reliance_digital: {
            ...result.platforms.reliance_digital,
            products: (result.platforms.reliance_digital?.products || []).filter(isValidProduct)
          },
          myntra: {
            ...result.platforms.myntra,
            products: (result.platforms.myntra?.products || []).filter(isValidProduct)
          },
          meesho: {
            ...(result.platforms.meesho || { platform: 'Meesho', search_query: result.search_query, total_products: 0, products: [], scraped_at: result.scraped_at, status: 'error' }),
            products: (result.platforms.meesho?.products || []).filter(isValidProduct)
          }
        }
      };

      console.log('Filtered Meesho products:', filteredResults.platforms.meesho.products.length); // Debug log

      setData(filteredResults);

      // Generate report automatically
      const reportData = generateReport(filteredResults);
      setReport(reportData);

      // Save recent searches
      const recentSearches = JSON.parse(
        localStorage.getItem('recentSearches') || '[]'
      );
      const updatedSearches = [
        query,
        ...recentSearches.filter((q: string) => q !== query),
      ].slice(0, 5);
      localStorage.setItem('recentSearches', JSON.stringify(updatedSearches));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return { loading, error, data, report, fetchProducts };
};
