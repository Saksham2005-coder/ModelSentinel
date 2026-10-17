import { ModelListResponse } from './models';
import { Incident } from './incidents';
import { Deployment } from './deployments';
import { OverviewMetrics } from './analytics';
import { ReliabilityTrendsResponse } from './engineering_intelligence';
import { WorkflowRun } from './workflows';

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
      repository_id: "410e2e44-97a4-4a32-8594-2ff8fe130e46",
      id: "4872c9f0-b895-4d27-8547-28113a3bb876",
      created_at: "2026-10-15T15:45:35.893526Z",
      updated_at: "2026-10-17T15:45:35.893526Z"
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
      id: "7d6bafb3-a892-49ee-b09f-50bc5f653314",
      created_at: "2026-10-02T15:45:35.893526Z",
      updated_at: "2026-10-16T15:45:35.893526Z"
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
      repository_id: "7ea41179-9c35-47d0-8ad9-4182317e83a2",
      id: "33a3a20d-9e42-4cb6-b288-89ae9fdc430c",
      created_at: "2026-09-07T15:45:35.893526Z",
      updated_at: "2026-10-15T15:45:35.893526Z"
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
      id: "571ffbe0-8966-4ce0-979a-cd3dac1d3868",
      created_at: "2026-09-27T15:45:35.893526Z",
      updated_at: "2026-10-17T15:45:35.893526Z"
    }
  ],
  total: 4,
  page: 1,
  limit: 20
};

export const DEMO_INCIDENTS: Incident[] = [
  {
    incident_key: "INC-90ac1c82",
    model_id: "4872c9f0-b895-4d27-8547-28113a3bb876",
    model_version_id: "5273f69d-5d71-4edb-bc5e-b98b0e5f0b81",
    title: "Sudden F1 drop in Spam Classifier",
    summary: "Significant performance degradation detected following new spam campaign format",
    severity: "critical",
    status: "investigating",
    category: "performance_degradation",
    detected_at: "2026-10-15T12:45:35.893526Z",
    last_seen_at: "2026-10-17T15:45:35.893526Z",
    created_at: "2026-10-15T12:45:35.893526Z",
    updated_at: "2026-10-17T15:45:35.893526Z",
    id: "2ffa080c-1678-4325-9d1c-d59f22e04b52"
  },
  {
    incident_key: "INC-0d325c23",
    model_id: "7d6bafb3-a892-49ee-b09f-50bc5f653314",
    model_version_id: "72cce0f0-ea67-4281-bdd5-fd5731e63a16",
    title: "Spike in RMSE due to holiday season mismatch",
    summary: "Seasonal holiday volume caused high prediction error",
    severity: "high",
    status: "active",
    category: "performance_degradation",
    detected_at: "2026-10-16T14:45:35.893526Z",
    last_seen_at: "2026-10-17T15:45:35.893526Z",
    created_at: "2026-10-16T14:45:35.893526Z",
    updated_at: "2026-10-17T15:45:35.893526Z",
    id: "c8ed56fb-7e15-4fb3-9957-7c01c5520d69"
  },
  {
    incident_key: "INC-fb5ffe34",
    model_id: "33a3a20d-9e42-4cb6-b288-89ae9fdc430c",
    model_version_id: "d40ee3c0-2269-4203-b2de-281f3ebfe69e",
    title: "Concept Drift in EMEA Region",
    summary: "Distribution divergence detected on localized transaction features",
    severity: "medium",
    status: "resolved",
    category: "data_drift",
    detected_at: "2026-09-22T15:45:35.893526Z",
    last_seen_at: "2026-10-17T15:45:35.893526Z",
    resolved_at: "2026-09-25T15:45:35.893526Z",
    created_at: "2026-09-22T15:45:35.893526Z",
    updated_at: "2026-09-25T15:45:35.893526Z",
    id: "3493c0d2-281d-48f3-8983-06901606ebcc"
  },
  {
    incident_key: "INC-36fbc2c7",
    model_id: "571ffbe0-8966-4ce0-979a-cd3dac1d3868",
    model_version_id: "110534b1-7df6-44a7-8f4d-d8a79d2cfd6c",
    title: "Minor latency spike",
    summary: "P99 latency briefly exceeded 120ms during peak batch inference",
    severity: "low",
    status: "resolved",
    category: "service_health",
    detected_at: "2026-10-02T15:45:35.893526Z",
    last_seen_at: "2026-10-17T15:45:35.893526Z",
    created_at: "2026-10-02T15:45:35.893526Z",
    updated_at: "2026-10-03T15:45:35.893526Z",
    id: "f05bac73-bde9-419a-8648-764c638ab87b"
  },
  {
    incident_key: "INC-5a8b9a71",
    model_id: "4872c9f0-b895-4d27-8547-28113a3bb876",
    model_version_id: "68bd88e0-f006-4580-ba29-91ebd12ce835",
    title: "Old version memory leak",
    summary: "Gradual memory leak observed in v2.0 inference workers",
    severity: "medium",
    status: "resolved",
    category: "service_health",
    detected_at: "2026-08-28T15:45:35.893526Z",
    last_seen_at: "2026-10-17T15:45:35.893526Z",
    created_at: "2026-08-28T15:45:35.893526Z",
    updated_at: "2026-08-30T15:45:35.893526Z",
    id: "b14d828b-908f-4a8c-907c-f86334b60a53"
  }
];

