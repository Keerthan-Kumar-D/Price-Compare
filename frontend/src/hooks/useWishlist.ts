import { useState, useEffect, useCallback } from 'react';
import { WishlistItem } from '../types/product';
import { useAuth } from '../contexts/AuthContext';
import { useToast } from '../contexts/ToastContext';

const API_BASE_URL = 'http://localhost:8000';

export const useWishlist = () => {
  const [wishlistItems, setWishlistItems] = useState<WishlistItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { token, isAuthenticated } = useAuth();
  const { showToast } = useToast();

  const makeAuthenticatedRequest = async (url: string, options: RequestInit = {}) => {
    if (!token) throw new Error('No authentication token');

    return fetch(url, {
      ...options,
      headers: {
        ...options.headers,
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });
  };

  const fetchWishlist = useCallback(async () => {
    if (!isAuthenticated || !token) return;

    setLoading(true);
    setError(null);

    try {
      const response = await makeAuthenticatedRequest(`${API_BASE_URL}/wishlist/`);
      
      if (!response.ok) {
        throw new Error('Failed to fetch wishlist');
      }

      const items: WishlistItem[] = await response.json();
      console.log('Fetched wishlist items:', items.length);
      setWishlistItems(items);
    } catch (err: any) {
      setError(err.message || 'Failed to load wishlist');
      console.error('Wishlist fetch error:', err);
    } finally {
      setLoading(false);
    }
  }, [isAuthenticated, token]);

  const addToWishlist = async (productId: string) => {
    if (!isAuthenticated || !token) {
      throw new Error('Please sign in to add items to your wishlist');
    }

    console.log('Adding to wishlist:', { productId, token: token?.substring(0, 10) + '...' });

    try {
      const response = await makeAuthenticatedRequest(`${API_BASE_URL}/wishlist/add`, {
        method: 'POST',
        body: JSON.stringify({ product_id: productId }),
      });

      console.log('Wishlist add response status:', response.status);

      if (!response.ok) {
        const errorData = await response.json();
        console.error('Wishlist add error:', errorData);
        throw new Error(errorData.detail || 'Failed to add to wishlist');
      }

      const newItem: WishlistItem = await response.json();
      console.log('Successfully added to wishlist:', newItem);
      
      // Show success notification
      showToast('success', 'Product added to wishlist!');
      
      // Force refresh the entire wishlist to ensure sync with database and get latest data
      await fetchWishlist();
      
      console.log('Wishlist refreshed after adding item');
      
      return newItem;
    } catch (err: any) {
      console.error('Wishlist add exception:', err);
      const errorMessage = err.message || 'Failed to add to wishlist';
      setError(errorMessage);
      showToast('error', errorMessage);
      throw err;
    }
  };

  const removeFromWishlist = async (productId: string) => {
    if (!isAuthenticated || !token) {
      throw new Error('Please sign in to manage your wishlist');
    }

    console.log('Removing from wishlist:', productId);

    try {
      const response = await makeAuthenticatedRequest(
        `${API_BASE_URL}/wishlist/remove/${productId}`,
        { method: 'DELETE' }
      );

      console.log('Remove response status:', response.status);

      if (!response.ok) {
        const errorData = await response.json();
        console.error('Remove error:', errorData);
        throw new Error(errorData.detail || 'Failed to remove from wishlist');
      }

      // Show success notification
      showToast('success', 'Product removed from wishlist!');
      
      // Force refresh the entire wishlist to ensure sync with database
      await fetchWishlist();
      
      console.log('Wishlist refreshed after removing item');
      
      console.log('Successfully removed from wishlist');
    } catch (err: any) {
      console.error('Remove from wishlist error:', err);
      const errorMessage = err.message || 'Failed to remove from wishlist';
      setError(errorMessage);
      showToast('error', errorMessage);
      throw err;
    }
  };

  const isInWishlist = async (productId: string): Promise<boolean> => {
    if (!isAuthenticated || !token || !productId) return false;

    console.log('Checking wishlist status:', { productId, authenticated: isAuthenticated });

    // Check if we already have this product in our local state
    const existsInLocalState = wishlistItems.some(item => 
      item.product_id === productId || 
      (item.product && item.product._id === productId)
    );
    
    if (existsInLocalState) {
      console.log('Found in local wishlist state');
      return true;
    }

    try {
      const response = await makeAuthenticatedRequest(
        `${API_BASE_URL}/wishlist/check/${productId}`
      );

      console.log('Wishlist check response status:', response.status);

      if (response.ok) {
        const data = await response.json();
        console.log('Wishlist check result:', data);
        return data.in_wishlist || false;
      }
    } catch (err) {
      console.error('Error checking wishlist status:', err);
    }
    
    return false;
  };

  // Fetch wishlist on auth state change
  useEffect(() => {
    if (isAuthenticated) {
      fetchWishlist();
    } else {
      setWishlistItems([]);
    }
  }, [isAuthenticated]);

  return {
    wishlistItems,
    loading,
    error,
    addToWishlist,
    removeFromWishlist,
    isInWishlist,
    refreshWishlist: fetchWishlist,
  };
};