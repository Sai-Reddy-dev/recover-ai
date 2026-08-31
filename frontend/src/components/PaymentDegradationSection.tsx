import { AlertTriangle, CreditCard, Users, IndianRupee } from 'lucide-react';
import type { PaymentDegradation } from '@/types/dashboard';
import { formatINR, formatNumber } from '@/lib/format';

interface PaymentDegradationSectionProps {
  data: PaymentDegradation;
}

export function PaymentDegradationSection({ data }: PaymentDegradationSectionProps) {
  const cells = [
    {
      label: 'Degraded Payment Methods',
      value: formatNumber(data.degraded_methods),
      icon: CreditCard,
      iconBg: 'bg-amber-50',
      iconText: 'text-amber-600',
    },
    {
      label: 'Affected Subscriptions',
      value: formatNumber(data.affected_subscriptions),
      icon: Users,
      iconBg: 'bg-rose-50',
      iconText: 'text-rose-600',
    },
    {
      label: 'Revenue at Risk from Degradation',
      value: formatINR(data.revenue_at_risk),
      icon: IndianRupee,
      iconBg: 'bg-rose-50',
      iconText: 'text-rose-600',
    },
  ];

  const hasDegradation = data.degraded_methods > 0 || data.affected_subscriptions > 0;

  return (
    <section className="card card-pad flex flex-col gap-5">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h2 className="text-base font-semibold text-ink-900">Payment Degradation</h2>
          <p className="mt-0.5 text-sm text-ink-500">
            Payment methods experiencing issues and their revenue impact
          </p>
        </div>
        <div
          className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-lg ${
            hasDegradation ? 'bg-rose-50' : 'bg-emerald-50'
          }`}
        >
          <AlertTriangle
            className={`h-5 w-5 ${hasDegradation ? 'text-rose-600' : 'text-emerald-600'}`}
            strokeWidth={2}
          />
        </div>
      </div>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        {cells.map((cell) => {
          const Icon = cell.icon;
          return (
            <div key={cell.label} className="rounded-lg border border-ink-200 bg-ink-50/50 p-4">
              <div className="flex items-center gap-2">
                <div className={`flex h-8 w-8 items-center justify-center rounded-md ${cell.iconBg}`}>
                  <Icon className={`h-4 w-4 ${cell.iconText}`} strokeWidth={2} />
                </div>
                <p className="text-xs font-medium text-ink-500">{cell.label}</p>
              </div>
              <p className="mt-3 text-xl font-semibold tracking-tight text-ink-900">{cell.value}</p>
            </div>
          );
        })}
      </div>
    </section>
  );
}
