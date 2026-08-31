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

export interface DashboardData {
  summary: DashboardSummary;
  cases: DashboardCases;
  recovery_by_action: RecoveryByAction[];
  payment_degradation: PaymentDegradation;
  recent_audit_events: AuditEvent[];
}
