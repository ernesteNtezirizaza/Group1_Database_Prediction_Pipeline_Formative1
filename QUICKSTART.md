# Quick Start Guide

## Prerequisites

Before starting, ensure you have:
- Python 3.8 or higher
- MySQL 8.0+ installed and running
- MongoDB 4.4+ installed and running

## Installation

### Step 1: Clone and Setup

```bash
# Clone the repository
git clone git@github.com:ernesteNtezirizaza/Group1_Database_Prediction_Pipeline_Formative1.git
cd Group1_Database_Prediction_Pipeline_Formative1

# Run setup script (if on Linux/Mac)
./setup.sh

# OR manually setup virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Step 2: Configure Database

Create a `.env` file in the project root:

```env
MYSQL_HOST=your_host_here
MYSQL_USER=your_user_here
MYSQL_PASSWORD=your_password_here
MYSQL_DATABASE=your_database_here

MONGO_HOST=your_host_here
MONGO_PORT=your_port_here
MONGO_DATABASE=your_database_here

```

### Step 3: Setup MySQL Database

```bash
mysql -u root -p < database setup/setup_mysql_database.sql
```

Or manually in MySQL:
```sql
source ./database setup/setup_mysql_database.sql;
```

### Step 4: Load Data

**Load into MySQL:**
```bash
python scripts/load_data_mysql.py hotel_bookings.csv
```

**Load into MongoDB:**
```bash
python scripts/load_data_mongodb.py hotel_bookings.csv
```

### Step 5: Train ML Model

```bash
python scripts/train_model.py
```

This will create:
- `models/cancellation_model.pkl`
- `models/feature_preprocessor.pkl`
- `models/meal_encoder.pkl`
- `models/deposit_encoder.pkl`

### Step 6: Start API Server

```bash
python main.py
```

Or with uvicorn:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: https://group1-database-prediction-pipeline.onrender.com
- **Docs**: https://group1-database-prediction-pipeline.onrender.com/docs
- **Health**: https://group1-database-prediction-pipeline.onrender.com/health

### Step 7: Test API

Open a new terminal and run:
```bash
python tests/test_api.py
```

### Step 8: Run Predictions

```bash
python scripts/prediction_script.py
```

This will:
1. Fetch latest bookings from API
2. Make cancellation predictions
3. Save results to JSON file

## Common Issues

### Issue: "Module not found"
**Solution**: Ensure virtual environment is activated and dependencies are installed
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: "Can't connect to MySQL"
**Solution**: 
1. Check MySQL is running: `sudo service mysql start`
2. Verify credentials in `.env`
3. Ensure database exists

**Solution**:
1. Check MongoDB is running: `sudo service mongod start`
2. Verify connection string in `.env`

### Issue: "No booking data"
**Solution**: Load data first
```bash
python load_data_mysql.py hotel_bookings.csv
```

### Issue: "Model not found"
**Solution**: Train the model first
```bash
python scripts/train_model.py
```

## Verifying Installation

Run these commands to verify everything works:

```bash
# 1. Check Python version
python --version  # Should be 3.8+

# 2. Check MySQL connection
mysql -u root -p -e "USE hotel_booking_db; SHOW TABLES;"

# 3. Check MongoDB connection
mongosh --eval "db.stats()"

# 4. Check API is running
curl https://group1-database-prediction-pipeline.onrender.com/health

# 5. Run all tests
python test_api.py
```

## Next Steps

1. Explore API documentation: https://group1-database-prediction-pipeline.onrender.com/docs
2. Try different endpoints
3. Run predictions on new data
4. Analyze prediction results
5. Review `README.md` for detailed documentation

## Project Structure

```
ml-group-1-drafttt/
├── hotel_bookings.csv          # Dataset
├── requirements.txt             # Dependencies
├── README.md                    # Full documentation
├── QUICKSTART.md               # This file
├── PROJECT_CHECKLIST.md         # Checklist
│
├── Database/
│   ├── setup_mysql_database.sql    # MySQL schema
│   ├── load_data_mysql.py          # MySQL loader
│   └── load_data_mongodb.py        # MongoDB loader
│
├── API/
│   └── main.py                     # FastAPI app
│
├── ML/
│   ├── train_model.py              # Model training
│   └── prediction_script.py        # Predictions
│
└── Tests/
    └── test_api.py                 # API tests
```

## Getting Help

1. Check `README.md` for detailed documentation
2. Check `PROJECT_CHECKLIST.md` for requirements
3. Review API docs at https://group1-database-prediction-pipeline.onrender.com/docs
4. Contact team members

## Key Files

| File                       | Purpose                                |
| -------------------------- | -------------------------------------- |
| `main.py`                  | FastAPI application with all endpoints |
| `setup_mysql_database.sql` | Database schema and setup              |
| `train_model.py`           | Train ML model                         |
| `prediction_script.py`     | Make predictions                       |
| `test_api.py`              | Test all endpoints                     |
| `README.md`                | Complete documentation                 |

---

**Ready to use!** 
