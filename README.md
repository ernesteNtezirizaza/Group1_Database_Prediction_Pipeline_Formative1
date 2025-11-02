# Hotel Booking Management System - Database & Prediction Pipeline

A comprehensive database and machine learning pipeline system for managing hotel bookings and predicting cancellations.

## Project Overview

This project implements a complete database system with both relational (MySQL) and NoSQL (MongoDB) databases, a RESTful API using FastAPI, and a machine learning pipeline for predicting booking cancellations.

## Table of Contents

- [Quick Start](#quick-start)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Database Schema](#database-schema)
- [Installation](#installation)
- [Setup](#setup)
- [API Endpoints](#api-endpoints)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Additional Resources](#additional-resources)
- [License](#license)

## Quick Start

For a detailed quick start guide, see:
- **[QUICKSTART.md](QUICKSTART.md)** - Step-by-step setup and usage guide

## Features

### Database Features
- **MySQL Database**: Normalized relational database (3NF) with 5 main tables
- **MongoDB Database**: Document-based NoSQL database with embedded documents
- **Stored Procedures**: Data validation and statistics calculation
- **Triggers**: Automated logging of booking changes
- **Indexes**: Optimized query performance
- **ML Prediction Tracking**: Dedicated predictions table for storing ML model results

### API Features
- **Dual Database Support**: CRUD operations for both MySQL and MongoDB
- **CRUD Operations**: Full Create, Read, Update, Delete functionality (20+ endpoints per database)
- **RESTful Design**: Clean and intuitive API endpoints with OpenAPI docs
- **Input Validation**: Comprehensive data validation using Pydantic
- **Error Handling**: Proper HTTP status codes and error messages
- **Statistics**: Real-time booking statistics
- **Prediction Logs**: Access ML prediction history and logs via API

### ML Features
- **Cancellation Prediction**: Random Forest classifier
- **Feature Engineering**: Automated feature preparation
- **Model Training**: Training pipeline with cross-validation
- **Batch Prediction**: Process multiple bookings at once
- **Prediction Persistence**: Automatically saves predictions to both MySQL and MongoDB
- **Model Versioning**: Track different model versions and their performance

## Technology Stack

- **Backend**: Python 3.8+, FastAPI
- **Databases**: MySQL 8.0+, MongoDB 4.4+
- **Machine Learning**: scikit-learn, pandas, numpy
- **API Documentation**: Swagger/OpenAPI (automatic with FastAPI)

## Database Schema

### MySQL Tables

#### 1. hotels
- hotel_id (PK, AUTO_INCREMENT)
- hotel_name (VARCHAR, UNIQUE)
- created_at (TIMESTAMP)

#### 2. guests
- guest_id (PK, AUTO_INCREMENT)
- country (VARCHAR(3))
- is_repeated_guest (BOOLEAN)
- customer_type (VARCHAR)
- created_at (TIMESTAMP)

#### 3. bookings
- booking_id (PK, AUTO_INCREMENT)
- hotel_id (FK → hotels)
- guest_id (FK → guests)
- lead_time, arrival_date fields
- guest information, room details
- status information
- created_at (TIMESTAMP)

#### 4. booking_logs
- log_id (PK, AUTO_INCREMENT)
- booking_id (FK → bookings)
- action (VARCHAR)
- old_status, new_status (VARCHAR)
- timestamp (TIMESTAMP)

#### 5. predictions
- prediction_id (PK, AUTO_INCREMENT)
- booking_id (FK → bookings)
- predicted_canceled (BOOLEAN)
- cancellation_probability (DECIMAL(5,4))
- not_cancelled_probability (DECIMAL(5,4))
- features_used (INT)
- model_version (VARCHAR)
- prediction_timestamp (TIMESTAMP)
- notes (TEXT)

### Stored Procedures
- `sp_validate_booking`: Validates booking data before insertion
- `sp_get_booking_statistics`: Returns aggregated booking statistics

### Triggers
- `trg_booking_after_update`: Logs status changes
- `trg_booking_after_insert`: Logs new bookings

### MongoDB Collections
- `hotels`: Hotel documents with metadata
- `guests`: Guest documents with attributes
- `bookings`: Denormalized booking documents with embedded hotel/guest info
- `predictions`: ML prediction results with model metadata

See `docs/database_schema_design.md` for detailed ERD and schema documentation.

## Installation

### Prerequisites
- Python 3.8 or higher
- MySQL 8.0+ server
- MongoDB 4.4+ server

### Python Dependencies

```bash
pip install -r requirements.txt
```

### Database Setup

1. **MySQL Setup**:
```bash
mysql -u root -p < "database setup/setup_mysql_database.sql"
```

2. **MongoDB Setup**:
MongoDB will automatically create the database when you first insert data.

## Setup

### 1. Configure Database Connections

Create a `.env` file in the project root:

```env
MYSQL_HOST=your_host
MYSQL_USER=your_user
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=your_database

MONGO_HOST=your_host
MONGO_PORT=your_port
MONGO_DATABASE=your_database

API_BASE_URL=https://group1-database-prediction-pipeline.onrender.com
```

### 2. Load Data

**MySQL**:
```bash
python scripts/load_data_mysql.py hotel_bookings.csv
```

**MongoDB**:
```bash
python scripts/load_data_mongodb.py hotel_bookings.csv
```

### 3. Train Machine Learning Model

```bash
python scripts/train_model.py
```

This will create in the `models/` directory:
- `cancellation_model.pkl`: Trained Random Forest model
- `feature_preprocessor.pkl`: Feature preprocessor
- `meal_encoder.pkl` and `deposit_encoder.pkl`: Label encoders

### 4. Start FastAPI Server

```bash
python main.py
# OR
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

API will be available at:
- API Base: https://group1-database-prediction-pipeline.onrender.com
- Interactive Docs: https://group1-database-prediction-pipeline.onrender.com/docs
- OpenAPI Schema: https://group1-database-prediction-pipeline.onrender.com/openapi.json

### 5. Run Prediction Script

```bash
python scripts/prediction_script.py
```

This will:
- Fetch bookings from the API
- Make cancellation predictions using the trained model
- Save predictions to both MySQL and MongoDB databases
- Generate a JSON file with prediction results

## API Endpoints

### Guests

| Method | Endpoint              | Description                |
| ------ | --------------------- | -------------------------- |
| POST   | `/api/v1/guests`      | Create a new guest         |
| GET    | `/api/v1/guests`      | Get all guests (paginated) |
| GET    | `/api/v1/guests/{id}` | Get guest by ID            |
| PUT    | `/api/v1/guests/{id}` | Update guest               |
| DELETE | `/api/v1/guests/{id}` | Delete guest               |

### Hotels

| Method | Endpoint              | Description        |
| ------ | --------------------- | ------------------ |
| POST   | `/api/v1/hotels`      | Create a new hotel |
| GET    | `/api/v1/hotels`      | Get all hotels     |
| GET    | `/api/v1/hotels/{id}` | Get hotel by ID    |
| PUT    | `/api/v1/hotels/{id}` | Update hotel       |
| DELETE | `/api/v1/hotels/{id}` | Delete hotel       |

### Bookings

| Method | Endpoint                | Description                              |
| ------ | ----------------------- | ---------------------------------------- |
| POST   | `/api/v1/bookings`      | Create a new booking                     |
| GET    | `/api/v1/bookings`      | Get all bookings (paginated, filterable) |
| GET    | `/api/v1/bookings/{id}` | Get booking by ID                        |
| PUT    | `/api/v1/bookings/{id}` | Update booking                           |
| DELETE | `/api/v1/bookings/{id}` | Delete booking                           |

### Statistics & Logs

| Method | Endpoint                | Description             |
| ------ | ----------------------- | ----------------------- |
| GET    | `/api/v1/statistics`    | Get booking statistics  |
| GET    | `/api/v1/bookings/logs` | Get booking change logs |

### Predictions (MySQL)

| Method | Endpoint                            | Description                                 |
| ------ | ----------------------------------- | ------------------------------------------- |
| GET    | `/api/v1/predictions/logs`          | Get all predictions (filterable, paginated) |
| GET    | `/api/v1/predictions/logs/{id}`     | Get specific prediction by ID               |
| GET    | `/api/v1/bookings/{id}/predictions` | Get all predictions for a specific booking  |

### Predictions (MongoDB)

| Method | Endpoint                                  | Description                                 |
| ------ | ----------------------------------------- | ------------------------------------------- |
| GET    | `/api/v1/mongo/predictions/logs`          | Get all predictions (filterable, paginated) |
| GET    | `/api/v1/mongo/predictions/logs/{id}`     | Get specific prediction by ID               |
| GET    | `/api/v1/mongo/bookings/{id}/predictions` | Get all predictions for a specific booking  |

### MongoDB Endpoints

**Note**: MongoDB uses ObjectId strings instead of integer IDs

#### Guests
| Method | Endpoint                    | Description                |
| ------ | --------------------------- | -------------------------- |
| POST   | `/api/v1/mongo/guests`      | Create a new guest         |
| GET    | `/api/v1/mongo/guests`      | Get all guests (paginated) |
| GET    | `/api/v1/mongo/guests/{id}` | Get guest by ID            |
| PUT    | `/api/v1/mongo/guests/{id}` | Update guest               |
| DELETE | `/api/v1/mongo/guests/{id}` | Delete guest               |

#### Hotels
| Method | Endpoint                    | Description        |
| ------ | --------------------------- | ------------------ |
| POST   | `/api/v1/mongo/hotels`      | Create a new hotel |
| GET    | `/api/v1/mongo/hotels`      | Get all hotels     |
| GET    | `/api/v1/mongo/hotels/{id}` | Get hotel by ID    |
| PUT    | `/api/v1/mongo/hotels/{id}` | Update hotel       |
| DELETE | `/api/v1/mongo/hotels/{id}` | Delete hotel       |

#### Bookings
| Method | Endpoint                      | Description                              |
| ------ | ----------------------------- | ---------------------------------------- |
| POST   | `/api/v1/mongo/bookings`      | Create a new booking                     |
| GET    | `/api/v1/mongo/bookings`      | Get all bookings (paginated, filterable) |
| GET    | `/api/v1/mongo/bookings/{id}` | Get booking by ID                        |
| PUT    | `/api/v1/mongo/bookings/{id}` | Update booking                           |
| DELETE | `/api/v1/mongo/bookings/{id}` | Delete booking                           |

### Health Check

| Method | Endpoint  | Description     |
| ------ | --------- | --------------- |
| GET    | `/health` | Health check    |
| GET    | `/`       | API information |

## Usage

### Example API Calls

**Create a Guest**:
```bash
curl -X POST "https://group1-database-prediction-pipeline.onrender.com/api/v1/guests" \
  -H "Content-Type: application/json" \
  -d '{
    "country": "USA",
    "is_repeated_guest": false,
    "customer_type": "Transient"
  }'
```

**Get All Bookings**:
```bash
curl "https://group1-database-prediction-pipeline.onrender.com/api/v1/bookings?limit=10&skip=0"
```

**Get Statistics**:
```bash
curl "https://group1-database-prediction-pipeline.onrender.com/api/v1/statistics"
```

**Make Predictions**:
```bash
python scripts/prediction_script.py
```

**Get Prediction Logs**:
```bash
curl "https://group1-database-prediction-pipeline.onrender.com/api/v1/predictions/logs?limit=10"
```

**Get Predictions for a Booking**:
```bash
curl "https://group1-database-prediction-pipeline.onrender.com/api/v1/bookings/1/predictions"
```

**MongoDB Example - Create Guest**:
```bash
curl -X POST "https://group1-database-prediction-pipeline.onrender.com/api/v1/mongo/guests" \
  -H "Content-Type: application/json" \
  -d '{
    "country": "USA",
    "is_repeated_guest": false,
    "customer_type": "Transient"
  }'
```

**MongoDB Example - Get All Bookings**:
```bash
curl "https://group1-database-prediction-pipeline.onrender.com/api/v1/mongo/bookings?limit=10&skip=0"
```

## Project Structure

```
Group1_Database_Prediction_Pipeline_Formative1/
├── hotel_bookings.csv              # Source dataset
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── QUICKSTART.md                   # Quick start guide
├── main.py                         # FastAPI application entry point
│
├── api/                            # API modules
│   ├── mysql_api.py               # MySQL API endpoints
│   └── mongodb_api.py             # MongoDB API endpoints
│
├── database setup/                 # Database setup files
│   └── setup_mysql_database.sql   # MySQL schema and setup
│
├── scripts/                        # Utility scripts
│   ├── load_data_mysql.py         # MySQL data loader
│   ├── load_data_mongodb.py       # MongoDB data loader
│   ├── train_model.py             # Model training script
│   └── prediction_script.py       # Prediction script
│
├── models/                         # ML model files
│   ├── cancellation_model.pkl     # Trained model
│   ├── feature_preprocessor.pkl   # Feature preprocessor
│   ├── meal_encoder.pkl           # Meal type encoder
│   └── deposit_encoder.pkl        # Deposit type encoder
│
├── docs/                           # Documentation
│   └── database_schema_design.md  # Database schema with ERD
│
├── erd/                            # ERD generation files
│   ├── generate_erd.py            # Python script to generate ERD
│   ├── dbdiagram_erd.dbml         # dbdiagram.io code
│   └── ERD_Diagram_image.png      # Generated ERD image
│
├── tests/                          # Test files
│   └── test_api.py                # API tests
│
├── output/                         # Output directory
├── logs/                           # Log files directory
└── predictions_*.json              # Prediction results (in root)
```

## Additional Resources

- **Quick Start Guide**: See [QUICKSTART.md](QUICKSTART.md) for a step-by-step setup guide
- **Database Schema**: See [docs/database_schema_design.md](docs/database_schema_design.md) for detailed schema documentation
- **ERD Generation**: Use `erd/generate_erd.py` to generate the ERD diagram
- **dbdiagram.io**: Use `erd/dbdiagram_erd.dbml` at https://dbdiagram.io to view the ERD online

## License

This project is part of the ALU ML Pipeline course assignments.

## Acknowledgements

- Dataset: [Hotel Booking Demand Dataset](https://www.kaggle.com/datasets/jessemostipak/hotel-booking-demand) from Kaggle
- FastAPI: https://fastapi.tiangolo.com/
- scikit-learn: https://scikit-learn.org/

## Contact

For questions or issues, please contact the team or open an issue in the repository.
