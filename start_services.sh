#!/bin/bash

# TenGo Django Application Startup Script
# This script starts Redis, Django ASGI server, and provides nginx configuration

PROJECT_DIR="/home/thisisemmanuel-tengo/htdocs/tengo.thisisemmanuel.pro"
VENV_PATH="$PROJECT_DIR/venv"  # Adjust if your virtual environment is elsewhere

echo "🚀 Starting TenGo Application Services..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to check if a service is running
check_service() {
    if pgrep -f "$1" > /dev/null; then
        echo -e "${GREEN}✅ $2 is running${NC}"
        return 0
    else
        echo -e "${RED}❌ $2 is not running${NC}"
        return 1
    fi
}

# Function to start Redis
start_redis() {
    echo -e "${BLUE}🔧 Starting Redis server...${NC}"
    if command -v redis-server &> /dev/null; then
        if ! check_service "redis-server" "Redis"; then
            redis-server --daemonize yes --port 6379
            sleep 2
            if check_service "redis-server" "Redis"; then
                echo -e "${GREEN}✅ Redis started successfully${NC}"
            else
                echo -e "${YELLOW}⚠️  Redis failed to start, using in-memory channel layer${NC}"
            fi
        fi
    else
        echo -e "${YELLOW}⚠️  Redis not installed, using in-memory channel layer${NC}"
        echo -e "${BLUE}💡 To install Redis: sudo apt-get install redis-server${NC}"
    fi
}

# Function to activate virtual environment
activate_venv() {
    if [ -d "$VENV_PATH" ]; then
        echo -e "${BLUE}🐍 Activating virtual environment...${NC}"
        source "$VENV_PATH/bin/activate"
        echo -e "${GREEN}✅ Virtual environment activated${NC}"
    else
        echo -e "${YELLOW}⚠️  Virtual environment not found at $VENV_PATH${NC}"
        echo -e "${BLUE}💡 Please ensure your virtual environment is set up${NC}"
    fi
}

# Function to run Django migrations
run_migrations() {
    echo -e "${BLUE}🔄 Running Django migrations...${NC}"
    cd "$PROJECT_DIR"
    python manage.py migrate
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Migrations completed${NC}"
    else
        echo -e "${RED}❌ Migrations failed${NC}"
        exit 1
    fi
}

# Function to clear caches if needed
clear_caches() {
    echo -e "${BLUE}🧹 Clearing caches...${NC}"
    cd "$PROJECT_DIR"
    
    # Clear Python cache
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.pyc" -delete 2>/dev/null || true
    
    # Clear Django cache if possible
    if [ -d "$VENV_PATH" ]; then
        source "$VENV_PATH/bin/activate"
        python manage.py shell -c "
from django.core.cache import cache
try:
    cache.clear()
    print('Cache cleared')
except:
    pass
" 2>/dev/null || true
    fi
    
    echo -e "${GREEN}✅ Caches cleared${NC}"
}

# Function to collect static files
collect_static() {
    echo -e "${BLUE}📁 Collecting static files (fresh)...${NC}"
    cd "$PROJECT_DIR"
    
    # Force fresh collection
    python manage.py collectstatic --noinput --clear
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Static files collected fresh${NC}"
    else
        echo -e "${RED}❌ Static file collection failed${NC}"
        exit 1
    fi
}

# Function to start Django ASGI server
start_django() {
    echo -e "${BLUE}🌐 Starting Django ASGI server on port 8060 (fresh)...${NC}"
    cd "$PROJECT_DIR"
    
    # Kill any existing Django processes on port 8060
    if lsof -ti:8060 > /dev/null; then
        echo -e "${YELLOW}⚠️  Killing existing process on port 8060${NC}"
        kill -9 $(lsof -ti:8060) 2>/dev/null || true
        sleep 2
    fi
    
    # Remove old log file
    rm -f django.log
    
    # Start Django with Daphne (ASGI server)
    echo -e "${BLUE}🚀 Starting fresh Daphne ASGI server...${NC}"
    nohup daphne -b 0.0.0.0 -p 8060 TenGo.asgi:application > django.log 2>&1 &
    
    sleep 3
    
    if lsof -ti:8060 > /dev/null; then
        echo -e "${GREEN}✅ Django ASGI server started fresh on port 8060${NC}"
        echo -e "${BLUE}📊 Server logs: tail -f $PROJECT_DIR/django.log${NC}"
    else
        echo -e "${RED}❌ Failed to start Django server${NC}"
        echo -e "${BLUE}📊 Check logs: cat $PROJECT_DIR/django.log${NC}"
        exit 1
    fi
}

# Function to show nginx configuration
show_nginx_config() {
    echo -e "${BLUE}📝 Nginx configuration saved to: $PROJECT_DIR/nginx_config.conf${NC}"
    echo -e "${YELLOW}🔧 To apply nginx configuration:${NC}"
    echo -e "${BLUE}   sudo cp $PROJECT_DIR/nginx_config.conf /etc/nginx/sites-available/tengo${NC}"
    echo -e "${BLUE}   sudo ln -sf /etc/nginx/sites-available/tengo /etc/nginx/sites-enabled/tengo${NC}"
    echo -e "${BLUE}   sudo nginx -t${NC}"
    echo -e "${BLUE}   sudo systemctl reload nginx${NC}"
}

# Main execution
main() {
    echo -e "${BLUE}🎯 TenGo Application Startup${NC}"
    echo "================================"
    
    # Parse arguments for refresh option
    if [[ "$1" == "--refresh" ]] || [[ "$1" == "-r" ]]; then
        echo -e "${YELLOW}🔄 Running with cache refresh...${NC}"
        clear_caches
    fi
    
    # Start Redis
    start_redis
    
    # Activate virtual environment
    activate_venv
    
    # Run migrations
    run_migrations
    
    # Collect static files
    collect_static
    
    # Start Django
    start_django
    
    # Show nginx configuration instructions
    show_nginx_config
    
    echo ""
    echo -e "${GREEN}🎉 All services started successfully!${NC}"
    echo -e "${BLUE}🌐 Your application should be available at: https://tengo.thisisemmanuel.pro${NC}"
    echo -e "${BLUE}📊 WebSocket endpoint: wss://tengo.thisisemmanuel.pro/ws/delivery/${NC}"
    echo -e "${BLUE}📊 Restaurant WebSocket: wss://tengo.thisisemmanuel.pro/ws/restaurant/{restaurant_id}/${NC}"
    echo ""
    echo -e "${YELLOW}📋 Service Status:${NC}"
    check_service "redis-server" "Redis"
    check_service "daphne.*8060" "Django ASGI Server"
    echo ""
    echo -e "${BLUE}🛠️  Useful commands:${NC}"
    echo -e "${BLUE}   Stop Django: kill \$(lsof -ti:8060)${NC}"
    echo -e "${BLUE}   Stop Redis: sudo systemctl stop redis${NC}"
    echo -e "${BLUE}   View Django logs: tail -f $PROJECT_DIR/django.log${NC}"
    echo -e "${BLUE}   Test WebSocket: wscat -c ws://localhost:8060/ws/delivery/${NC}"
}

# Run if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
