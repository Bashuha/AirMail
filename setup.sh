#!/bin/bash

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}--- Setup environment (Docker) ---${NC}\n"

# Clean .env
> .env

# 1. Mandatory field: USER
input_user=""
while [ -z "$input_user" ]; do
    read -p "Enter RabbitMQ user (mandatory): " input_user
done
echo "RMQ_USER=$input_user" >> .env

# 2. Mandatory field: PASSWORD (hidden input)
input_pass=""
while [ -z "$input_pass" ]; do
    read -s -p "Enter RabbitMQ password (mandatory): " input_pass
    echo "" # New line after hidden input
done
echo "RMQ_PASSWORD=$input_pass" >> .env

# 3. Mandatory SMTP fields
smtp_user=""
while [ -z "$smtp_user" ]; do
    read -p "Enter SMTP user (mandatory): " smtp_user
done
echo "SMTP_USER=$smtp_user" >> .env

smtp_pass=""
while [ -z "$smtp_pass" ]; do
    read -s -p "Enter SMTP password (mandatory): " smtp_pass
    echo ""
done
echo "SMTP_PASSWORD=$smtp_pass" >> .env

smtp_from=""
while [ -z "$smtp_from" ]; do
    read -p "Enter SMTP from email (mandatory): " smtp_from
done
echo "SMTP_FROM=$smtp_from" >> .env

echo -e "\n${GREEN}.env file created.${NC}"

# 5. Start containers
echo -e "${YELLOW}Starting containers...${NC}"
docker compose up -d --build

# 6. Check status
sleep 3
docker compose ps