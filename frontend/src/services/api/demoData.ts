import { ModelListResponse } from './models';
import { Incident } from './incidents';
import { Deployment } from './deployments';
import { OverviewMetrics } from './analytics';
import { ReliabilityTrendsResponse } from './engineering_intelligence';

export const DEMO_MODELS: ModelListResponse = {
  items: [
    {
      name: "Spam Classifier V2",
      slug: "spam-classifier-v2",
      description: "Production transformer model classifying incoming email and message spam",
      framework: "huggingface",
      task_type: "classification",
      primary_metric: "f1_score",
      status: "UNHEALTHY",
      environment: "production",
      repository_id: "e669fb0d-211a-401e-ae89-e319a8467e5a",
      id: "76977adf-cd41-4680-a4a6-01739b00a4ba",
      created_at: "2026-10-10T20:48:45.725579",
      updated_at: "2026-10-10T20:48:45.725580"
    },
    {
      name: "Demand Forecast V1",
      slug: "demand-forecast-v1",
      description: "Hourly inventory demand predictor with temporal features",
      framework: "pytorch",
      task_type: "regression",
      primary_metric: "rmse",
      status: "AT_RISK",
      environment: "production",
      id: "c954bfcd-7b90-468d-9cbd-46082c7e0aee",
      created_at: "2026-10-10T20:48:45.725574",
      updated_at: "2026-10-10T20:48:45.725575"
    },
    {
      name: "Fraud Detection V3",
      slug: "fraud-detection-v3",
      description: "Real-time payment transaction risk scorer",
      framework: "lightgbm",
      task_type: "classification",
      primary_metric: "roc_auc",
      status: "HEALTHY",
      environment: "production",
      repository_id: "8a1624a1-2752-4d6c-926b-55dc4faaaa35",
      id: "edb731c4-f6eb-4be6-9e34-196911a22609",
      created_at: "2026-10-10T20:48:45.725569",
      updated_at: "2026-10-10T20:48:45.725570"
    },
    {
      name: "Customer Churn V2",
      slug: "customer-churn-v2",
      description: "Monthly customer retention risk prediction",
      framework: "xgboost",
      task_type: "classification",
      primary_metric: "accuracy",
      status: "HEALTHY",
      environment: "production",
      id: "06761286-4f44-4bce-9b9b-0d5b877d9869",
      created_at: "2026-10-10T20:48:45.725552",
      updated_at: "2026-10-10T20:48:45.725559"
    },
    {
      name: "Fraud Detection",
      slug: "fraud-detection",
      description: "Staging pipeline testing next-gen anomaly filters",
      framework: "tensorflow",
      task_type: "anomaly_detection",
      primary_metric: "f1_score",
      status: "draft",
      environment: "staging",
      id: "18c38efc-a073-4d21-b65c-27651787b919",
      created_at: "2026-10-09T20:07:30.948353",
      updated_at: "2026-10-09T20:07:30.948360"
    }
  ],
  total: 5,
  page: 1,
  limit: 20
};