export const DEMO_OVERVIEW: OverviewMetrics = {
  reliability_score: 92,
  score_contributors: {
    "Incident Frequency": -3,
    "Critical Incidents": -5,
    "Deployment Stability": 0,
    "MTTR": 0,
    "Regression Stability": 0
  },
  total_incidents: 5,
  open_incidents: 2,
  resolved_incidents: 3,
  critical_incidents: 1,
  mttd_minutes: 3.8,
  mttr_minutes: 16.2,
  deployment_degradation_rate: 0.0,
  regression_coverage: 96.5
};

export const DEMO_TRENDS: ReliabilityTrendsResponse = {
  trends: [
    { timestamp: "2026-10-11T00:00:00Z", incidents: 0, reliability_score: 98 },
    { timestamp: "2026-10-12T00:00:00Z", incidents: 0, reliability_score: 98 },
    { timestamp: "2026-10-13T00:00:00Z", incidents: 0, reliability_score: 96 },
    { timestamp: "2026-10-14T00:00:00Z", incidents: 0, reliability_score: 95 },
    { timestamp: "2026-10-15T00:00:00Z", incidents: 1, reliability_score: 84 },
    { timestamp: "2026-10-16T00:00:00Z", incidents: 1, reliability_score: 89 },
    { timestamp: "2026-10-17T00:00:00Z", incidents: 0, reliability_score: 92 }
  ],
  direction: "RECOVERING",
  data_sufficiency: "SUFFICIENT"
};

export const DEMO_DEPLOYMENTS: Deployment[] = [
  {
    id: "286a018e-a463-4ab4-99ba-270bbaeca41a",
    pull_request_id: "d8965861-83b5-4e50-9632-684d2772a290",
    incident_id: "2ffa080c-1678-4325-9d1c-d59f22e04b52",
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
    deployed_at: "2026-10-16T14:45:35.893526Z",
    environment: "production",
    created_at: "2026-10-16T14:45:35.893526Z"
  },
  {
    id: "e2c2f077-27ca-4a28-a730-8d03d970d891",
    pull_request_id: "0eca4d19-24ff-4c32-a16f-1d17dff9896d",
    incident_id: "3493c0d2-281d-48f3-8983-06901606ebcc",
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
    deployed_at: "2026-09-24T15:45:35.893526Z",
    environment: "production",
    created_at: "2026-09-24T15:45:35.893526Z"
  }
];

