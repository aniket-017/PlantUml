#!/bin/bash

# Setup script for CSV to PlantUML Generator Frontend

echo "🚀 Setting up CSV to PlantUML Generator Frontend..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm first."
    exit 1
fi

echo "✅ Node.js $(node --version) and npm $(npm --version) found"

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Install additional required packages
echo "📦 Installing additional packages..."
npm install react-router-dom axios lucide-react

# Install Tailwind CSS and related packages
echo "🎨 Installing Tailwind CSS..."
npm install -D tailwindcss@latest postcss@latest autoprefixer@latest

echo "✅ All dependencies installed successfully!"

echo ""
echo "🎉 Setup complete! You can now run the development server:"
echo ""
echo "  npm run dev"
echo ""
echo "Then open http://localhost:5173 in your browser."
echo ""
echo "Make sure your backend server is running on http://127.0.0.1:8000"