export const DEMO_INCIDENTS: Incident[] = [
  {
    incident_key: "INC-647ff65c",
    model_id: "76977adf-cd41-4680-a4a6-01739b00a4ba",
    model_version_id: "5ce3c10e-0f36-45f0-9711-32fd0c603951",
    title: "Sudden F1 drop in Spam Classifier",
    summary: "Significant performance degradation detected following new spam campaign format",
    severity: "critical",
    status: "active",
    category: "performance_degradation",
    detected_at: "2026-10-08T17:48:45.560121",
    last_seen_at: "2026-10-10T20:48:45.944454",
    created_at: "2026-10-08T17:48:45.560121",
    updated_at: "2026-10-11T05:26:19.819135",
    id: "c68995ea-3fe6-4e7f-93d9-8433a5c23f8f"
  },
  {
    incident_key: "INC-8ee01349",
    model_id: "c954bfcd-7b90-468d-9cbd-46082c7e0aee",
    model_version_id: "72cce0f0-ea67-4281-bdd5-fd5731e63a16",
    title: "Spike in RMSE due to holiday season mismatch",
    summary: "Seasonal holiday volume caused high prediction error",
    severity: "high",
    status: "investigating",
    category: "performance_degradation",
    detected_at: "2026-10-09T19:48:45.560121",
    last_seen_at: "2026-10-10T20:48:45.934949",
    created_at: "2026-10-09T19:48:45.560121",
    updated_at: "2026-10-10T21:02:40.807888",
    id: "f06bfc3e-a44f-4658-89a0-98aafb5fd813"
  },
  {
    incident_key: "INC-f5f0c471",
    model_id: "edb731c4-f6eb-4be6-9e34-196911a22609",
    model_version_id: "d40ee3c0-2269-4203-b2de-281f3ebfe69e",
    title: "Concept Drift in EMEA Region",
    summary: "Distribution divergence detected on localized transaction features",
    severity: "medium",
    status: "resolved",
    category: "data_drift",
    detected_at: "2026-10-01T20:48:45.560121",
    last_seen_at: "2026-10-10T20:48:45.935100",
    resolved_at: "2026-10-04T12:00:00.000000",
    created_at: "2026-10-01T20:48:45.560121",
    updated_at: "2026-10-04T12:00:00.000000",
    id: "35d64821-4f1b-4fc6-b7fa-a38fbe886a11"
  },
  {
    incident_key: "INC-0b7d07cf",
    model_id: "06761286-4f44-4bce-9b9b-0d5b877d9869",
    model_version_id: "110534b1-7df6-44a7-8f4d-d8a79d2cfd6c",
    title: "Minor latency spike",
    summary: "P99 latency briefly exceeded 120ms during peak batch inference",
    severity: "low",
    status: "resolved",
    category: "service_health",
    detected_at: "2026-09-25T20:48:45.560121",
    last_seen_at: "2026-10-10T20:48:46.000982",
    created_at: "2026-09-25T20:48:45.560121",
    updated_at: "2026-10-10T20:48:46.000985",
    id: "9db6a7f5-5ff7-4b93-abe9-41f83929ee85"
  }
];

export const DEMO_OVERVIEW: OverviewMetrics = {
  reliability_score: 91,
  score_contributors: {
    "Incident Frequency": -4,
    "Critical Incidents": -5,
    "Deployment Stability": 0,
    "MTTR": 0,
    "Regression Stability": 0
  },
  total_incidents: 4,
  open_incidents: 2,
  resolved_incidents: 2,
  critical_incidents: 1,
  mttd_minutes: 4.2,
  mttr_minutes: 18.5,
  deployment_degradation_rate: 0.0,
  regression_coverage: 94.2
};

export const DEMO_TRENDS: ReliabilityTrendsResponse = {
  trends: [
    { timestamp: "2026-10-05T00:00:00Z", incidents: 0, reliability_score: 100 },
    { timestamp: "2026-10-06T00:00:00Z", incidents: 0, reliability_score: 100 },
    { timestamp: "2026-10-07T00:00:00Z", incidents: 0, reliability_score: 98 },
    { timestamp: "2026-10-08T00:00:00Z", incidents: 1, reliability_score: 85 },
    { timestamp: "2026-10-09T00:00:00Z", incidents: 1, reliability_score: 88 },
    { timestamp: "2026-10-10T00:00:00Z", incidents: 0, reliability_score: 91 },
    { timestamp: "2026-10-11T00:00:00Z", incidents: 0, reliability_score: 91 }
  ],
  direction: "RECOVERING",
  data_sufficiency: "SUFFICIENT"
};

export const DEMO_DEPLOYMENTS: Deployment[] = [
  {
    id: "617f2ceb-ef8d-4e93-be28-51d5f6dc814a",
    pull_request_id: "e896b81f-e3ce-46d0-94e2-123140083baa",
    incident_id: "c68995ea-3fe6-4e7f-93d9-8433a5c23f8f",
    commit_sha: "abc1234",
    status: "HEALTHY",
    gate_result: {
      patch_approved: true,
      validation_passed: true,
      regression_passed: true,
      security_passed: true,
      ci_passed: true,
      human_approved: true
    },
    deployed_at: "2026-10-09T19:48:45.560121",
    environment: "production",
    created_at: "2026-10-10T20:48:45.988255"
  },
  {
    id: "e2c2f077-27ca-4a28-a730-8d03d970d891",
    pull_request_id: "d9f72321-2755-481f-be58-763026b1a08e",
    incident_id: "1e4e1b15-5596-44c4-8bee-c56e026c9665",
    commit_sha: "aaa",
    status: "DEPLOYED",
    gate_result: {
      patch_approved: true,
      validation_passed: true,
      regression_passed: true,
      security_passed: true,
      ci_passed: true,
      human_approved: true
    },

    deployed_at: "2026-09-18T20:48:45.560121",
    environment: "production",
    created_at: "2026-10-10T20:48:45.920944"
  }
];
