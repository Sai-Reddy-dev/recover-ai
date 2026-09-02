import {
  Brain,
  CheckCircle2,
  Clock3,
  XCircle,
  AlertTriangle,
  ShieldCheck,
  ShieldX,
} from 'lucide-react';
import type {
  AIDecisionControl as AIDecisionControlData,
} from '@/types/dashboard';

interface Props {
  data: AIDecisionControlData[];
}

function formatAction(action: string | null) {
  if (!action) return '—';

  return action
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

function formatRootCause(rootCause: string | null) {
  if (!rootCause) return 'Unknown';

  return rootCause
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

function formatCurrency(amount: number) {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(amount);
}

function getRiskClass(risk: string | null) {
  switch (risk?.toLowerCase()) {
    case 'high':
    case 'critical':
      return 'bg-red-50 text-red-700 ring-red-600/20';

    case 'medium':
      return 'bg-amber-50 text-amber-700 ring-amber-600/20';

    default:
      return 'bg-ink-50 text-ink-600 ring-ink-500/20';
  }
}

function getStatusIcon(status: string | null) {
  switch (status?.toLowerCase()) {
    case 'success':
      return <CheckCircle2 className="h-4 w-4" />;

    case 'failed':
      return <XCircle className="h-4 w-4" />;

    case 'pending':
      return <Clock3 className="h-4 w-4" />;

    default:
      return <AlertTriangle className="h-4 w-4" />;
  }
}

function getStatusClass(status: string | null) {
  switch (status?.toLowerCase()) {
    case 'success':
      return 'text-emerald-600';

    case 'failed':
      return 'text-red-600';

    case 'pending':
      return 'text-amber-600';

    default:
      return 'text-ink-500';
  }
}

function getGuardrailClass(approved: boolean | null) {
  if (approved === true) {
    return 'text-emerald-600';
  }

  if (approved === false) {
    return 'text-red-600';
  }

  return 'text-ink-500';
}

function getGuardrailIcon(approved: boolean | null) {
  if (approved === true) {
    return <ShieldCheck className="h-4 w-4" />;
  }

  if (approved === false) {
    return <ShieldX className="h-4 w-4" />;
  }

  return <AlertTriangle className="h-4 w-4" />;
}

export function AIDecisionControl({ data }: Props) {
  return (
    <section className="overflow-hidden rounded-2xl border border-ink-200 bg-white shadow-sm">
      {/* Section Header */}
      <div className="border-b border-ink-200 px-5 py-5 sm:px-6">
        <div className="flex items-start gap-3">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-indigo-50 text-indigo-600">
            <Brain className="h-5 w-5" />
          </div>

          <div>
            <h2 className="text-base font-semibold text-ink-900">
              AI Decision & Recovery Control
            </h2>

            <p className="mt-1 text-sm text-ink-500">
              AI recommendations, guardrail decisions, and execution outcomes.
            </p>
          </div>
        </div>
      </div>

      {/* Decision Rows */}
      <div className="divide-y divide-ink-100">
        {data.map((item) => (
          <div
            key={item.recovery_case_id}
            className="p-5 transition hover:bg-ink-50/50 sm:p-6"
          >
            <div className="grid grid-cols-1 gap-5 lg:grid-cols-12">
              {/* Revenue / Case */}
              <div className="lg:col-span-2">
                <p className="text-[11px] font-medium uppercase tracking-wider text-ink-400">
                  Revenue at Risk
                </p>

                <p className="mt-1 text-lg font-semibold text-ink-900">
                  {formatCurrency(item.revenue_at_risk)}
                </p>

                <p className="mt-1 break-all text-[10px] text-ink-400">
                  {item.recovery_case_id}
                </p>
              </div>

              {/* AI Analysis */}
              <div className="lg:col-span-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-[11px] font-medium uppercase tracking-wider text-ink-400">
                      Root Cause
                    </p>

                    <p className="mt-1 text-sm font-medium text-ink-800">
                      {formatRootCause(item.root_cause)}
                    </p>
                  </div>

                  <div>
                    <p className="text-[11px] font-medium uppercase tracking-wider text-ink-400">
                      Confidence
                    </p>

                    <p className="mt-1 text-sm font-semibold text-ink-800">
                      {item.confidence !== null
                        ? `${(item.confidence * 100).toFixed(1)}%`
                        : '—'}
                    </p>
                  </div>

                  <div>
                    <p className="text-[11px] font-medium uppercase tracking-wider text-ink-400">
                      Risk
                    </p>

                    <span
                      className={`mt-1 inline-flex rounded-full px-2 py-1 text-[11px] font-medium capitalize ring-1 ring-inset ${getRiskClass(
                        item.risk_level,
                      )}`}
                    >
                      {item.risk_level ?? 'Unknown'}
                    </span>
                  </div>

                  <div>
                    <p className="text-[11px] font-medium uppercase tracking-wider text-ink-400">
                      AI Recommendation
                    </p>

                    <p className="mt-1 text-sm font-semibold text-indigo-600">
                      {formatAction(item.recommended_action)}
                    </p>
                  </div>
                </div>

                {item.reason && (
                  <p className="mt-4 text-xs leading-5 text-ink-500">
                    {item.reason}
                  </p>
                )}
              </div>

              {/* Guardrail + Execution */}
              <div className="lg:col-span-4">
                <div className="grid grid-cols-1 gap-4">
                  {/* Guardrail */}
                  <div>
                    <p className="text-[11px] font-medium uppercase tracking-wider text-ink-400">
                      Guardrail
                    </p>

                    <div
                      className={`mt-1 flex items-center gap-1.5 text-sm font-semibold ${getGuardrailClass(
                        item.guardrail_approved,
                      )}`}
                    >
                      {getGuardrailIcon(item.guardrail_approved)}

                      <span>
                        {item.guardrail_approved === true
                          ? 'Approved'
                          : item.guardrail_approved === false
                            ? 'Blocked'
                            : 'Not Evaluated'}
                      </span>
                    </div>

                    {item.guardrail_action && (
                      <p className="mt-1 text-xs text-ink-600">
                        Action: {formatAction(item.guardrail_action)}
                      </p>
                    )}

                    {item.guardrail_reason && (
                      <p className="mt-2 text-xs leading-5 text-ink-500">
                        {item.guardrail_reason}
                      </p>
                    )}
                  </div>

                  {/* Execution */}
                  <div>
                    <p className="text-[11px] font-medium uppercase tracking-wider text-ink-400">
                      Execution
                    </p>

                    <p className="mt-1 text-sm font-medium text-ink-800">
                      {formatAction(item.executed_action)}
                    </p>

                    <div
                      className={`mt-1 flex items-center gap-1.5 text-sm font-semibold ${getStatusClass(
                        item.execution_status,
                      )}`}
                    >
                      {getStatusIcon(item.execution_status)}

                      <span>
                        {formatAction(item.execution_status)}
                      </span>
                    </div>

                    {item.execution_result && (
                      <p className="mt-2 text-xs text-ink-500">
                        {formatAction(item.execution_result)}
                      </p>
                    )}

                    {item.attempt_number !== null && (
                      <p className="mt-1 text-xs text-ink-400">
                        Attempt #{item.attempt_number}
                      </p>
                    )}
                  </div>
                </div>
              </div>

              {/* Control Indicator */}
              <div className="flex items-center justify-start lg:col-span-2 lg:justify-end">
                <div className="rounded-xl border border-ink-200 bg-ink-50 px-3 py-2">
                  <div className="flex items-center gap-2">
                    <div className="h-2 w-2 rounded-full bg-emerald-500" />

                    <span className="text-[11px] font-medium text-ink-600">
                      AI Decision
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}