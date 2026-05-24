import { ShoppingCart, TrendingDown, LogIn } from 'lucide-react';
import { motion } from 'framer-motion';
import { useAuth } from '../contexts/AuthContext';
import { UserMenu } from './UserMenu';

interface HeaderProps {
  onAuthClick: () => void;
  onWishlistClick: () => void;
  onReportClick: () => void;
}

export const Header: React.FC<HeaderProps> = ({ onAuthClick, onWishlistClick, onReportClick }) => {
  const { isAuthenticated, isLoading } = useAuth();
  return (
    <motion.header
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      className="sticky top-0 z-50 backdrop-blur-xl bg-white/80 border-b border-slate-200/50 shadow-sm"
    >
      <div className="container mx-auto px-4 py-5 flex items-center justify-between">
        <motion.div
          className="flex items-center gap-3"
          whileHover={{ scale: 1.02 }}
        >
          <div className="relative">
            <motion.div
              animate={{
                rotate: [0, -10, 10, -10, 0],
              }}
              transition={{
                duration: 2,
                repeat: Infinity,
                repeatDelay: 3,
              }}
            >
              <ShoppingCart className="w-9 h-9 text-blue-600" strokeWidth={2.5} />
            </motion.div>
            <motion.div
              className="absolute -bottom-1 -right-1 bg-gradient-to-br from-green-400 to-emerald-500 rounded-full p-1"
              animate={{
                scale: [1, 1.2, 1],
              }}
              transition={{
                duration: 2,
                repeat: Infinity,
              }}
            >
              <TrendingDown className="w-3 h-3 text-white" strokeWidth={3} />
            </motion.div>
          </div>
          <div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 via-blue-700 to-cyan-600 bg-clip-text text-transparent">
              PriceCompare
            </h1>
            <p className="text-xs text-slate-500 font-medium">Find the best deals, instantly</p>
          </div>
        </motion.div>

        <div className="flex items-center gap-4">
          <div className="hidden sm:flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-blue-50 to-cyan-50 rounded-full border border-blue-200">
            <div className="flex -space-x-1">
              <div className="w-6 h-6 bg-gradient-to-br from-orange-400 to-orange-600 rounded-full border-2 border-white flex items-center justify-center text-xs font-bold text-white">A</div>
              <div className="w-6 h-6 bg-gradient-to-br from-blue-500 to-blue-700 rounded-full border-2 border-white flex items-center justify-center text-xs font-bold text-white">F</div>
              <div className="w-6 h-6 bg-gradient-to-br from-pink-500 to-purple-600 rounded-full border-2 border-white flex items-center justify-center text-xs font-bold text-white">M</div>
              <div className="w-6 h-6 bg-white rounded-full border-2 border-white flex items-center justify-center text-xs font-bold text-pink-500">M</div>
            </div>
            <span className="text-xs font-semibold text-slate-700">4 Platforms</span>
          </div>

          {/* Authentication Section */}
          {!isLoading && (
            <>
              {isAuthenticated ? (
                <UserMenu 
                  onWishlistClick={onWishlistClick}
                  onReportClick={onReportClick}
                />
              ) : (
                <motion.button
                  onClick={onAuthClick}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className="flex items-center space-x-2 bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 text-white px-4 py-2 rounded-lg transition-all font-medium"
                >
                  <LogIn className="w-4 h-4" />
                  <span className="hidden sm:inline">Sign In</span>
                </motion.button>
              )}
            </>
          )}
        </div>
      </div>
    </motion.header>
  );
};
