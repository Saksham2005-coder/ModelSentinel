from app.db.session import SessionLocal
from app.models.model import Model, ModelVersion, ModelMetric
from app.schemas.model import ModelCreate, ModelVersionCreate
from app.services import model_service
import random
from datetime import datetime, timedelta, timezone

def seed():
    print("Seeding database...")
    db = SessionLocal()

    # Clear existing
    db.query(ModelMetric).delete()
    db.query(ModelVersion).delete()
    db.query(Model).delete()
    db.commit()

    # 1. Email Spam Classifier
    m1 = model_service.create_model(db, ModelCreate(
        name="Email Spam Classifier",
        slug="email-spam-classifier",
        description="Classifies incoming emails as spam or ham based on content.",
        framework="scikit-learn",
        task_type="classification",
        problem_type="binary_classification",
        primary_metric="f1_score",
        owner="ml-core-team",
        environment="production",
        status="active"
    ))
    
    # 2. Customer Churn Prediction
    m2 = model_service.create_model(db, ModelCreate(
        name="Customer Churn Prediction",
        slug="customer-churn-prediction",
        description="Predicts likelihood of a customer canceling their subscription within 30 days.",
        framework="xgboost",
        task_type="classification",
        problem_type="binary_classification",
        primary_metric="roc_auc",
        owner="retention-squad",
        environment="production",
        status="warning"
    ))

    # 3. Fraud Detection
    m3 = model_service.create_model(db, ModelCreate(
        name="Fraud Detection",
        slug="fraud-detection",
        description="Real-time transaction fraud detection.",
        framework="pytorch",
        task_type="anomaly_detection",
        problem_type="anomaly",
        primary_metric="precision",
        owner="risk-team",
        environment="staging",
        status="degraded"
    ))

    # 4. Sales Forecasting
    m4 = model_service.create_model(db, ModelCreate(
        name="Sales Forecasting",
        slug="sales-forecasting",
        description="Predicts weekly sales volume by region.",
        framework="pytorch",
        task_type="forecasting",
        problem_type="time_series",
        primary_metric="mape",
        owner="finance-ml",
        environment="development",
        status="active"
    ))

    # Create versions
    v1 = model_service.create_model_version(db, m1.id, ModelVersionCreate(
        version="1.0.0",
        description="Initial production release",
        framework_version="1.2.2",
        python_version="3.9",
        is_active=False
    ))
    v2 = model_service.create_model_version(db, m1.id, ModelVersionCreate(
        version="1.1.0",
        description="Added TF-IDF features",
        framework_version="1.2.2",
        python_version="3.9",
        is_active=True
    ))

    # Seed some metrics
    now = datetime.now(timezone.utc)
    for i in range(10):
        recorded_at = now - timedelta(days=9-i)
        
        # Spam classifier metrics (steady)
        metric = ModelMetric(
            model_version_id=v2.id,
            metric_name="f1_score",
            metric_value=0.92 + random.uniform(-0.01, 0.01),
            dataset_name="production",
            evaluation_type="online",
            recorded_at=recorded_at
        )
        db.add(metric)

    db.commit()
    
    # Generate deterministic dataset for Email Spam Classifier
    print("Generating demo CSV datasets...")
    import pandas as pd
    import numpy as np
    import os
    
    np.random.seed(42)
    n_samples = 1000
    
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    # Baseline
    b_target = np.random.choice([0, 1], p=[0.78, 0.22], size=n_samples)
    b_url_length = np.where(b_target == 1, np.random.normal(45, 10, n_samples), np.random.normal(25, 5, n_samples))
    b_url_count = np.where(b_target == 1, np.random.poisson(4, n_samples), np.random.poisson(1, n_samples))
    b_sender_domain = np.random.choice(['gmail.com', 'yahoo.com', 'corporate.com', 'unknown.io'], p=[0.5, 0.2, 0.2, 0.1], size=n_samples)
    
    b_prob = np.where(b_target == 1, np.random.beta(8, 2, n_samples), np.random.beta(2, 8, n_samples))
    b_pred = (b_prob > 0.5).astype(int)
    
    b_df = pd.DataFrame({
        'target': b_target,
        'prediction': b_pred,
        'probability': b_prob,
        'url_length': b_url_length,
        'url_count': b_url_count,
        'sender_domain': b_sender_domain
    })
    
    # Current (Drifted)
    c_target = np.random.choice([0, 1], p=[0.61, 0.39], size=n_samples) # Shifted class balance
    c_url_length = np.where(c_target == 1, np.random.normal(60, 15, n_samples), np.random.normal(25, 5, n_samples)) # Drifted
    c_url_count = np.where(c_target == 1, np.random.poisson(7, n_samples), np.random.poisson(1, n_samples)) # Drifted
    c_sender_domain = np.random.choice(['gmail.com', 'yahoo.com', 'corporate.com', 'unknown.io'], p=[0.3, 0.1, 0.1, 0.5], size=n_samples) # Drifted categorical
    
    # Degraded predictions
    c_prob = np.where(c_target == 1, np.random.beta(5, 5, n_samples), np.random.beta(4, 6, n_samples))
    c_pred = (c_prob > 0.5).astype(int)
    
    # Introduce some missing values
    c_url_length[np.random.choice(n_samples, size=int(0.06 * n_samples), replace=False)] = np.nan
    
    c_df = pd.DataFrame({
        'target': c_target,
        'prediction': c_pred,
        'probability': c_prob,
        'url_length': c_url_length,
        'url_count': c_url_count,
        'sender_domain': c_sender_domain
    })
    
    b_df.to_csv(os.path.join(data_dir, f'{m1.slug}_baseline.csv'), index=False)
    c_df.to_csv(os.path.join(data_dir, f'{m1.slug}_current.csv'), index=False)

    print("Seeding complete.")
    db.close()

if __name__ == "__main__":
    seed()
