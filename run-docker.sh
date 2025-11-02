#!/bin/bash

# F4F Instagram Checker - Docker Runner Script
# This script helps you run the checker with Docker

set -e

echo "=================================="
echo "F4F Instagram Checker - Docker"
echo "=================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker is not installed."
    echo "Please install Docker from: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo "❌ Error: Docker is not running."
    echo "Please start Docker Desktop and try again."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found!"
    echo ""
    echo "Creating .env file..."
    echo "Please enter your Instagram credentials:"
    echo ""
    
    read -p "Instagram Username: " username
    read -sp "Instagram Password: " password
    echo ""
    
    cat > .env << EOF
INSTAGRAM_USERNAME=$username
INSTAGRAM_PASSWORD=$password
EOF
    
    echo "✅ .env file created successfully!"
    echo ""
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p results/csv results/text pickles

echo "✅ Directories ready"
echo ""

# Check if this is the first run
if [[ "$1" == "--rebuild" ]] || ! docker images | grep -q "f4f-checker"; then
    echo "🔨 Building Docker image (this may take a few minutes)..."
    docker-compose build
    echo "✅ Build complete!"
    echo ""
fi

echo "🚀 Starting F4F Instagram Checker..."
echo ""
echo "⏳ This may take several minutes depending on your follower/following count."
echo "   Results will be saved to ./results/ and ./pickles/"
echo ""

docker-compose up

echo ""
echo "✅ Done! Check the results/ folder for your data."
echo ""
echo "Cleaning up..."
docker-compose down

echo ""
echo "Run this script again anytime to check for unfollowers!"
echo ""

