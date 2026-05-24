export interface Product {
  _id?: string;
  title: string;
  price: string;
  original_price?: string;
  rating?: string;
  reviews_count?: string;
  ratings_count?: string;
  image_url?: string;
  product_link?: string;
  delivery?: string;
  discount?: string;
  features?: string[];
  exchange_offer?: string;
  brand?: string;
  special_tag?: string;
  cod_available?: string;  // For Meesho
}

export interface ScrapingResponse {
  platform: string;
  search_query: string;
  total_products: number;
  products: Product[];
  scraped_at: string;
  status: string;
  message?: string;
}

export interface ApiResponse {
  search_query: string;
  platforms: {
    amazon: ScrapingResponse;
    flipkart: ScrapingResponse;
    reliance_digital: ScrapingResponse;
    myntra: ScrapingResponse;
    meesho: ScrapingResponse;
  };
  total_products_found: number;
  scraped_at: string;
}

// Authentication types
export interface User {
  _id: string;
  email: string;
  name: string;
  created_at: string;
  last_login?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

export interface SignUpData {
  email: string;
  name: string;
  password: string;
}

export interface LoginData {
  email: string;
  password: string;
}

// Wishlist types
export interface WishlistItem {
  _id: string;
  product_id: string;
  added_at: string;
  price_alerts?: any;
  product?: Product;
}

// Report types
export interface LowestPriceItem {
  product_name: string;
  lowest_price: string;
  platform: string;
  product_link: string;
  image_url?: string;
  original_price?: string;
  discount?: string;
}

export interface LowestPriceReport {
  total_products: number;
  report_generated_at: string;
  products: LowestPriceItem[];
}
