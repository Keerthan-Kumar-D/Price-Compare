import { motion } from 'framer-motion';
import { Package2 } from 'lucide-react';
import { Product } from '../types/product';
import { ProductCard } from './ProductCard';
import { EmptyState } from './EmptyState';

interface PlatformSectionProps {
  title: string;
  products: Product[];
  color: string;
  logo: string;
  onAuthRequired?: () => void;
}

export const PlatformSection = ({
  title,
  products,
  color,
  logo,
  onAuthRequired,
}: PlatformSectionProps) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-4"
    >
      <div className="sticky top-20 z-10 bg-gradient-to-br from-slate-50 to-blue-50/30 backdrop-blur-sm rounded-2xl p-4 border border-slate-200 shadow-sm mb-6">
        <div className="flex items-center gap-3">
          <div className={`w-12 h-12 ${
            title === 'Myntra' ? 'bg-white' : 
            title === 'Meesho' ? 'bg-purple-600' : 
            color
          } rounded-xl flex items-center justify-center shadow-lg p-2`}>
            {logo.startsWith('http') ? (
              <>
                <img 
                  src={logo} 
                  alt={`${title} logo`}
                  className="w-full h-full object-contain filter brightness-0 invert"
                  onError={(e) => {
                    (e.target as HTMLImageElement).style.display = 'none';
                    (e.target as HTMLImageElement).nextElementSibling?.classList.remove('hidden');
                  }}
                />
                <span className="text-2xl hidden">
                  {title === 'Amazon' ? '🛒' : title === 'Flipkart' ? '🏪' : title === 'Myntra' ? '👗' : '🏬'}
                </span>
              </>
            ) : title === 'Myntra' ? (
              <span className="text-3xl font-bold bg-gradient-to-br from-pink-500 to-orange-500 bg-clip-text text-transparent">
                {logo}
              </span>
            ) : title === 'Meesho' ? (
              <span className="text-3xl font-bold text-yellow-400" style={{ fontFamily: '"Nunito", sans-serif' }}>
                {logo}
              </span>
            ) : (
              <span className="text-3xl font-bold text-white">
                {logo}
              </span>
            )}
          </div>
          <div className="flex-1">
            <h2 className="text-xl font-bold text-slate-800">
              {title}
            </h2>
            <div className="flex items-center gap-2 mt-1">
              <Package2 className="w-3.5 h-3.5 text-slate-500" />
              <span className="text-sm text-slate-600 font-medium">
                {products.length} {products.length === 1 ? 'product' : 'products'} found
              </span>
            </div>
          </div>
          {products.length > 0 && (
            <div className="text-right">
              <div className="text-xs text-slate-500 uppercase tracking-wide font-semibold">Best Price</div>
              <div className="text-lg font-bold bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent">
                {products[0].price}
              </div>
            </div>
          )}
        </div>
      </div>

      {products.length > 0 ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {products.map((product, index) => (
            <ProductCard 
              key={index} 
              product={product} 
              index={index} 
              onAuthRequired={onAuthRequired}
            />
          ))}
        </div>
      ) : (
        <EmptyState message={`No results found on ${title}`} />
      )}
    </motion.div>
  );
};
