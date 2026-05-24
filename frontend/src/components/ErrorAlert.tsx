import { AlertCircle, X } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface ErrorAlertProps {
  message: string;
  onClose: () => void;
}

export const ErrorAlert = ({ message, onClose }: ErrorAlertProps) => {
  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -20 }}
        className="max-w-4xl mx-auto mb-6 px-4"
      >
        <div className="bg-white border-l-4 border-red-500 rounded-xl shadow-lg p-5 flex items-start gap-4">
          <div className="bg-red-100 rounded-lg p-2 flex-shrink-0">
            <AlertCircle className="w-5 h-5 text-red-600" />
          </div>
          <div className="flex-1">
            <p className="text-red-600 font-bold text-base">Error</p>
            <p className="text-slate-700 text-sm mt-1">
              {message}
            </p>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-600 transition-colors flex-shrink-0"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
      </motion.div>
    </AnimatePresence>
  );
};
