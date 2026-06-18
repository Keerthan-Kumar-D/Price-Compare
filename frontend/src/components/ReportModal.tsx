import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { X, BarChart3, TrendingDown, ExternalLink, Award } from 'lucide-react';
import { LowestPriceReport, LowestPriceItem } from '../types/product';

interface ReportModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const API_BASE_URL = import.meta.env.VITE_API_URL;

export const ReportModal: React.FC<ReportModalProps> = ({ isOpen, onClose }) => {
  const [report, setReport] = useState<LowestPriceReport | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchReport = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/report/lowest-prices`);
      
      if (!response.ok) {
        throw new Error('Failed to fetch report');
      }

      const reportData: LowestPriceReport = await response.json();
      setReport(reportData);
    } catch (err: any) {
      setError(err.message || 'Failed to load report');
      console.error('Report fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchReport();
    }
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 px-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.95 }}
        className="bg-white rounded-2xl shadow-2xl w-full max-w-6xl max-h-[90vh] overflow-hidden"
      >
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200 bg-gradient-to-r from-blue-50 to-cyan-50">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-full flex items-center justify-center">
              <BarChart3 className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-gray-800">Lowest Price Report</h2>
              <p className="text-gray-600 text-sm">
                {report ? `${report.total_products} products analyzed` : 'Loading...'}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Content */}
        <div className="overflow-y-auto max-h-[calc(90vh-120px)]">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <div className="text-center">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
                <p className="text-gray-600">Analyzing prices across platforms...</p>
              </div>
            </div>
          ) : error ? (
            <div className="text-center py-12 px-6">
              <div className="w-24 h-24 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-6">
                <X className="w-12 h-12 text-red-500" />
              </div>
              <h3 className="text-xl font-semibold text-gray-800 mb-2">Failed to Load Report</h3>
              <p className="text-gray-600 mb-6">{error}</p>
              <button
                onClick={fetchReport}
                className="bg-gradient-to-r from-blue-600 to-cyan-600 text-white px-6 py-3 rounded-lg font-semibold hover:from-blue-700 hover:to-cyan-700 transition-all"
              >
                Try Again
              </button>
            </div>
          ) : !report || report.products.length === 0 ? (
            <div className="text-center py-12 px-6">
              <div className="w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-6">
                <BarChart3 className="w-12 h-12 text-gray-400" />
              </div>
              <h3 className="text-xl font-semibold text-gray-800 mb-2">No Data Available</h3>
              <p className="text-gray-600 mb-6">
                No products found in the database. Try searching for products first to generate a report.
              </p>
              <button
                onClick={onClose}
                className="bg-gradient-to-r from-blue-600 to-cyan-600 text-white px-6 py-3 rounded-lg font-semibold hover:from-blue-700 hover:to-cyan-700 transition-all"
              >
                Start Shopping
              </button>
            </div>
          ) : (
            <div className="p-6">
              {/* Report Summary */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-4">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-blue-500 rounded-lg flex items-center justify-center">
                      <BarChart3 className="w-5 h-5 text-white" />
                    </div>
                    <div>
                      <p className="text-sm font-medium text-blue-700">Total Products</p>
                      <p className="text-2xl font-bold text-blue-900">{report.total_products}</p>
                    </div>
                  </div>
                </div>

                <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-xl p-4">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-green-500 rounded-lg flex items-center justify-center">
                      <Award className="w-5 h-5 text-white" />
                    </div>
                    <div>
                      <p className="text-sm font-medium text-green-700">Best Deals</p>
                      <p className="text-2xl font-bold text-green-900">
                        {report.products.filter(p => p.discount).length}
                      </p>
                    </div>
                  </div>
                </div>

                <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl p-4">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-purple-500 rounded-lg flex items-center justify-center">
                      <TrendingDown className="w-5 h-5 text-white" />
                    </div>
                    <div>
                      <p className="text-sm font-medium text-purple-700">Generated</p>
                      <p className="text-sm font-bold text-purple-900">
                        {new Date(report.report_generated_at).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Products Table */}
              <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="text-left py-3 px-4 font-semibold text-gray-700">Product</th>
                        <th className="text-left py-3 px-4 font-semibold text-gray-700">Lowest Price</th>
                        <th className="text-left py-3 px-4 font-semibold text-gray-700">Platform</th>
                        <th className="text-left py-3 px-4 font-semibold text-gray-700">Discount</th>
                        <th className="text-center py-3 px-4 font-semibold text-gray-700">Action</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                      {report.products.map((item, index) => (
                        <ReportItemRow key={index} item={item} index={index} />
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}
        </div>
      </motion.div>
    </div>
  );
};

interface ReportItemRowProps {
  item: LowestPriceItem;
  index: number;
}

const ReportItemRow: React.FC<ReportItemRowProps> = ({ item, index }) => {
  const getPlatformColor = (platform: string) => {
    switch (platform.toLowerCase()) {
      case 'amazon':
        return 'bg-orange-100 text-orange-800';
      case 'flipkart':
        return 'bg-blue-100 text-blue-800';
      case 'reliance digital':
        return 'bg-red-100 text-red-800';
      case 'myntra':
        return 'bg-pink-100 text-pink-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <motion.tr
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05 }}
      className="hover:bg-gray-50 transition-colors"
    >
      <td className="py-4 px-4">
        <div className="flex items-center space-x-3">
          {item.image_url && (
            <img
              src={item.image_url}
              alt={item.product_name}
              className="w-12 h-12 object-contain bg-gray-50 rounded-lg"
              onError={(e) => {
                (e.target as HTMLImageElement).style.display = 'none';
              }}
            />
          )}
          <div>
            <p className="font-medium text-gray-900 line-clamp-2 text-sm leading-relaxed">
              {item.product_name}
            </p>
          </div>
        </div>
      </td>
      <td className="py-4 px-4">
        <div>
          <p className="font-bold text-lg text-green-600">{item.lowest_price}</p>
          {item.original_price && item.original_price !== item.lowest_price && (
            <p className="text-sm text-gray-500 line-through">{item.original_price}</p>
          )}
        </div>
      </td>
      <td className="py-4 px-4">
        <span className={`px-2 py-1 rounded-full text-xs font-semibold ${getPlatformColor(item.platform)}`}>
          {item.platform}
        </span>
      </td>
      <td className="py-4 px-4">
        {item.discount ? (
          <span className="px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs font-semibold">
            {item.discount}
          </span>
        ) : (
          <span className="text-gray-400 text-sm">No discount</span>
        )}
      </td>
      <td className="py-4 px-4 text-center">
        <a
          href={item.product_link}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center space-x-1 bg-gradient-to-r from-blue-600 to-cyan-600 text-white px-3 py-2 rounded-lg text-sm font-semibold hover:from-blue-700 hover:to-cyan-700 transition-all"
        >
          <span>View</span>
          <ExternalLink className="w-3 h-3" />
        </a>
      </td>
    </motion.tr>
  );
};