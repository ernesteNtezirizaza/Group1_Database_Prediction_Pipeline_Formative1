"""
Train ML Model for Hotel Booking Cancellation Prediction
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
import joblib
import warnings
warnings.filterwarnings('ignore')


def load_and_prepare_data(csv_file: str):
    """
    Load data from CSV and prepare features
    """
    print(f"Loading data from {csv_file}...")
    df = pd.read_csv(csv_file)
    
    print(f"Loaded {len(df)} records")
    
    # Handle missing values
    df = df.fillna(0)
    
    # Select features for prediction
    feature_columns = [
        'lead_time',
        'arrival_date_year',
        'stays_in_weekend_nights',
        'stays_in_week_nights',
        'adults',
        'children',
        'babies',
        'previous_cancellations',
        'previous_bookings_not_canceled',
        'booking_changes',
        'days_in_waiting_list',
        'adr',
        'required_car_parking_spaces',
        'total_of_special_requests'
    ]
    
    # Encode categorical features
    le_meal = LabelEncoder()
    df['meal_encoded'] = le_meal.fit_transform(df['meal'].astype(str))
    
    le_deposit = LabelEncoder()
    df['deposit_encoded'] = le_deposit.fit_transform(df['deposit_type'].astype(str))
    
    # Add encoded features
    feature_columns.extend(['meal_encoded', 'deposit_encoded'])
    
    # Prepare X and y
    X = df[feature_columns].values
    y = df['is_canceled'].values
    
    # Handle any remaining NaN or inf values
    X = np.nan_to_num(X, nan=0.0, posinf=0.0, neginf=0.0)
    
    print(f"Feature matrix shape: {X.shape}")
    print(f"Target distribution: {np.bincount(y.astype(int))}")
    
    return X, y, le_meal, le_deposit


def train_model(X, y, test_size=0.2, random_state=42):
    """
    Train Random Forest model
    """
    print(f"\nSplitting data: {test_size*100:.0f}% test, {(1-test_size)*100:.0f}% train")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )
    
    print(f"Training samples: {len(X_train)}")
    print(f"Test samples: {len(X_test)}")
    
    # Create pipeline with scaling and classifier
    pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('classifier', RandomForestClassifier(
            n_estimators=100,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=random_state,
            n_jobs=-1
        ))
    ])
    
    print("\nTraining model...")
    pipeline.fit(X_train, y_train)
    
    # Evaluate on test set
    train_score = pipeline.score(X_train, y_train)
    test_score = pipeline.score(X_test, y_test)
    
    print(f"\nModel Performance:")
    print(f"  Training accuracy: {train_score:.4f} ({train_score*100:.2f}%)")
    print(f"  Test accuracy: {test_score:.4f} ({test_score*100:.2f}%)")
    
    # Cross-validation
    print("\nPerforming 5-fold cross-validation...")
    cv_scores = cross_val_score(pipeline, X_train, y_train, cv=5)
    print(f"  CV accuracy: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
    
    # Feature importance
    feature_names = [
        'lead_time', 'arrival_date_year', 'stays_in_weekend_nights',
        'stays_in_week_nights', 'adults', 'children', 'babies',
        'previous_cancellations', 'previous_bookings_not_canceled',
        'booking_changes', 'days_in_waiting_list', 'adr',
        'required_car_parking_spaces', 'total_of_special_requests',
        'meal_encoded', 'deposit_encoded'
    ]
    
    importances = pipeline.named_steps['classifier'].feature_importances_
    feature_importance = list(zip(feature_names, importances))
    feature_importance.sort(key=lambda x: x[1], reverse=True)
    
    print("\nTop 5 Most Important Features:")
    for feature, importance in feature_importance[:5]:
        print(f"  {feature}: {importance:.4f}")
    
    return pipeline, X_test, y_test


def main():
    """
    Main training function
    """
    print("=" * 60)
    print("Hotel Booking Cancellation Prediction - Model Training")
    print("=" * 60)
    
    # Load and prepare data
    X, y, le_meal, le_deposit = load_and_prepare_data('hotel_bookings.csv')
    
    # Train model
    model, X_test, y_test = train_model(X, y)
    
    # Save model
    model_path = 'models/cancellation_model.pkl'
    joblib.dump(model, model_path)
    print(f"\nModel saved to {model_path}")
    
    # Save preprocessor separately (already included in pipeline)
    preprocessor_path = 'models/feature_preprocessor.pkl'
    joblib.dump(model.named_steps['scaler'], preprocessor_path)
    print(f"Preprocessor saved to {preprocessor_path}")
    
    # Save encoders
    joblib.dump(le_meal, 'models/meal_encoder.pkl')
    joblib.dump(le_deposit, 'models/deposit_encoder.pkl')
    print("Encoders saved")
    
    print("\nTraining completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
