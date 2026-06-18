import { Product } from '../types/product';

const API_BASE_URL = import.meta.env.VITE_API_URL;

export const saveProductAndGetId = async (productData: Product, tempId: string, token: string): Promise<string> => {
  if (!token) throw new Error('No authentication token');

  const response = await fetch(`${API_BASE_URL}/products/save`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify({
      ...productData,
      temp_id: tempId
    }),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Failed to save product');
  }

  const result = await response.json();
  return result._id || result.id;
};

export const generateTempId = (product: Product): string => {
  // Create a temporary identifier based on product details
  const identifier = product.title + product.price + (product.product_link || '');
  
  // Use a hash-like function that can handle Unicode characters
  let hash = 0;
  for (let i = 0; i < identifier.length; i++) {
    const char = identifier.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash; // Convert to 32-bit integer
  }
  
  // Convert to positive number and then to string
  return Math.abs(hash).toString(36);
};