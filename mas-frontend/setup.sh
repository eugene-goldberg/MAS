#!/bin/bash

echo "🚀 Setting up MAS Testing Frontend..."

# Backend setup
echo "📦 Setting up backend..."
cd backend

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "Installing backend dependencies..."
pip install -r requirements.txt

# Create .env file from example
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please update backend/.env with your configuration"
fi

cd ..

# Frontend setup
echo "📦 Setting up frontend..."
cd frontend

# Install dependencies
echo "Installing frontend dependencies..."
npm install

# Create .env file from example
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
fi

cd ..

echo "✅ Setup complete!"
echo ""
echo "To start the services:"
echo ""
echo "Backend:"
echo "  cd backend"
echo "  source venv/bin/activate"
echo "  python -m app.main"
echo ""
echo "Frontend:"
echo "  cd frontend"
echo "  npm start"
echo ""
echo "Or use Docker:"
echo "  docker-compose up --build"