export const DEMO_WORKFLOWS: WorkflowRun[] = [
  {
    id: "wf-b5881bc1",
    name: "Patch Review Flow",
    workflow_type: "patch_review",
    description: "Standard remediation code review and regression gating pipeline",
    status: "COMPLETED",
    entity_type: "patch_proposal",
    entity_id: "85381e43-2673-4e32-b9e4-14927429b157",
    started_at: "2026-10-16T07:45:35.893526Z",
    completed_at: "2026-10-16T08:45:35.893526Z",
    created_at: "2026-10-16T07:45:35.893526Z",
    steps: []
  },
  {
    id: "wf-98fefd59",
    name: "Deployment Gate",
    workflow_type: "deployment_gate",
    description: "Canary rollout policy and automated rollback watchdog",
    status: "COMPLETED",
    entity_type: "pull_request",
    entity_id: "0eca4d19-24ff-4c32-a16f-1d17dff9896d",
    started_at: "2026-09-24T14:45:35.893526Z",
    completed_at: "2026-09-24T15:45:35.893526Z",
    created_at: "2026-09-24T14:45:35.893526Z",
    steps: []
  },
  {
    id: "wf-1f1600e7",
    name: "Incident Triage",
    workflow_type: "incident_triage",
    description: "Root cause clustering and historical resolution memory matching",
    status: "RUNNING",
    entity_type: "incident",
    entity_id: "c8ed56fb-7e15-4fb3-9957-7c01c5520d69",
    started_at: "2026-10-16T14:45:35.893526Z",
    completed_at: null,
    created_at: "2026-10-16T14:45:35.893526Z",
    steps: []
  }
];

export const DEMO_REPOSITORIES = [
  {
    id: "410e2e44-97a4-4a32-8594-2ff8fe130e46",
    name: "ml-serving-platform",
    status: "ready",
    source_type: "public_git",
    current_commit: "abc1234",
    indexed_at: "2026-10-07T15:45:35.893526Z"
  },
  {
    id: "7ea41179-9c35-47d0-8ad9-4182317e83a2",
    name: "fraud-prediction-service",
    status: "ready",
    source_type: "public_git",
    current_commit: "f5e6d7c8",
    indexed_at: "2026-10-07T15:45:35.893526Z"
  }
];

export const DEMO_REGRESSION_TESTS = [
  {
    id: "6849803c-f8d1-4424-85a4-395857f94a34",
    name: "Emoji parsing regression suite",
    source_incident_id: "2ffa080c-1678-4325-9d1c-d59f22e04b52",
    root_cause: "Unicode 15 emoji parsing logic exception in text_features.py",
    severity: "high",
    status: "active",
    last_run: "passed",
    last_run_time: "2026-10-16T09:45:35.893526Z"
  },
  {
    id: "c8fa5896-73fa-447c-a83c-4ce55375572e",
    name: "Length constraint suite",
    source_incident_id: "2ffa080c-1678-4325-9d1c-d59f22e04b52",
    root_cause: "Exceeded max length truncation edge-case",
    severity: "medium",
    status: "active",
    last_run: "passed",
    last_run_time: "2026-10-16T09:45:35.893526Z"
  },
  {
    id: "ff23e9ea-dd80-4a76-b4dc-e6fca9a80968",
    name: "Null handling suite",
    source_incident_id: "3493c0d2-281d-48f3-8983-06901606ebcc",
    root_cause: "Null imputation in categorical preprocessing",
    severity: "high",
    status: "active",
    last_run: "passed",
    last_run_time: "2026-10-07T15:45:35.893526Z"
  }
];

export const DEMO_INTEGRATIONS = [
  {
    id: "int-github-001",
    provider: "github",
    name: "GitHub Enterprise",
    type: "repository",
    status: "CONNECTED",
    updated_at: "2026-10-17T15:45:35.893526Z"
  },
  {
    id: "int-pagerduty-002",
    provider: "pagerduty",
    name: "PagerDuty Incident Sync",
    type: "alerting",
    status: "CONNECTED",
    updated_at: "2026-10-17T15:45:35.893526Z"
  },
  {
    id: "int-slack-003",
    provider: "slack",
    name: "Slack War-Room Channel",
    type: "notification",
    status: "CONNECTED",
    updated_at: "2026-10-17T15:45:35.893526Z"
  }
];

export const DEMO_WEBHOOKS = [
  {
    id: "wh-gh-9912",
    provider: "github",
    event_type: "pull_request.opened",
    processing_status: "PROCESSED",
    delivery_id: "del-8921fa09-2311",
    received_at: "2026-10-17T14:22:10Z"
  },
  {
    id: "wh-gh-9913",
    provider: "github",
    event_type: "push",
    processing_status: "PROCESSED",
    delivery_id: "del-3881ca12-9011",
    received_at: "2026-10-17T13:45:00Z"
  },
  {
    id: "wh-pd-9914",
    provider: "pagerduty",
    event_type: "incident.acknowledged",
    processing_status: "PROCESSED",
    delivery_id: "del-10023ee-4491",
    received_at: "2026-10-17T11:10:05Z"
  }
];

