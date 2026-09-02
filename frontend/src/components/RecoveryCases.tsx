import {
  AlertTriangle,
  CheckCircle2,
  Clock3,
  XCircle,
} from 'lucide-react';
import type { RecoveryCase } from '@/types/dashboard';

interface Props {
  data: RecoveryCase[];
}

function formatAction(action: string | null) {
  if (!action) return '—';

  return action
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

function getPriorityClass(priority: string) {
  switch (priority.toLowerCase()) {
    case 'critical':
      return 'bg-red-50 text-red-700 ring-red-600/20';

    case 'high':
      return 'bg-orange-50 text-orange-700 ring-orange-600/20';

    case 'medium':
      return 'bg-amber-50 text-amber-700 ring-amber-600/20';

    default:
      return 'bg-ink-50 text-ink-600 ring-ink-500/20';
  }
}

function getStatusClass(status: string) {
  switch (status.toLowerCase()) {
    case 'recovered':
      return 'text-emerald-600';

    case 'active':
      return 'text-blue-600';

    case 'escalated':
      return 'text-orange-600';

    case 'failed':
      return 'text-red-600';

    case 'stopped':
      return 'text-ink-500';

    default:
      return 'text-ink-500';
  }
}

function getStatusIcon(status: string) {
  switch (status.toLowerCase()) {
    case 'recovered':
      return <CheckCircle2 className="h-4 w-4" />;

    case 'active':
      return <Clock3 className="h-4 w-4" />;

    case 'escalated':
      return <AlertTriangle className="h-4 w-4" />;

    case 'failed':
      return <XCircle className="h-4 w-4" />;

    default:
      return <Clock3 className="h-4 w-4" />;
  }
}

export function RecoveryCases({ data }: Props) {
  return (
    <section className="overflow-hidden rounded-2xl border border-ink-200 bg-white shadow-sm">
      <div className="border-b border-ink-200 px-5 py-5 sm:px-6">
        <h2 className="text-base font-semibold text-ink-900">
          Recovery Cases
        </h2>

        <p className="mt-1 text-sm text-ink-500">
          Active and recently processed revenue recovery cases.
        </p>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full min-w-[900px]">
          <thead>
            <tr className="border-b border-ink-100 bg-ink-50/50">
              <th className="px-5 py-3 text-left text-[11px] font-medium uppercase tracking-wider text-ink-400">
                Customer
              </th>

              <th className="px-5 py-3 text-left text-[11px] font-medium uppercase tracking-wider text-ink-400">
                Revenue at Risk
              </th>

              <th className="px-5 py-3 text-left text-[11px] font-medium uppercase tracking-wider text-ink-400">
                Priority
              </th>

              <th className="px-5 py-3 text-left text-[11px] font-medium uppercase tracking-wider text-ink-400">
                Status
              </th>

              <th className="px-5 py-3 text-left text-[11px] font-medium uppercase tracking-wider text-ink-400">
                Failure
              </th>

              <th className="px-5 py-3 text-left text-[11px] font-medium uppercase tracking-wider text-ink-400">
                AI Action
              </th>

              <th className="px-5 py-3 text-left text-[11px] font-medium uppercase tracking-wider text-ink-400">
                Retries
              </th>
            </tr>
          </thead>

          <tbody className="divide-y divide-ink-100">
            {data.map((item) => (
              <tr
                key={item.recovery_case_id}
                className="transition hover:bg-ink-50/50"
              >
                <td className="px-5 py-4">
                  <p className="text-sm font-medium text-ink-900">
                    {item.customer_name}
                  </p>

                  <p className="mt-1 text-xs text-ink-400">
                    {item.customer_email}
                  </p>
                </td>

                <td className="px-5 py-4">
                  <p className="text-sm font-semibold text-ink-900">
                    {formatCurrency(item.revenue_at_risk)}
                  </p>
                </td>

                <td className="px-5 py-4">
                  <span
                    className={`inline-flex rounded-full px-2 py-1 text-[11px] font-medium capitalize ring-1 ring-inset ${getPriorityClass(
                      item.priority,
                    )}`}
                  >
                    {item.priority}
                  </span>
                </td>

                <td className="px-5 py-4">
                  <div
                    className={`flex items-center gap-1.5 text-sm font-medium ${getStatusClass(
                      item.status,
                    )}`}
                  >
                    {getStatusIcon(item.status)}

                    <span>
                      {formatAction(item.status)}
                    </span>
                  </div>
                </td>

                <td className="px-5 py-4">
                  <p className="text-sm text-ink-700">
                    {formatAction(item.failure_reason)}
                  </p>

                  {item.payment_method && (
                    <p className="mt-1 text-xs text-ink-400">
                      {formatAction(item.payment_method)}
                    </p>
                  )}
                </td>

                <td className="px-5 py-4">
                  <p className="text-sm font-medium text-indigo-600">
                    {formatAction(item.recommended_action)}
                  </p>

                  {item.root_cause && (
                    <p className="mt-1 text-xs text-ink-400">
                      {formatAction(item.root_cause)}
                    </p>
                  )}
                </td>

                <td className="px-5 py-4">
                  <span className="text-sm font-medium text-ink-800">
                    #{item.retry_count}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}