# 🚀 Quick Setup Guide

## Prerequisites
- Python 3.8+
- Node.js 16+
- MongoDB Atlas account (free tier works)

## 1. Backend Setup

### Install Dependencies
```bash
cd /path/to/Scrapper
pip install -r requirements.txt
```

### Configure Environment
1. Copy `.env.example` to `.env`
2. Update the following variables in `.env`:

```bash
# Get this from MongoDB Atlas
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/scraper_db?retryWrites=true&w=majority
MONGODB_DB_NAME=scraper_db

# Optional local fallback for development
# MONGODB_FALLBACK_URI=mongodb://localhost:27017

# Generate a secure random key
JWT_SECRET_KEY=your-super-secret-jwt-key-here-make-it-long-and-random

# Update if frontend runs on different port
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

### Start Backend Server
```bash
python app.py
```
The API will be available at `http://localhost:8000`

## 2. Frontend Setup

### Install Dependencies
```bash
cd frontend
npm install
```

### Start Development Server
```bash
npm run dev
```
The frontend will be available at `http://localhost:5173`

## 3. MongoDB Atlas Setup

1. Go to [MongoDB Atlas](https://cloud.mongodb.com/)
2. Create a free account
3. Create a new cluster
4. Go to "Database Access" → Create a database user
5. Go to "Network Access" → Add IP address (0.0.0.0/0 for development)
6. Go to "Database" → Connect → "Connect your application"
7. Copy the connection string and update `MONGODB_URI` in `.env`

## 4. Test the Application

1. Open `http://localhost:5173` in your browser
2. Try searching for products (e.g., "laptop", "phone")
3. Click "Sign In" to create an account
4. Add products to wishlist using the heart button
5. Access wishlist and reports from the user menu

## 5. API Documentation

Once the backend is running, visit:
- Interactive API docs: `http://localhost:8000/docs`
- Alternative docs: `http://localhost:8000/redoc`

## Troubleshooting

### Backend Issues
- **MongoDB Connection Error**: Check your connection string and network access in MongoDB Atlas
- **Module Import Error**: Make sure all dependencies are installed with `pip install -r requirements.txt`
- **Port Already in Use**: Change `API_PORT` in `.env` or stop other services using port 8000

### Frontend Issues
- **CORS Error**: Make sure backend is running and `ALLOWED_ORIGINS` includes your frontend URL
- **API Connection Error**: Verify backend is running on `http://localhost:8000`
- **Build Error**: Run `npm install` to ensure all dependencies are installed

### Database Issues
- **Authentication Error**: Verify MongoDB Atlas username/password in connection string
- **Network Error**: Check Network Access settings in MongoDB Atlas
- **Collection Not Found**: The app will create collections automatically on first use

## Features to Test

### 🔐 Authentication
- Sign up with email and password
- Login and logout functionality
- Persistent sessions across browser refreshes

### 💝 Wishlist
- Add products to wishlist (heart button)
- View wishlist from user menu
- Remove products from wishlist
- Wishlist persistence across sessions

### 📊 Reports
- Generate lowest price reports
- View price comparisons across platforms
- Export data via direct links

### 🛒 Product Search
- Search across Amazon, Flipkart, and Reliance Digital
- Real-time price comparison
- Product details with ratings and reviews

## Production Deployment Tips

1. **Security**: Change `JWT_SECRET_KEY` to a strong random key
2. **CORS**: Update `ALLOWED_ORIGINS` to your production domain
3. **Database**: Use a dedicated MongoDB cluster for production
4. **Environment**: Set `DEBUG=false` and `ENVIRONMENT=production`
5. **HTTPS**: Use SSL certificates for production deployment

## Need Help?

Check the logs in the terminal where you started the servers for detailed error messages. Most issues are related to:
1. Missing environment variables
2. Database connection problems
3. Port conflicts
4. Missing dependencies