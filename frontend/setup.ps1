# Setup script for CSV to PlantUML Generator Frontend (PowerShell)

Write-Host "🚀 Setting up CSV to PlantUML Generator Frontend..." -ForegroundColor Green

# Check if Node.js is installed
try {
    $nodeVersion = node --version
    Write-Host "✅ Node.js $nodeVersion found" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js is not installed. Please install Node.js 18+ first." -ForegroundColor Red
    exit 1
}

# Check if npm is installed
try {
    $npmVersion = npm --version
    Write-Host "✅ npm $npmVersion found" -ForegroundColor Green
} catch {
    Write-Host "❌ npm is not installed. Please install npm first." -ForegroundColor Red
    exit 1
}

# Install dependencies
Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
npm install

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
    exit 1
}

# Install additional required packages
Write-Host "📦 Installing additional packages..." -ForegroundColor Yellow
npm install react-router-dom axios lucide-react

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install additional packages" -ForegroundColor Red
    exit 1
}

Write-Host "✅ All dependencies installed successfully!" -ForegroundColor Green

Write-Host ""
Write-Host "🎉 Setup complete! You can now run the development server:" -ForegroundColor Green
Write-Host ""
Write-Host "  npm run dev" -ForegroundColor Cyan
Write-Host ""
Write-Host "Then open http://localhost:5173 in your browser." -ForegroundColor White
Write-Host ""
Write-Host "Make sure your backend server is running on http://127.0.0.1:8000" -ForegroundColor Yellow