# ModelSentinel Demo Guide

This guide walks you through the deterministic presentation flow for ModelSentinel.

## 1. Start the Environment
Run the demo start command from the project root:
```bash
./demo start
```
*Wait for the services to become ready.*

## 2. Seed the Demo Data
Once started, seed the database with the deterministic presentation data:
```bash
./demo seed
```

## 3. Login
Navigate to `http://localhost:5173` and log in. 
Use the credentials for the admin you created during bootstrap (`scripts/create_admin.py`).

## 4. Presentation Flow
Follow this guaranteed path to showcase the core value proposition:
1. **Dashboard**: Immediate overview of system health.
2. **Models**: View all monitored models.
3. **Spam Classifier V2**: Click into this hero model.
4. **Model Intelligence**: View the AI insights.
5. **Incident**: Navigate to the active incident.
6. **Investigation**: See the investigation details.
7. **Repository**: Check the source repository.
8. **Change Intelligence**: View the change analysis.
9. **Change Risk**: Review the risk assessment.
10. **Patch**: Look at the generated patch.
11. **Validation**: Check validation results.
12. **Regression**: Review regression analysis.
13. **PR**: See the Pull Request.
14. **Deployment**: View deployment status.
15. **Verification**: Check verification steps.
16. **Incident Memory**: See similar past incidents.
17. **Reliability Timeline**: View the reliability graph.
18. **Engineering Intelligence**: Conclude the hero flow.

## 5. Add a New Model
After the main presentation, demonstrate adding a new model:
1. Click **Add Model**
2. Fill in the details for **Customer Churn V3**
3. Save and view the new model dashboard.

## 6. Reset Demo
To reset the environment back to the clean state without destroying the admin user:
```bash
./demo reset
```
