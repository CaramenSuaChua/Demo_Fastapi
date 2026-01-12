#!/bin/bash
set -e

echo "🚀 Starting FastAPI LLM Server with Docker..."

# Check if docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Build and run
cd docker
docker-compose up --build -d

echo "✅ Server is starting..."
echo "📡 API will be available at: http://localhost:8000"
echo "📝 API Docs: http://localhost:8000/docs"
echo ""
echo "📊 To check logs: docker-compose logs -f"
echo "🛑 To stop: docker-compose down"