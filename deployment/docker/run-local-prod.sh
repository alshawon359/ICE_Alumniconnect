#!/bin/bash
set -e

COMPOSE_FILE="deployment/docker/docker-compose.prod.yml"
BACKEND_HEALTH_URL="http://localhost:5001/api/health"
FRONTEND_URL="http://localhost:8080"

echo "🚀 Starting AlumniConnect Local Production Simulation..."
echo ""

# Start services
echo "📦 Building and starting Docker containers..."
docker compose -f "$COMPOSE_FILE" up --build -d

echo "⏳ Waiting for services to be ready..."
sleep 5

# Wait for backend health
MAX_RETRIES=30
RETRY_COUNT=0
until curl -f -s "$BACKEND_HEALTH_URL" > /dev/null 2>&1 || [ $RETRY_COUNT -eq $MAX_RETRIES ]; do
    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo "   Attempt $RETRY_COUNT/$MAX_RETRIES - waiting for backend..."
    sleep 2
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo "❌ Backend failed to become healthy. Check logs:"
    docker compose -f "$COMPOSE_FILE" logs backend
    exit 1
fi

echo ""
echo "✅ All services are healthy!"
echo ""
echo "🌐 Access the application:"
echo "   Frontend: $FRONTEND_URL"
echo "   API Health: $BACKEND_HEALTH_URL"
echo ""
echo "📊 View logs:"
echo "   docker compose -f $COMPOSE_FILE logs -f"
echo ""
echo "🛑 Stop services:"
echo "   docker compose -f $COMPOSE_FILE down"
echo ""
