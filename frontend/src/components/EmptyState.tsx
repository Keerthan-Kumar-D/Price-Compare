import { Package } from 'lucide-react';
import { motion } from 'framer-motion';

interface EmptyStateProps {
  message?: string;
}

export const EmptyState = ({ message = 'No results found' }: EmptyStateProps) => {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      className="flex flex-col items-center justify-center py-12 px-4 bg-white rounded-2xl border border-slate-200 shadow-sm"
    >
      <div className="bg-gradient-to-br from-slate-100 to-slate-200 rounded-full p-6 mb-4">
        <Package className="w-12 h-12 text-slate-500" />
      </div>
      <p className="text-slate-700 text-lg font-semibold">
        {message}
      </p>
      <p className="text-slate-500 text-sm mt-2">
        Try adjusting your search query
      </p>
    </motion.div>
  );
};
