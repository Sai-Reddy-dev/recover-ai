import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import type { DashboardSummary } from '@/types/dashboard';
import { formatCompactINR, formatINR } from '@/lib/format';

interface RecoveryPerformanceProps {
  summary: DashboardSummary;
}

interface TooltipPayloadItem {
  payload: { label: string; value: number };
  value: number;
}

function PerformanceTooltip({ active, payload }: { active?: boolean; payload?: TooltipPayloadItem[] }) {
  if (!active || !payload || payload.length === 0) return null;
  const item = payload[0];
  return (
    <div className="rounded-lg border border-ink-200 bg-white px-3 py-2 shadow-card-hover">
      <p className="text-xs font-medium text-ink-500">{item.payload.label}</p>
      <p className="text-sm font-semibold text-ink-900">{formatINR(item.value)}</p>
    </div>
  );
}

export function RecoveryPerformance({ summary }: RecoveryPerformanceProps) {
  const data = [
    { label: 'Revenue at Risk', value: summary.revenue_at_risk, fill: '#f43f5e' },
    { label: 'Revenue Recovered', value: summary.revenue_recovered, fill: '#10b981' },
  ];

  return (
    <section className="card card-pad flex flex-col gap-5">
      <div>
        <h2 className="text-base font-semibold text-ink-900">Recovery Performance</h2>
        <p className="mt-0.5 text-sm text-ink-500">
          Revenue at risk versus revenue recovered
        </p>
      </div>
      <div className="h-64 w-full sm:h-72">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} margin={{ top: 8, right: 8, left: 8, bottom: 8 }} barCategoryGap="28%">
            <CartesianGrid strokeDasharray="3 3" stroke="#eceef2" vertical={false} />
            <XAxis
              dataKey="label"
              tick={{ fill: '#667891', fontSize: 12 }}
              axisLine={{ stroke: '#d5dae2' }}
              tickLine={false}
            />
            <YAxis
              tick={{ fill: '#667891', fontSize: 12 }}
              tickFormatter={(v: number) => formatCompactINR(v)}
              axisLine={false}
              tickLine={false}
              width={72}
            />
            <Tooltip content={<PerformanceTooltip />} cursor={{ fill: 'rgba(102,120,145,0.06)' }} />
            <Bar dataKey="value" radius={[6, 6, 0, 0]} maxBarSize={120}>
              {data.map((entry) => (
                <Cell key={entry.label} fill={entry.fill} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}
