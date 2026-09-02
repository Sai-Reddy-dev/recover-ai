export interface DashboardSummary {
  revenue_at_risk: number;
  revenue_recovered: number;
  recovery_rate: number;
  recovered_subscriptions: number;
  recovered_cases: number;
}

export interface DashboardCases {
  active: number;
  failed: number;
  stopped: number;
}

export interface RecoveryByAction {
  action: string;
  recovered_cases: number;
  revenue_recovered: number;
}

export interface PaymentDegradation {
  degraded_methods: number;
  affected_subscriptions: number;
  revenue_at_risk: number;
}

export interface AuditEvent {
  event_type: string;
  actor: string;
  message: string;
  metadata: Record<string, unknown>;
  created_at: string;
}

export interface AIDecisionControl {
  recovery_case_id: string;
  revenue_at_risk: number;

  root_cause: string | null;
  confidence: number | null;
  risk_level: string | null;
  recommended_action: string | null;
  reason: string | null;

  guardrail_action: string | null;
  guardrail_approved: boolean | null;
  guardrail_reason: string | null;

  executed_action: string | null;
  execution_status: string | null;
  execution_result: string | null;
  attempt_number: number | null;
  executed_at: string | null;
}

export interface RecoveryCase {
  recovery_case_id: string;
  customer_name: string;
  customer_email: string;

  revenue_at_risk: number;
  status: string;
  priority: string;
  retry_count: number;

  opened_at: string | null;
  closed_at: string | null;

  failure_reason: string | null;
  decline_code: string | null;
  payment_method: string | null;

  root_cause: string | null;
  confidence: number | null;
  recommended_action: string | null;
}

export interface AIRecommendationDistribution {
  action: string;
  decision_count: number;
}

export interface DashboardData {
  summary: DashboardSummary;
  cases: DashboardCases;
  recovery_by_action: RecoveryByAction[];
  payment_degradation: PaymentDegradation;
  recent_audit_events: AuditEvent[];
  ai_decision_control: AIDecisionControl[];
  recovery_cases: RecoveryCase[];
  ai_recommendation_distribution: AIRecommendationDistribution[];
}