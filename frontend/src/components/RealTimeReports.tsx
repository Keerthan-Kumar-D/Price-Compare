import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, Clock, TrendingDown, ExternalLink, Loader } from 'lucide-react';
import { ApiResponse, LowestPriceItem } from '../types/product';

interface RealTimeReportsProps {
  onClose: () => void;
  preGeneratedReport?: LowestPriceItem[];
}

const RealTimeReports: React.FC<RealTimeReportsProps> = ({ onClose, preGeneratedReport }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [report, setReport] = useState<LowestPriceItem[]>(preGeneratedReport || []);
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');
  const [lastSearchTime, setLastSearchTime] = useState<string>(preGeneratedReport ? 'From your last search' : '');
  const [error, setError] = useState<string>('');
  const [priceFilter, setPriceFilter] = useState<string>('');
  const [rangeType, setRangeType] = useState<'above' | 'below'>('above');

  const extractPriceNumber = (price: string): number => {
    const cleanPrice = price.replace(/[^\d.]/g, '').replace(',', '');
    return parseFloat(cleanPrice) || Infinity;
  };

  const getFilteredReport = () => {
    if (!priceFilter || priceFilter.trim() === '') {
      return report;
    }

    const filterPrice = parseFloat(priceFilter);
    if (isNaN(filterPrice)) {
      return report;
    }

    return report.filter(item => {
      const itemPrice = extractPriceNumber(item.lowest_price);
      if (rangeType === 'above') {
        return itemPrice >= filterPrice;
      } else {
        return itemPrice <= filterPrice;
      }
    });
  };

  const generateRealTimeReport = async () => {
    if (!searchQuery.trim()) {
      setError('Please enter a search query');
      return;
    }

    setLoading(true);
    setError('');
    setReport([]);

    try {
      console.log('Fetching real-time data for:', searchQuery);

      // Fetch from all platforms (5 products per platform for a total of ~20-25 products)
      const response = await fetch(`http://localhost:8000/api/scrape/all?query=${encodeURIComponent(searchQuery)}&limit=5`);
      
      if (!response.ok) {
        throw new Error('Failed to fetch data');
      }

      const data: ApiResponse = await response.json();
      console.log('Received data:', data);

      // Process data to collect all products from all platforms
      const allProducts: LowestPriceItem[] = [];

      // Process each platform
      Object.entries(data.platforms).forEach(([platformName, platformData]) => {
        if (platformData.status === 'success' && platformData.products) {
          platformData.products.forEach(product => {
            const price = product.price;
            
            // Skip products without valid prices
            if (!price || price.toLowerCase().includes('not available')) {
              return;
            }

            const priceNumeric = extractPriceNumber(price);
            if (priceNumeric === Infinity) {
              return;
            }

            const platformDisplayName = platformName === 'reliance_digital' 
              ? 'Reliance Digital' 
              : platformName.charAt(0).toUpperCase() + platformName.slice(1);

            // Add all products from all platforms
            allProducts.push({
              product_name: product.title,
              lowest_price: price,
              platform: platformDisplayName,
              product_link: product.product_link || '',
              image_url: product.image_url,
              original_price: product.original_price,
              discount: product.discount || undefined
            });
          });
        }
      });

      // Sort by price according to selected order
      const reportItems = allProducts
        .sort((a, b) => extractPriceNumber(a.lowest_price) - extractPriceNumber(b.lowest_price));

      if (sortOrder === 'desc') {
        reportItems.reverse();
      }

      setReport(reportItems);
      setLastSearchTime(new Date().toLocaleString());
      
      console.log('Generated report with', reportItems.length, 'items');

    } catch (err: any) {
      console.error('Report generation error:', err);
      setError(err.message || 'Failed to generate report');
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      generateRealTimeReport();
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50"
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.9, opacity: 0 }}
        className="bg-white rounded-2xl shadow-2xl w-full max-w-6xl max-h-[90vh] overflow-hidden"
      >
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <TrendingDown className="w-8 h-8" />
              <div>
                <h2 className="text-2xl font-bold">Real-Time Price Report</h2>
                <p className="text-blue-100">Compare prices across all platforms instantly</p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="w-10 h-10 rounded-full bg-white/20 hover:bg-white/30 flex items-center justify-center transition-colors"
            >
              ✕
            </button>
          </div>

          {/* Search Section */}
          <div className="mt-6">
            <div className="flex gap-3">
              <div className="flex-1 relative">
                <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Enter product name to search across all platforms..."
                  className="w-full pl-12 pr-4 py-3 rounded-xl border-0 text-gray-900 placeholder-gray-500 focus:ring-2 focus:ring-white/50"
                  disabled={loading}
                />
              </div>
              <button
                onClick={generateRealTimeReport}
                disabled={loading || !searchQuery.trim()}
                className="px-8 py-3 bg-white text-blue-600 rounded-xl font-semibold hover:bg-blue-50 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 transition-colors"
              >
                {loading ? (
                  <>
                    <Loader className="w-5 h-5 animate-spin" />
                    Searching...
                  </>
                ) : (
                  <>
                    <Search className="w-5 h-5" />
                    Generate Report
                  </>
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 max-h-[60vh] overflow-y-auto">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-4">
              {error}
            </div>
          )}

          {lastSearchTime && (
            <div className="flex items-center gap-2 text-gray-500 mb-4">
              <Clock className="w-4 h-4" />
              <span className="text-sm">Last updated: {lastSearchTime}</span>
            </div>
          )}

          {loading && (
            <div className="flex items-center justify-center py-12">
              <Loader className="w-8 h-8 animate-spin text-blue-600" />
              <span className="ml-3 text-gray-600">Searching across all platforms...</span>
            </div>
          )}

          {!loading && report.length === 0 && searchQuery && (
            <div className="text-center py-12 text-gray-500">
              <TrendingDown className="w-12 h-12 mx-auto mb-4 text-gray-300" />
              <p>No products found. Try a different search term.</p>
            </div>
          )}

          <AnimatePresence>
            {report.length > 0 && (
              <div className="space-y-4">
                <div className="bg-gradient-to-r from-green-50 to-blue-50 p-4 rounded-xl border border-green-200">
                  <div className="flex items-center justify-between">
                    <h3 className="font-semibold text-gray-800 mb-2">
                      Lowest Price Report - {getFilteredReport().length} Products Found
                    </h3>
                    <div className="flex flex-col items-start gap-3">
                      {/* Price Filter Input (stacked) */}
                      <div className="flex items-center gap-2 w-full">
                        <label className="text-sm text-gray-600 w-20">Sort:</label>
                        <input
                          type="number"
                          value={priceFilter}
                          onChange={(e) => setPriceFilter(e.target.value)}
                          placeholder="Enter price"
                          className="px-2 py-1 rounded-md border text-sm w-40"
                        />
                      </div>

                      {/* Range Selector (stacked) */}
                      <div className="flex items-center gap-2 w-full">
                        <label className="text-sm text-gray-600 w-20">Range:</label>
                        <select
                          value={rangeType}
                          onChange={(e) => setRangeType(e.target.value as 'above' | 'below')}
                          className="px-2 py-1 rounded-md border text-sm w-40"
                        >
                          <option value="above">Above</option>
                          <option value="below">Below</option>
                        </select>
                      </div>

                      {/* Sort Order Dropdown (stacked) */}
                      <div className="flex items-center gap-2 w-full">
                        <label className="text-sm text-gray-600 w-20">Order:</label>
                        <select
                          value={sortOrder}
                          onChange={(e) => {
                            const newOrder = e.target.value as 'asc' | 'desc';
                            setSortOrder(newOrder);
                            // Re-sort existing report when toggled
                            setReport((prev) => {
                              const copy = [...prev];
                              copy.sort((a, b) => extractPriceNumber(a.lowest_price) - extractPriceNumber(b.lowest_price));
                              return newOrder === 'desc' ? copy.reverse() : copy;
                            });
                          }}
                          className="px-2 py-1 rounded-md border text-sm w-40"
                        >
                          <option value="asc">Low → High</option>
                          <option value="desc">High → Low</option>
                        </select>
                      </div>
                    </div>
                  </div>
                  <p className="text-sm text-gray-600">
                    Real-time comparison showing the best deals across Amazon, Flipkart, Myntra, and Meesho.
                  </p>
                </div>

                <div className="grid gap-4">
                  {getFilteredReport().map((item, index) => (
                    <motion.div
                      key={`${item.product_name}-${index}`}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: index * 0.05 }}
                      className="bg-white border border-gray-200 rounded-xl p-4 hover:shadow-lg transition-shadow"
                    >
                      <div className="flex items-center gap-4">
                        {item.image_url && (
                          <img
                            src={item.image_url}
                            alt={item.product_name}
                            className="w-16 h-16 object-contain rounded-lg bg-gray-50"
                            onError={(e) => {
                              (e.target as HTMLImageElement).style.display = 'none';
                            }}
                          />
                        )}
                        <div className="flex-1">
                          <h4 className="font-semibold text-gray-800 mb-1 line-clamp-2">
                            {item.product_name}
                          </h4>
                          <div className="flex items-center gap-4">
                            <div className="text-2xl font-bold text-green-600">
                              {item.lowest_price}
                            </div>
                            <div className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm font-medium">
                              {item.platform}
                            </div>
                            {item.discount && (
                              <div className="px-3 py-1 bg-red-100 text-red-700 rounded-full text-sm font-medium">
                                {item.discount}
                              </div>
                            )}
                          </div>
                          {item.original_price && item.original_price !== item.lowest_price && (
                            <div className="text-sm text-gray-500 line-through mt-1">
                              Original: {item.original_price}
                            </div>
                          )}
                        </div>
                        <div className="flex flex-col gap-2">
                          <a
                            href={item.product_link}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
                          >
                            <ExternalLink className="w-4 h-4" />
                            View Deal
                          </a>
                        </div>
                      </div>
                    </motion.div>
                  ))}
                </div>
              </div>
            )}
          </AnimatePresence>

          {!loading && !searchQuery && (
            <div className="text-center py-12 text-gray-500">
              <TrendingDown className="w-12 h-12 mx-auto mb-4 text-gray-300" />
              <h3 className="text-lg font-semibold mb-2">Real-Time Price Comparison</h3>
              <p className="max-w-md mx-auto">
                Enter a product name above to get live pricing data from Amazon, Flipkart, and Reliance Digital. 
                Find the best deals instantly!
              </p>
            </div>
          )}
        </div>
      </motion.div>
    </motion.div>
  );
};

export default RealTimeReports;