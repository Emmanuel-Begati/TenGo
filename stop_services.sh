#!/bin/bash

# TenGo Django Application Stop Script

echo "🛑 Stopping TenGo Application Services..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to stop Django server
stop_django() {
    echo -e "${BLUE}🛑 Stopping Django server on port 8060...${NC}"
    if lsof -ti:8060 > /dev/null; then
        kill -9 $(lsof -ti:8060) 2>/dev/null
        sleep 2
        if ! lsof -ti:8060 > /dev/null; then
            echo -e "${GREEN}✅ Django server stopped${NC}"
        else
            echo -e "${RED}❌ Failed to stop Django server${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  Django server not running on port 8060${NC}"
    fi
}

# Function to stop Redis (optional)
stop_redis() {
    read -p "Do you want to stop Redis server? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${BLUE}🛑 Stopping Redis server...${NC}"
        if pgrep -f "redis-server" > /dev/null; then
            sudo systemctl stop redis 2>/dev/null || pkill redis-server
            sleep 2
            if ! pgrep -f "redis-server" > /dev/null; then
                echo -e "${GREEN}✅ Redis server stopped${NC}"
            else
                echo -e "${RED}❌ Failed to stop Redis server${NC}"
            fi
        else
            echo -e "${YELLOW}⚠️  Redis server not running${NC}"
        fi
    fi
}

# Main execution
main() {
    echo -e "${BLUE}🎯 TenGo Application Shutdown${NC}"
    echo "================================"
    
    # Stop Django
    stop_django
    
    # Optionally stop Redis
    stop_redis
    
    echo ""
    echo -e "${GREEN}🎉 Services stopped successfully!${NC}"
}

# Run if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
