import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { User, Heart, LogOut, BarChart3, ChevronDown } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

interface UserMenuProps {
  onWishlistClick: () => void;
  onReportClick: () => void;
}

export const UserMenu: React.FC<UserMenuProps> = ({ onWishlistClick, onReportClick }) => {
  const [isOpen, setIsOpen] = useState(false);
  const { user, logout } = useAuth();

  if (!user) return null;

  return (
    <div className="relative">
      <motion.button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center space-x-2 bg-white/10 backdrop-blur-sm hover:bg-white/20 px-4 py-2 rounded-lg transition-all"
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
      >
        <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-full flex items-center justify-center">
          <User className="w-5 h-5 text-white" />
        </div>
        <span className="text-white font-medium hidden sm:block">
          {user.name.split(' ')[0]}
        </span>
        <ChevronDown className={`w-4 h-4 text-white transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </motion.button>

      <AnimatePresence>
        {isOpen && (
          <>
            <div
              className="fixed inset-0 z-10"
              onClick={() => setIsOpen(false)}
            />
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="absolute right-0 top-full mt-2 w-56 bg-white rounded-xl shadow-2xl border border-gray-100 py-2 z-20"
            >
              <div className="px-4 py-3 border-b border-gray-100">
                <p className="text-sm text-gray-500">Signed in as</p>
                <p className="font-semibold text-gray-800 truncate">{user.email}</p>
              </div>

              <button
                onClick={() => {
                  onWishlistClick();
                  setIsOpen(false);
                }}
                className="w-full px-4 py-3 text-left hover:bg-gray-50 flex items-center space-x-3 transition-colors"
              >
                <Heart className="w-5 h-5 text-red-500" />
                <span className="text-gray-700">My Wishlist</span>
              </button>

              <button
                onClick={() => {
                  onReportClick();
                  setIsOpen(false);
                }}
                className="w-full px-4 py-3 text-left hover:bg-gray-50 flex items-center space-x-3 transition-colors"
              >
                <BarChart3 className="w-5 h-5 text-blue-500" />
                <span className="text-gray-700">Price Reports</span>
              </button>

              <div className="border-t border-gray-100 mt-2 pt-2">
                <button
                  onClick={() => {
                    logout();
                    setIsOpen(false);
                  }}
                  className="w-full px-4 py-3 text-left hover:bg-gray-50 flex items-center space-x-3 transition-colors text-red-600"
                >
                  <LogOut className="w-5 h-5" />
                  <span>Sign Out</span>
                </button>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  );
};