import { motion } from 'framer-motion';

export const LoadingSkeleton = () => {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
      {[...Array(3)].map((_, colIndex) => (
        <div key={colIndex} className="space-y-4">
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: colIndex * 0.1 }}
            className="bg-gradient-to-br from-slate-50 to-blue-50/30 backdrop-blur-sm rounded-2xl p-4 border border-slate-200"
          >
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-slate-200 rounded-xl animate-pulse" />
              <div className="flex-1 space-y-2">
                <div className="h-5 bg-slate-200 rounded w-24 animate-pulse" />
                <div className="h-3 bg-slate-200 rounded w-32 animate-pulse" />
              </div>
            </div>
          </motion.div>

          {[...Array(2)].map((_, cardIndex) => (
            <motion.div
              key={cardIndex}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: colIndex * 0.1 + cardIndex * 0.1 }}
              className="bg-white rounded-2xl border border-slate-200 p-5"
            >
              <div className="relative mb-4 rounded-xl overflow-hidden bg-slate-100 aspect-square animate-pulse" />

              <div className="space-y-3">
                <div className="h-4 bg-slate-200 rounded animate-pulse" />
                <div className="h-4 bg-slate-200 rounded w-3/4 animate-pulse" />
                <div className="h-10 bg-slate-200 rounded w-1/2 animate-pulse" />
                <div className="flex gap-2 pt-2">
                  <div className="h-6 bg-slate-200 rounded w-16 animate-pulse" />
                  <div className="h-6 bg-slate-200 rounded w-16 animate-pulse" />
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      ))}
    </div>
  );
};
