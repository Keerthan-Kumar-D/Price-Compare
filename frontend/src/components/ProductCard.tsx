import { ExternalLink, Star, Truck, TrendingDown, Heart } from 'lucide-react';
import { motion } from 'framer-motion';
import { useState, useEffect } from 'react';
import { Product } from '../types/product';
import { useAuth } from '../contexts/AuthContext';
import { useWishlist } from '../hooks/useWishlist';
import { saveProductAndGetId, generateTempId } from '../utils/productUtils';

interface ProductCardProps {
  product: Product;
  index: number;
  onAuthRequired?: () => void;
}

const calculateDiscount = (price: string, originalPrice: string): number | null => {
  const priceNum = parseFloat(price.replace(/[^0-9.]/g, ''));
  const originalNum = parseFloat(originalPrice.replace(/[^0-9.]/g, ''));

  if (isNaN(priceNum) || isNaN(originalNum) || originalNum <= priceNum) {
    return null;
  }

  return Math.round(((originalNum - priceNum) / originalNum) * 100);
};

export const ProductCard = ({ product, index, onAuthRequired }: ProductCardProps) => {
  const discount = product.original_price ? calculateDiscount(product.price, product.original_price) : null;
  
  const { isAuthenticated, token } = useAuth();
  const { addToWishlist, removeFromWishlist, isInWishlist } = useWishlist();
  const [inWishlist, setInWishlist] = useState(false);
  const [wishlistLoading, setWishlistLoading] = useState(false);

  // Check if product is in wishlist when component mounts or product changes
  useEffect(() => {
    const checkWishlistStatus = async () => {
      if (isAuthenticated && product._id) {
        const status = await isInWishlist(product._id);
        setInWishlist(status);
      } else {
        setInWishlist(false);
      }
    };
    
    checkWishlistStatus();
  }, [isAuthenticated, product._id, isInWishlist]);

  // Also check when product gets an ID after saving
  useEffect(() => {
    if (isAuthenticated && product._id) {
      const checkStatus = async () => {
        const status = await isInWishlist(product._id!);
        setInWishlist(status);
      };
      checkStatus();
    }
  }, [product._id, isAuthenticated, isInWishlist]);

  const handleWishlistClick = async (e: React.MouseEvent) => {
    e.preventDefault();
    
    console.log('Wishlist button clicked:', {
      productId: product._id,
      isAuthenticated,
      inWishlist,
      productTitle: product.title
    });
    
    if (!isAuthenticated) {
      console.log('Not authenticated, showing auth modal');
      onAuthRequired?.();
      return;
    }

    // If product doesn't have an ID, we need to save it first or create a unique identifier
    let productId = product._id;
    if (!productId) {
      console.log('Product has no ID, saving to database first...');
      try {
        // Create a temporary identifier based on product details
        const tempId = generateTempId(product);
        productId = await saveProductAndGetId(product, tempId, token!);
        console.log('Product saved with ID:', productId);
        
        // Update the product object with the new ID for future reference
        product._id = productId;
      } catch (error) {
        console.error('Failed to save product:', error);
        alert('Failed to save product. Please try again.');
        return;
      }
    }

    setWishlistLoading(true);
    try {
      if (inWishlist) {
        console.log('Removing from wishlist');
        await removeFromWishlist(productId!);
        setInWishlist(false);
      } else {
        console.log('Adding to wishlist');
        await addToWishlist(productId!);
        setInWishlist(true);
        console.log('Successfully added to wishlist and updated state');
      }
    } catch (error) {
      console.error('Wishlist operation failed:', error);
      
      // Handle "already in wishlist" error gracefully
      if (error instanceof Error && error.message.includes('already in wishlist')) {
        // If product is already in wishlist, just update the state
        setInWishlist(true);
        console.log('Product was already in wishlist, updated state');
      } else {
        // Show alert for other errors
        alert(`Wishlist operation failed: ${error}`);
      }
    } finally {
      setWishlistLoading(false);
    }
  };



  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.08 }}
      whileHover={{ y: -6 }}
      className="bg-white rounded-2xl border border-slate-200 hover:border-blue-300 p-5 hover:shadow-2xl hover:shadow-blue-500/10 transition-all group relative overflow-hidden h-[420px] flex flex-col"
    >
      {/* Wishlist button */}
      <motion.button
        onClick={handleWishlistClick}
        disabled={wishlistLoading}
        className="absolute top-3 left-3 z-10 w-10 h-10 rounded-full bg-white/90 backdrop-blur-sm border border-gray-200 flex items-center justify-center hover:bg-white hover:scale-110 transition-all shadow-lg"
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.95 }}
      >
        <Heart
          className={`w-5 h-5 transition-colors ${
            inWishlist 
              ? 'text-red-500 fill-red-500' 
              : 'text-gray-400 hover:text-red-500'
          }`}
        />
      </motion.button>

      <div className="absolute inset-0 bg-gradient-to-br from-blue-50/50 via-transparent to-cyan-50/50 opacity-0 group-hover:opacity-100 transition-opacity"></div>

      {(discount && discount > 0) || product.discount && (
        <motion.div
          initial={{ scale: 0, rotate: -12 }}
          animate={{ scale: 1, rotate: -12 }}
          transition={{ delay: index * 0.08 + 0.2, type: "spring" }}
          className="absolute top-3 right-3 z-10 bg-gradient-to-br from-green-500 to-emerald-600 text-white px-3 py-1.5 rounded-lg shadow-lg flex items-center gap-1"
        >
          <TrendingDown className="w-3 h-3" />
          <span className="text-xs font-bold">
            {product.discount || `${discount}% OFF`}
          </span>
        </motion.div>
      )}

      <div className="relative mb-4 rounded-xl overflow-hidden bg-slate-50 h-48 group-hover:bg-slate-100 transition-colors flex-shrink-0">
        {product.image_url ? (
          <img
            src={product.image_url}
            alt={product.title}
            className="w-full h-full object-contain p-4 group-hover:scale-110 transition-transform duration-500"
            onError={(e) => {
              (e.target as HTMLImageElement).src =
                'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="200" height="200"%3E%3Crect fill="%23f1f5f9" width="200" height="200"/%3E%3Ctext fill="%2394a3b8" font-family="sans-serif" font-size="14" x="50%25" y="50%25" text-anchor="middle" dominant-baseline="middle"%3ENo Image%3C/text%3E%3C/svg%3E';
            }}
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-slate-400 text-sm">
            No Image
          </div>
        )}
      </div>

      <div className="relative space-y-3 flex-grow flex flex-col">
        <h3 className="font-semibold text-sm text-slate-800 line-clamp-2 leading-relaxed group-hover:text-blue-700 transition-colors h-10">
          {product.title}
        </h3>

        <div className="flex items-baseline gap-2 flex-wrap">
          <span className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-cyan-600 bg-clip-text text-transparent">
            {product.price}
          </span>
          {product.original_price && product.original_price !== product.price && (
            <span className="text-sm text-slate-400 line-through">
              {product.original_price}
            </span>
          )}
        </div>

        <div className="flex items-center justify-between pt-2 border-t border-slate-100 min-h-[32px]">
          {product.rating && (
            <div className="flex items-center gap-1.5">
              <div className="flex items-center gap-1 bg-gradient-to-r from-yellow-400 to-orange-400 px-2 py-1 rounded-lg">
                <Star className="w-3.5 h-3.5 fill-white text-white" />
                <span className="font-bold text-white text-sm">
                  {product.rating}
                </span>
              </div>
              {product.reviews_count && (
                <span className="text-xs text-slate-500">
                  ({product.reviews_count})
                </span>
              )}
            </div>
          )}

          {product.delivery && (
            <div className="flex items-center gap-1.5 text-xs text-slate-600 bg-green-50 px-2 py-1 rounded-lg">
              <Truck className="w-3.5 h-3.5 text-green-600" />
              <span className="line-clamp-1 font-medium text-green-700">Fast</span>
            </div>
          )}
        </div>

        <div className="mt-auto space-y-2">
          {product.cod_available && (
            <div className="text-xs text-blue-700 bg-blue-50 px-2 py-1 rounded-lg font-medium">
              💵 {product.cod_available}
            </div>
          )}

          {product.exchange_offer && (
            <div className="text-xs text-green-700 bg-green-50 px-2 py-1 rounded-lg">
              💰 {product.exchange_offer}
            </div>
          )}

          {product.features && product.features.length > 0 && (
            <div className="text-xs text-slate-600">
              <div className="flex flex-wrap gap-1">
                {product.features.slice(0, 2).map((feature, idx) => (
                  <span key={idx} className="bg-slate-100 px-2 py-1 rounded text-xs">
                    {feature}
                  </span>
                ))}
              </div>
            </div>
          )}

          <motion.a
            href={product.product_link}
            target="_blank"
            rel="noopener noreferrer"
            initial={{ opacity: 0, y: 10 }}
            whileHover={{ opacity: 1, y: 0 }}
            className="flex items-center justify-center gap-2 pt-3 border-t border-slate-100 cursor-pointer"
          >
            <span className="text-blue-600 text-sm font-semibold">View on Store</span>
            <ExternalLink className="w-4 h-4 text-blue-600" />
          </motion.a>
        </div>
      </div>
    </motion.div>
  );
};
