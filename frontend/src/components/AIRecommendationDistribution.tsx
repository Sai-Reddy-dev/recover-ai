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

import type {
  AIRecommendationDistribution as AIRecommendationDistributionType,
} from '@/types/dashboard';

import { actionLabel } from '@/lib/labels';
import { formatNumber } from '@/lib/format';

interface Props {
  data: AIRecommendationDistributionType[];
}

interface TooltipPayloadItem {
  payload: {
    action: string;
    label: string;
    decision_count: number;
  };
}

function RecommendationTooltip({
  active,
  payload,
}: {
  active?: boolean;
  payload?: TooltipPayloadItem[];
}) {
  if (!active || !payload || payload.length === 0) {
    return null;
  }

  const item = payload[0].payload;

  return (
    <div className="rounded-lg border border-ink-200 bg-white px-3 py-2 shadow-card-hover">
      <p className="text-xs font-medium text-ink-500">
        {item.label}
      </p>

      <p className="mt-0.5 text-sm font-semibold text-ink-900">
        {formatNumber(item.decision_count)} decisions
      </p>
    </div>
  );
}

const PALETTE = [
  '#1c66f2',
  '#10b981',
  '#f59e0b',
  '#8b5cf6',
  '#ef4444',
  '#06b6d4',
];

export function AIRecommendationDistribution({
  data,
}: Props) {
  const chartData = data.map((item) => ({
    ...item,
    label: actionLabel(item.action),
  }));

  return (
    <section className="card card-pad flex flex-col gap-5">
      <div>
        <h2 className="text-base font-semibold text-ink-900">
          AI Recommendation Distribution
        </h2>

        <p className="mt-0.5 text-sm text-ink-500">
          Recovery actions recommended by the AI agent
        </p>
      </div>

      {chartData.length === 0 ? (
        <div className="flex h-64 items-center justify-center text-sm text-ink-400">
          No AI decisions recorded yet
        </div>
      ) : (
        <div className="h-64 w-full sm:h-72">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={chartData}
              layout="vertical"
              margin={{
                top: 4,
                right: 16,
                left: 8,
                bottom: 4,
              }}
            >
              <CartesianGrid
                strokeDasharray="3 3"
                stroke="#eceef2"
                horizontal={false}
              />

              <XAxis
                type="number"
                tick={{ fill: '#667891', fontSize: 12 }}
                tickFormatter={(value: number) =>
                  formatNumber(value)
                }
                axisLine={false}
                tickLine={false}
              />

              <YAxis
                type="category"
                dataKey="label"
                tick={{ fill: '#526076', fontSize: 12 }}
                axisLine={false}
                tickLine={false}
                width={140}
              />

              <Tooltip
                content={<RecommendationTooltip />}
                cursor={{
                  fill: 'rgba(102,120,145,0.06)',
                }}
              />

              <Bar
                dataKey="decision_count"
                radius={[0, 6, 6, 0]}
                maxBarSize={32}
              >
                {chartData.map((entry, index) => (
                  <Cell
                    key={entry.action}
                    fill={PALETTE[index % PALETTE.length]}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </section>
  );
}