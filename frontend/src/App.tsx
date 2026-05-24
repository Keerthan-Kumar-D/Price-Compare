import { useState } from 'react';
import { motion } from 'framer-motion';
import { Header } from './components/Header';
import { SearchBar } from './components/SearchBar';
import { PlatformSection } from './components/PlatformSection';
import { LoadingSkeleton } from './components/LoadingSkeleton';
import { ErrorAlert } from './components/ErrorAlert';
import { AuthModal } from './components/AuthModal';
import { WishlistModal } from './components/WishlistModal';
import RealTimeReports from './components/RealTimeReports';
import { useFetchProducts } from './hooks/useFetchProducts';
import { AuthProvider } from './contexts/AuthContext';
import { ToastProvider } from './contexts/ToastContext';

function AppContent() {
  const { loading, error, data, report, fetchProducts } = useFetchProducts();
  const [showError, setShowError] = useState(true);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [showWishlistModal, setShowWishlistModal] = useState(false);
  const [showReportModal, setShowReportModal] = useState(false);

  const handleSearch = (query: string) => {
    setShowError(true);
    fetchProducts(query);
  };

  const hasResults =
    data &&
    (data.platforms.amazon.products.length > 0 ||
      data.platforms.flipkart.products.length > 0 ||
      data.platforms.reliance_digital.products.length > 0 ||
      data.platforms.myntra.products.length > 0 ||
      data.platforms.meesho.products.length > 0);

  const activePlatformsCount = data ? 
    [data.platforms.amazon, data.platforms.flipkart, data.platforms.reliance_digital, data.platforms.myntra]
      .filter(platform => platform.products.length > 0).length : 0;

  // Debug logging
  if (data) {
    console.log('Meesho products count:', data.platforms.meesho?.products?.length || 0);
    console.log('Meesho data:', data.platforms.meesho);
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50/50 to-cyan-50/30">
      <Header 
        onAuthClick={() => setShowAuthModal(true)}
        onWishlistClick={() => setShowWishlistModal(true)}
        onReportClick={() => setShowReportModal(true)}
      />

      <main className="container mx-auto py-12">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center mb-16 px-4"
        >
          <motion.h1
            initial={{ y: -20 }}
            animate={{ y: 0 }}
            className="text-5xl md:text-7xl font-extrabold mb-6 bg-gradient-to-r from-slate-800 via-blue-700 to-cyan-700 bg-clip-text text-transparent leading-tight"
          >
            Find the Best Deals
          </motion.h1>
          <motion.p
            initial={{ y: -20 }}
            animate={{ y: 0 }}
            transition={{ delay: 0.1 }}
            className="text-slate-600 text-xl max-w-2xl mx-auto"
          >
            Compare prices across Amazon, Flipkart, Myntra, and Meesho
          </motion.p>
        </motion.div>

        <SearchBar onSearch={handleSearch} loading={loading} />

        <div className="mt-12">
          {error && showError && (
            <ErrorAlert message={error} onClose={() => setShowError(false)} />
          )}

          {loading && (
            <div className="container mx-auto px-4">
              <LoadingSkeleton />
            </div>
          )}

          {!loading && hasResults && data && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="container mx-auto px-4"
            >
              {/* Main platforms in grid */}
              <div className={`grid grid-cols-1 gap-8 ${
                activePlatformsCount === 1 ? 'lg:grid-cols-1 max-w-md mx-auto' :
                activePlatformsCount === 2 ? 'lg:grid-cols-2' :
                'xl:grid-cols-3 lg:grid-cols-2'
              }`}>
                {data.platforms.amazon.products.length > 0 && (
                  <PlatformSection
                    title="Amazon"
                    products={data.platforms.amazon.products}
                    color="bg-gradient-to-br from-orange-400 to-orange-600"
                    logo="https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg"
                    onAuthRequired={() => setShowAuthModal(true)}
                  />
                )}
                {data.platforms.flipkart.products.length > 0 && (
                  <PlatformSection
                    title="Flipkart"
                    products={data.platforms.flipkart.products}
                    color="bg-gradient-to-br from-blue-500 to-blue-700"
                    logo="https://static-assets-web.flixcart.com/batman-returns/batman-returns/p/images/fkheaderlogo_exploreplus-44005d.svg"
                    onAuthRequired={() => setShowAuthModal(true)}
                  />
                )}
                {data.platforms.myntra.products.length > 0 && (
                  <PlatformSection
                    title="Myntra"
                    products={data.platforms.myntra.products}
                    color="bg-gradient-to-br from-pink-500 to-purple-600"
                    logo="M"
                    onAuthRequired={() => setShowAuthModal(true)}
                  />
                )}
              </div>

              {/* Show Meesho below other platforms in a full-width section */}
              {data.platforms.meesho && data.platforms.meesho.products.length > 0 && (
                <div className="mt-8">
                  <PlatformSection
                    title="Meesho"
                    products={data.platforms.meesho.products || []}
                    color="bg-gradient-to-br from-purple-500 to-indigo-600"
                    logo="M"
                    onAuthRequired={() => setShowAuthModal(true)}
                  />
                </div>
              )}
            </motion.div>
          )}

          {!loading && data && !hasResults && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="container mx-auto px-4"
            >
              <div className="bg-white rounded-2xl border border-slate-200 shadow-lg p-12 text-center max-w-2xl mx-auto">
                <div className="text-6xl mb-6">🔍</div>
                <h3 className="text-3xl font-bold text-slate-800 mb-3">
                  No Products Found
                </h3>
                <p className="text-slate-600 text-lg">
                  We couldn't find any valid products matching your search. Try a different query or check your spelling.
                </p>
              </div>
            </motion.div>
          )}
        </div>
      </main>

      <footer className="mt-24 py-8 border-t border-slate-200 bg-white/50 backdrop-blur-sm">
        <div className="container mx-auto px-4">
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5 }}
            className="text-center"
          >
            <p className="text-slate-600 text-sm font-medium">
              © 2025 PriceCompare. All rights reserved.
            </p>
            <p className="text-slate-500 text-xs mt-2">
              Compare prices and save money on your favorite products
            </p>
          </motion.div>
        </div>
      </footer>

      {/* Modals */}
      <AuthModal 
        isOpen={showAuthModal} 
        onClose={() => setShowAuthModal(false)} 
      />
      <WishlistModal 
        isOpen={showWishlistModal} 
        onClose={() => setShowWishlistModal(false)} 
      />
      {showReportModal && (
        <RealTimeReports 
          onClose={() => setShowReportModal(false)}
          preGeneratedReport={report}
        />
      )}
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <ToastProvider>
        <AppContent />
      </ToastProvider>
    </AuthProvider>
  );
}

export default App;