export const DEMO_MEMORIES = [
  {
    id: "mem-001",
    incident_id: "2ffa080c-1678-4325-9d1c-d59f22e04b52",
    title: "Spam Classifier Unicode Exception in Tokenizer",
    root_cause: "Unicode 15 emoji and non-standard UTF-8 symbols caused uncaught exceptions in custom tokenizer pipeline.",
    root_cause_category: "Data Preprocessing",
    model_id: "4872c9f0-b895-4d27-8547-28113a3bb876",
    affected_segments: ["emoji_heavy", "mobile_traffic"],
    resolution_summary: "Replaced regex tokenizer with robust byte-level fallback and added defensive sanitization filter.",
    created_at: "2026-10-15T16:20:00Z",
    resolution: {
      effectiveness_score: 96,
      validation_status: "PASSED",
      deployment_status: "COMPLETED",
      post_deployment_status: "STABLE"
    }
  },
  {
    id: "mem-002",
    incident_id: "c8ed56fb-7e15-4fb3-9957-7c01c5520d69",
    title: "Seasonal Holiday Surge Distribution Shift",
    root_cause: "Holiday traffic surge shifted demand features outside 3-sigma training bounds.",
    root_cause_category: "Covariate Shift",
    model_id: "7d6bafb3-a892-49ee-b09f-50bc5f653314",
    affected_segments: ["holiday_promotions", "flash_deals"],
    resolution_summary: "Activated dynamic feature clipping and fallback exponential smoothing during sudden traffic spikes.",
    created_at: "2026-10-16T18:00:00Z",
    resolution: {
      effectiveness_score: 92,
      validation_status: "PASSED",
      deployment_status: "COMPLETED",
      post_deployment_status: "STABLE"
    }
  },
  {
    id: "mem-003",
    incident_id: "3493c0d2-281d-48f3-8983-06901606ebcc",
    title: "Fraud Scorer Missing Category Value Null Pointer",
    root_cause: "New merchant categorical value introduced without imputation map entry.",
    root_cause_category: "Schema Incompatibility",
    model_id: "33a3a20d-9e42-4cb6-b288-89ae9fdc430c",
    affected_segments: ["new_merchants"],
    resolution_summary: "Introduced unmapped category bucket `__UNKNOWN__` with risk prior estimation.",
    created_at: "2026-10-08T10:15:00Z",
    resolution: {
      effectiveness_score: 99,
      validation_status: "PASSED",
      deployment_status: "COMPLETED",
      post_deployment_status: "STABLE"
    }
  }
];

export const DEMO_CHANGE_RISK_ASSESSMENTS = [
  {
    id: "cra-001",
    patch_proposal_id: "patch-tokenizer-fallback-v1",
    risk_score: 24,
    risk_level: "LOW",
    created_at: "2026-10-17T14:30:00Z",
    factors: [
      { factor: "Preserves existing API contract", contribution: 5 },
      { factor: "Coverage across edge case test suite", contribution: 12 },
      { factor: "Single module isolation", contribution: 7 }
    ],
    blast_radius: {
      files: ["backend/ml/tokenizers.py", "tests/test_tokenizers.py"],
      models: ["Spam Classifier V2"],
      features: ["raw_text_tokens", "char_length"],
      regression_tests: ["Emoji parsing regression suite"],
      historical_incidents: ["INC-90ac1c82"]
    },
    recommended_regressions: ["6849803c-f8d1-4424-85a4-395857f94a34"]
  },
  {
    id: "cra-002",
    patch_proposal_id: "patch-dynamic-clipping-v2",
    risk_score: 48,
    risk_level: "MODERATE",
    created_at: "2026-10-17T12:15:00Z",
    factors: [
      { factor: "Modifies feature transformation threshold", contribution: 25 },
      { factor: "Affects high-throughput prediction path", contribution: 15 },
      { factor: "Automated regression tests verified", contribution: 8 }
    ],
    blast_radius: {
      files: ["backend/ml/features.py"],
      models: ["Demand Forecast V1"],
      features: ["hourly_demand", "promo_multiplier"],
      regression_tests: ["Length constraint suite"],
      historical_incidents: ["INC-0d325c23"]
    },
    recommended_regressions: ["c8fa5896-73fa-447c-a83c-4ce55375572e"]
  }
];
