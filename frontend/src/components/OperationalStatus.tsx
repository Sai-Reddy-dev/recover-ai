import type { LucideIcon } from 'lucide-react';
import { AlertCircle, XCircle, Ban, CreditCard, Users } from 'lucide-react';
import type { DashboardCases, PaymentDegradation } from '@/types/dashboard';
import { formatNumber } from '@/lib/format';

interface OperationalStatusProps {
  cases: DashboardCases;
  degradation: PaymentDegradation;
}

interface StatusItem {
  label: string;
  value: number;
  icon: LucideIcon;
  tone: 'brand' | 'rose' | 'amber' | 'slate' | 'violet';
}

const TONES: Record<StatusItem['tone'], { ring: string; iconBg: string; iconText: string; value: string }> = {
  brand: { ring: 'border-brand-200', iconBg: 'bg-brand-50', iconText: 'text-brand-600', value: 'text-ink-900' },
  rose: { ring: 'border-rose-200', iconBg: 'bg-rose-50', iconText: 'text-rose-600', value: 'text-rose-700' },
  amber: { ring: 'border-amber-200', iconBg: 'bg-amber-50', iconText: 'text-amber-600', value: 'text-amber-700' },
  slate: { ring: 'border-ink-200', iconBg: 'bg-ink-100', iconText: 'text-ink-600', value: 'text-ink-700' },
  violet: { ring: 'border-violet-200', iconBg: 'bg-violet-50', iconText: 'text-violet-600', value: 'text-violet-700' },
};

function StatusCard({ item }: { item: StatusItem }) {
  const tone = TONES[item.tone];
  const Icon = item.icon;
  return (
    <div className={`card card-pad flex items-center gap-4 ${tone.ring}`}>
      <div className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-lg ${tone.iconBg}`}>
        <Icon className={`h-5 w-5 ${tone.iconText}`} strokeWidth={2} />
      </div>
      <div className="min-w-0">
        <p className={`text-2xl font-semibold tracking-tight ${tone.value}`}>{formatNumber(item.value)}</p>
        <p className="truncate text-xs font-medium text-ink-500">{item.label}</p>
      </div>
    </div>
  );
}

export function OperationalStatus({ cases, degradation }: OperationalStatusProps) {
  const items: StatusItem[] = [
    { label: 'Active Recovery Cases', value: cases.active, icon: AlertCircle, tone: 'brand' },
    { label: 'Failed Recovery Cases', value: cases.failed, icon: XCircle, tone: 'rose' },
    { label: 'Stopped Workflows', value: cases.stopped, icon: Ban, tone: 'amber' },
    { label: 'Degraded Payment Methods', value: degradation.degraded_methods, icon: CreditCard, tone: 'slate' },
    { label: 'Affected Subscriptions', value: degradation.affected_subscriptions, icon: Users, tone: 'violet' },
  ];

  return (
    <section className="flex flex-col gap-4">
      <div>
        <h2 className="text-base font-semibold text-ink-900">Operational Status</h2>
        <p className="mt-0.5 text-sm text-ink-500">Current workload and system health</p>
      </div>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5">
        {items.map((item) => (
          <StatusCard key={item.label} item={item} />
        ))}
      </div>
    </section>
  );
}
