import React, { useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Heart, ShoppingCart, Trash2, ExternalLink } from 'lucide-react';
import { useWishlist } from '../hooks/useWishlist';
import { WishlistItem } from '../types/product';

interface WishlistModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const WishlistModal: React.FC<WishlistModalProps> = ({ isOpen, onClose }) => {
  const { wishlistItems, loading, removeFromWishlist, refreshWishlist } = useWishlist();

  // Fetch fresh wishlist data every time the modal opens
  useEffect(() => {
    if (isOpen) {
      console.log('Wishlist modal opened, fetching fresh data...');
      refreshWishlist();
    }
  }, [isOpen]); // Remove refreshWishlist from dependency array to prevent infinite loop

  const handleRemoveItem = async (productId: string) => {
    try {
      console.log('Removing item from wishlist:', productId);
      await removeFromWishlist(productId);
      console.log('Item removed successfully');
    } catch (error) {
      console.error('Failed to remove item:', error);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 px-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.95 }}
        className="bg-white rounded-2xl shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-hidden"
      >
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-br from-red-500 to-pink-500 rounded-full flex items-center justify-center">
              <Heart className="w-5 h-5 text-white fill-white" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-gray-800">My Wishlist</h2>
              <p className="text-gray-600 text-sm">
                {wishlistItems.length} {wishlistItems.length === 1 ? 'item' : 'items'} saved
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
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            </div>
          ) : wishlistItems.length === 0 ? (
            <div className="text-center py-12 px-6">
              <div className="w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-6">
                <Heart className="w-12 h-12 text-gray-400" />
              </div>
              <h3 className="text-xl font-semibold text-gray-800 mb-2">Your wishlist is empty</h3>
              <p className="text-gray-600 mb-6">
                Start adding products to your wishlist by clicking the heart icon on any product card
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
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <AnimatePresence>
                  {wishlistItems.map((item, index) => (
                    <WishlistItemCard
                      key={item._id}
                      item={item}
                      index={index}
                      onRemove={() => handleRemoveItem(item.product_id)}
                    />
                  ))}
                </AnimatePresence>
              </div>
            </div>
          )}
        </div>
      </motion.div>
    </div>
  );
};

interface WishlistItemCardProps {
  item: WishlistItem;
  index: number;
  onRemove: () => void;
}

const WishlistItemCard: React.FC<WishlistItemCardProps> = ({ item, index, onRemove }) => {
  const product = item.product;

  // Debug logs removed for cleaner console

  if (!product) {
    console.log('No product data for wishlist item:', item);
    return (
      <div className="bg-gray-100 rounded-xl p-4 text-center">
        <p className="text-gray-500">Product data not available</p>
        <button
          onClick={onRemove}
          className="mt-2 px-3 py-1 bg-red-500 text-white rounded text-sm"
        >
          Remove
        </button>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ delay: index * 0.1 }}
      className="bg-white rounded-xl border border-gray-200 hover:border-blue-300 p-4 hover:shadow-lg transition-all group relative"
    >
      {/* Remove button - always visible */}
      <button
        onClick={() => {
          console.log('Remove button clicked for product:', item.product_id);
          onRemove();
        }}
        className="absolute top-3 right-3 w-8 h-8 rounded-full bg-red-50 hover:bg-red-100 flex items-center justify-center transition-colors z-10 border border-red-200 shadow-sm"
        title="Remove from wishlist"
      >
        <Trash2 className="w-4 h-4 text-red-500" />
      </button>

      {/* Product Image */}
      <div className="relative mb-3 rounded-lg overflow-hidden bg-gray-50 h-32">
        {product.image_url ? (
          <img
            src={product.image_url}
            alt={product.title || 'Product image'}
            className="w-full h-full object-contain p-2"
            onError={(e) => {
              console.log('Image failed to load:', product.image_url);
              (e.target as HTMLImageElement).src =
                'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="200" height="200"%3E%3Crect fill="%23f1f5f9" width="200" height="200"/%3E%3Ctext fill="%2394a3b8" font-family="sans-serif" font-size="14" x="50%25" y="50%25" text-anchor="middle" dominant-baseline="middle"%3ENo Image%3C/text%3E%3C/svg%3E';
            }}
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-gray-400 text-sm">
            No Image Available
          </div>
        )}
      </div>

      {/* Product Info */}
      <div className="space-y-2 pr-10"> {/* Add right padding for remove button */}
        <h4 className="font-semibold text-sm text-gray-800 line-clamp-2 leading-relaxed">
          {product.title || 'Unknown Product'}
        </h4>

        <div className="flex items-center justify-between">
          <span className="text-lg font-bold text-blue-600">
            {product.price || 'Price not available'}
          </span>
          {product.original_price && product.original_price !== product.price && (
            <span className="text-sm text-gray-400 line-through">
              {product.original_price}
            </span>
          )}
        </div>

        {/* Added date */}
        <p className="text-xs text-gray-500">
          Added {new Date(item.added_at).toLocaleDateString()}
        </p>

        {/* Action buttons */}
        <div className="flex space-x-2 pt-2">
          {product.product_link ? (
            <>
              <a
                href={product.product_link}
                target="_blank"
                rel="noopener noreferrer"
                className="flex-1 bg-gradient-to-r from-blue-600 to-cyan-600 text-white py-2 px-3 rounded-lg text-xs font-semibold hover:from-blue-700 hover:to-cyan-700 transition-all flex items-center justify-center space-x-1"
                onClick={() => console.log('Opening link:', product.product_link)}
              >
                <ShoppingCart className="w-3 h-3" />
                <span>Buy Now</span>
              </a>
              <a
                href={product.product_link}
                target="_blank"
                rel="noopener noreferrer"
                className="w-10 h-8 border border-gray-300 rounded-lg flex items-center justify-center hover:bg-gray-50 transition-colors"
                title="View product"
              >
                <ExternalLink className="w-3 h-3 text-gray-600" />
              </a>
            </>
          ) : (
            <div className="text-xs text-gray-500 py-2">
              Product link not available
            </div>
          )}
        </div>

        {/* Remove button - always visible for both mobile and desktop */}
        <button
          onClick={() => {
            console.log('Bottom remove button clicked for product:', item.product_id);
            onRemove();
          }}
          className="w-full mt-2 px-3 py-2 bg-red-50 text-red-600 rounded-lg text-xs font-semibold hover:bg-red-100 transition-colors flex items-center justify-center space-x-1 border border-red-200"
        >
          <Trash2 className="w-3 h-3" />
          <span>Remove from Wishlist</span>
        </button>
      </div>
    </motion.div>
  );
};