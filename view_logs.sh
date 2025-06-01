#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Flask Application Logs ===${NC}"
echo -e "${GREEN}Press Ctrl+C to exit${NC}\n"

# Function to display logs with color
display_logs() {
    while true; do
        echo -e "\n${BLUE}=== $(date) ===${NC}"
        
        # Flask app logs
        if [ -f "logs/flask_app.log" ]; then
            echo -e "\n${GREEN}Flask Application Logs:${NC}"
            tail -n 20 logs/flask_app.log
        fi
        
        # Nginx logs (if accessible)
        if [ -f "/var/log/nginx/error.log" ]; then
            echo -e "\n${RED}Nginx Error Logs:${NC}"
            sudo tail -n 20 /var/log/nginx/error.log
        fi
        
        if [ -f "/var/log/nginx/access.log" ]; then
            echo -e "\n${GREEN}Nginx Access Logs:${NC}"
            sudo tail -n 20 /var/log/nginx/access.log
        fi
        
        sleep 5
    done
}

# Run the display function
display_logs 