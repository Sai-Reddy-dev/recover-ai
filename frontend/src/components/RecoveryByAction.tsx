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
import type { RecoveryByAction as RecoveryByActionType } from '@/types/dashboard';
import { actionLabel } from '@/lib/labels';
import { formatCompactINR, formatINR, formatNumber } from '@/lib/format';

interface RecoveryByActionProps {
  data: RecoveryByActionType[];
}

const PALETTE = ['#1c66f2', '#10b981', '#f59e0b', '#8b5cf6', '#ef4444', '#06b6d4'];

interface TooltipPayloadItem {
  payload: { action: string; label: string; recovered_cases: number; revenue_recovered: number };
}

function ActionTooltip({ active, payload }: { active?: boolean; payload?: TooltipPayloadItem[] }) {
  if (!active || !payload || payload.length === 0) return null;
  const item = payload[0].payload;
  return (
    <div className="rounded-lg border border-ink-200 bg-white px-3 py-2 shadow-card-hover">
      <p className="text-xs font-medium text-ink-500">{item.label}</p>
      <p className="mt-0.5 text-sm font-semibold text-ink-900">{formatINR(item.revenue_recovered)}</p>
      <p className="text-xs text-ink-500">{formatNumber(item.recovered_cases)} cases</p>
    </div>
  );
}

export function RecoveryByAction({ data }: RecoveryByActionProps) {
  const chartData = data.map((d) => ({
    ...d,
    label: actionLabel(d.action),
  }));

  return (
    <section className="card card-pad flex flex-col gap-5">
      <div>
        <h2 className="text-base font-semibold text-ink-900">Recovery by Action</h2>
        <p className="mt-0.5 text-sm text-ink-500">
          Recovered cases and revenue per recovery action
        </p>
      </div>
      {chartData.length === 0 ? (
        <div className="flex h-64 items-center justify-center text-sm text-ink-400">
          No recovery actions recorded yet
        </div>
      ) : (
        <div className="h-64 w-full sm:h-72">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} layout="vertical" margin={{ top: 4, right: 16, left: 8, bottom: 4 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#eceef2" horizontal={false} />
              <XAxis
                type="number"
                tick={{ fill: '#667891', fontSize: 12 }}
                tickFormatter={(v: number) => formatCompactINR(v)}
                axisLine={false}
                tickLine={false}
              />
              <YAxis
                type="category"
                dataKey="label"
                tick={{ fill: '#526076', fontSize: 12 }}
                axisLine={false}
                tickLine={false}
                width={120}
              />
              <Tooltip content={<ActionTooltip />} cursor={{ fill: 'rgba(102,120,145,0.06)' }} />
              <Bar dataKey="revenue_recovered" radius={[0, 6, 6, 0]} maxBarSize={36}>
                {chartData.map((entry, i) => (
                  <Cell key={entry.action} fill={PALETTE[i % PALETTE.length]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </section>
  );
}
