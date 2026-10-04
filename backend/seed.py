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
    print("Seeding complete.")
    db.close()

if __name__ == "__main__":
    seed()
