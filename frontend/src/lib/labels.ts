export const ACTION_LABELS: Record<string, string> = {
  retry_payment: 'Retry Payment',
  wait_and_retry: 'Wait and Retry',
  request_payment_update: 'Payment Update',
};

export function actionLabel(action: string): string {
  return ACTION_LABELS[action] ?? action.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
}

export type AuditSeverity = 'critical' | 'warning' | 'info' | 'success' | 'neutral';

const EVENT_SEVERITY: Record<string, AuditSeverity> = {
  risk_detected: 'critical',
  root_cause_identified: 'warning',
  recovery_decision: 'info',
  guardrail_evaluated: 'info',
  action_executed: 'success',
  workflow_stopped: 'critical',
  recovery_case_detected: 'critical',
  policy_evaluation: 'warning',
  recovery_result: 'success',
};

const EVENT_LABELS: Record<string, string> = {
  risk_detected: 'Risk Detected',
  root_cause_identified: 'Root Cause Identified',
  recovery_decision: 'Recovery Decision',
  guardrail_evaluated: 'Guardrail Evaluated',
  action_executed: 'Action Executed',
  workflow_stopped: 'Workflow Stopped',
  recovery_case_detected: 'Recovery Case Detected',
  policy_evaluation: 'Policy Evaluation',
  recovery_result: 'Recovery Result',
};

export function eventSeverity(eventType: string): AuditSeverity {
  return EVENT_SEVERITY[eventType] ?? 'neutral';
}

export function eventLabel(eventType: string): string {
  return EVENT_LABELS[eventType] ?? eventType.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
}
