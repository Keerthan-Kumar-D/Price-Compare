import { useState, FormEvent } from 'react';
import { Search, Sparkles } from 'lucide-react';
import { motion } from 'framer-motion';

interface SearchBarProps {
  onSearch: (query: string) => void;
  loading: boolean;
}

export const SearchBar = ({ onSearch, loading }: SearchBarProps) => {
  const [query, setQuery] = useState('');

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      onSearch(query.trim());
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.2 }}
      className="w-full max-w-4xl mx-auto px-4"
    >
      <form onSubmit={handleSubmit} className="relative">
        <div className="relative group">
          <div className="absolute inset-0 bg-gradient-to-r from-blue-400 via-cyan-400 to-blue-500 rounded-2xl blur-lg opacity-20 group-hover:opacity-30 transition-opacity"></div>
          <div className="relative bg-white rounded-2xl shadow-xl border border-slate-200 group-hover:border-blue-300 transition-all">
            <div className="flex items-center gap-3 px-6 py-5">
              <Search className="w-5 h-5 text-slate-400 flex-shrink-0" />
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search for any product to compare prices..."
                className="flex-1 outline-none text-slate-900 placeholder:text-slate-400 text-lg"
                disabled={loading}
              />
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                type="submit"
                disabled={loading}
                className="px-8 py-3 bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 text-white rounded-xl font-semibold flex items-center gap-2 transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-blue-500/25 hover:shadow-xl hover:shadow-blue-500/40"
              >
                {loading ? (
                  <>
                    <motion.div
                      animate={{ rotate: 360 }}
                      transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                    >
                      <Sparkles className="w-5 h-5" />
                    </motion.div>
                    <span>Searching...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-5 h-5" />
                    <span>Compare Prices</span>
                  </>
                )}
              </motion.button>
            </div>
          </div>
        </div>
      </form>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.4 }}
        className="flex items-center justify-center gap-6 mt-6 text-sm text-slate-500"
      >
        <span className="flex items-center gap-2">
          <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
          Real-time pricing
        </span>
        <span className="flex items-center gap-2">
          <span className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></span>
          4 platforms compared
        </span>
        <span className="flex items-center gap-2">
          <span className="w-2 h-2 bg-amber-500 rounded-full animate-pulse"></span>
          Wait for 30-60 seconds
        </span>
        
      </motion.div>
    </motion.div>
  );
};
