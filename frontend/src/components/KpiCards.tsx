import type { LucideIcon } from 'lucide-react';
import { TrendingDown, TrendingUp, Percent, CheckCircle2 } from 'lucide-react';
import type { DashboardSummary } from '@/types/dashboard';
import { formatINR, formatNumber, formatPercent } from '@/lib/format';

interface KpiCardsProps {
  summary: DashboardSummary;
}

interface Kpi {
  label: string;
  value: string;
  sub: string;
  icon: LucideIcon;
  tone: 'risk' | 'recovered' | 'rate' | 'subs';
}

const TONES: Record<Kpi['tone'], { ring: string; iconBg: string; iconText: string; accent: string }> = {
  risk: {
    ring: 'border-rose-200',
    iconBg: 'bg-rose-50',
    iconText: 'text-rose-600',
    accent: 'text-rose-700',
  },
  recovered: {
    ring: 'border-emerald-200',
    iconBg: 'bg-emerald-50',
    iconText: 'text-emerald-600',
    accent: 'text-emerald-700',
  },
  rate: {
    ring: 'border-brand-200',
    iconBg: 'bg-brand-50',
    iconText: 'text-brand-600',
    accent: 'text-brand-700',
  },
  subs: {
    ring: 'border-violet-200',
    iconBg: 'bg-violet-50',
    iconText: 'text-violet-600',
    accent: 'text-violet-700',
  },
};

function KpiCard({ kpi }: { kpi: Kpi }) {
  const tone = TONES[kpi.tone];
  const Icon = kpi.icon;
  return (
    <div className={`card card-pad flex flex-col gap-4 ${tone.ring}`}>
      <div className="flex items-start justify-between">
        <p className="text-sm font-medium text-ink-500">{kpi.label}</p>
        <div className={`flex h-9 w-9 items-center justify-center rounded-lg ${tone.iconBg}`}>
          <Icon className={`h-5 w-5 ${tone.iconText}`} strokeWidth={2} />
        </div>
      </div>
      <div>
        <p className={`text-2xl font-semibold tracking-tight sm:text-3xl ${tone.accent}`}>
          {kpi.value}
        </p>
        <p className="mt-1 text-xs text-ink-500">{kpi.sub}</p>
      </div>
    </div>
  );
}

export function KpiCards({ summary }: KpiCardsProps) {
  const kpis: Kpi[] = [
    {
      label: 'Revenue at Risk',
      value: formatINR(summary.revenue_at_risk),
      sub: 'Currently exposed across active cases',
      icon: TrendingDown,
      tone: 'risk',
    },
    {
      label: 'Revenue Recovered',
      value: formatINR(summary.revenue_recovered),
      sub: 'Total recovered to date',
      icon: TrendingUp,
      tone: 'recovered',
    },
    {
      label: 'Recovery Rate',
      value: formatPercent(summary.recovery_rate),
      sub: 'Recovered vs. at-risk revenue',
      icon: Percent,
      tone: 'rate',
    },
    {
      label: 'Recovered Subscriptions',
      value: formatNumber(summary.recovered_subscriptions),
      sub: `${formatNumber(summary.recovered_cases)} cases resolved`,
      icon: CheckCircle2,
      tone: 'subs',
    },
  ];

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
      {kpis.map((kpi) => (
        <KpiCard key={kpi.label} kpi={kpi} />
      ))}
    </div>
  );
}
