# MongoDB Schema Design

## Collections Structure

### 1. Users Collection
```javascript
{
  _id: ObjectId,
  email: String (unique, required),
  password: String (hashed, required),
  name: String (required),
  created_at: Date,
  updated_at: Date,
  is_active: Boolean (default: true),
  last_login: Date
}
```

### 2. Products Collection (Cache scraped products)
```javascript
{
  _id: ObjectId,
  title: String (required),
  normalized_title: String (for search/matching),
  platforms: {
    amazon: {
      price: String,
      original_price: String,
      product_link: String,
      image_url: String,
      rating: String,
      reviews_count: String,
      delivery: String,
      last_updated: Date
    },
    flipkart: {
      price: String,
      original_price: String,
      discount: String,
      product_link: String,
      image_url: String,
      rating: String,
      reviews_count: String,
      features: [String],
      exchange_offer: String,
      last_updated: Date
    },
    reliance_digital: {
      price: String,
      mrp: String,
      discount: String,
      savings: String,
      product_link: String,
      image_url: String,
      rating: String,
      brand: String,
      last_updated: Date
    }
  },
  search_keywords: [String],
  created_at: Date,
  updated_at: Date
}
```

### 3. Wishlists Collection
```javascript
{
  _id: ObjectId,
  user_id: ObjectId (ref: Users),
  product_id: ObjectId (ref: Products),
  added_at: Date,
  price_alerts: {
    enabled: Boolean (default: false),
    target_price: Number,
    platform: String
  }
}
```

### 4. Search History Collection (Optional)
```javascript
{
  _id: ObjectId,
  user_id: ObjectId (ref: Users),
  query: String,
  results_count: Number,
  searched_at: Date
}
```

## Indexes

```javascript
// Users
db.users.createIndex({ "email": 1 }, { unique: true })

// Products  
db.products.createIndex({ "normalized_title": "text", "search_keywords": "text" })
db.products.createIndex({ "platforms.amazon.price": 1 })
db.products.createIndex({ "platforms.flipkart.price": 1 })
db.products.createIndex({ "platforms.reliance_digital.price": 1 })

// Wishlists
db.wishlists.createIndex({ "user_id": 1, "product_id": 1 }, { unique: true })
db.wishlists.createIndex({ "user_id": 1 })

// Search History
db.search_history.createIndex({ "user_id": 1, "searched_at": -1 })
```