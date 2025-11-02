#!/bin/bash

# Hotel Booking System - Setup Script
# This script automates the setup process for the project

echo "========================================="
echo "Hotel Booking System - Setup"
echo "========================================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Python 3 is installed
echo -e "${YELLOW}Checking Python installation...${NC}"
if command -v python &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}Found: $PYTHON_VERSION${NC}"
else
    echo -e "${RED}Python 3 is not installed. Please install Python 3.8 or higher.${NC}"
    exit 1
fi

# Check if pip is installed
echo -e "${YELLOW}Checking pip installation...${NC}"
if command -v pip3 &> /dev/null; then
    echo -e "${GREEN}Found pip3${NC}"
else
    echo -e "${RED}pip3 is not installed. Please install pip.${NC}"
    exit 1
fi

# Create virtual environment
echo -e "${YELLOW}Creating virtual environment...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}Virtual environment created${NC}"
else
    echo -e "${YELLOW}Virtual environment already exists${NC}"
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate

# Install dependencies
echo -e "${YELLOW}Installing Python dependencies...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

echo -e "${GREEN}Dependencies installed successfully${NC}"

# Check if MySQL is installed
echo -e "${YELLOW}Checking MySQL installation...${NC}"
if command -v mysql &> /dev/null; then
    echo -e "${GREEN}Found MySQL${NC}"
    echo -e "${YELLOW}Note: You may need to manually setup MySQL database${NC}"
    echo -e "${YELLOW}Run: mysql -u root -p < setup_mysql_database.sql${NC}"
else
    echo -e "${RED}MySQL is not installed or not in PATH${NC}"
fi

# Check if MongoDB is installed
echo -e "${YELLOW}Checking MongoDB installation...${NC}"
if command -v mongod &> /dev/null || command -v mongosh &> /dev/null; then
    echo -e "${GREEN}Found MongoDB${NC}"
    echo -e "${YELLOW}Note: Ensure MongoDB service is running${NC}"
else
    echo -e "${RED}MongoDB is not installed or not in PATH${NC}"
fi

# Create necessary directories
echo -e "${YELLOW}Creating output directories...${NC}"
mkdir -p output
mkdir -p logs

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Creating .env file from template...${NC}"
    cat > .env << EOL
# MySQL Configuration
MYSQL_HOST=your_host_here
MYSQL_USER=your_user_here
MYSQL_PASSWORD=your_password_here
MYSQL_DATABASE=your_database_here

# MongoDB Configuration
MONGO_HOST=your_host_here
MONGO_PORT=your_port_here
MONGO_DATABASE=your_database_here

# API Configuration
API_BASE_URL=https://group1-database-prediction-pipeline.onrender.com
EOL
    echo -e "${GREEN}.env file created${NC}"
    echo -e "${YELLOW}Please update .env with your database credentials${NC}"
else
    echo -e "${YELLOW}.env file already exists${NC}"
fi

echo ""
echo "========================================="
echo -e "${GREEN}Setup completed!${NC}"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Update .env file with your database credentials"
echo "2. Setup MySQL database: mysql -u root -p < setup_mysql_database.sql"
echo "3. Load data into MySQL: python scripts/load_data_mysql.py hotel_bookings.csv"
echo "4. Load data into MongoDB: python scripts/load_data_mongodb.py hotel_bookings.csv"
echo "5. Train ML model: python train_model.py"
echo "6. Start API server: python main.py"
echo ""
echo "Activate virtual environment anytime with:"
echo "  source venv/bin/activate"
echo ""
