import { Activity } from 'lucide-react';

interface EmptyStateProps {
  onRefresh: () => void;
}

export function EmptyState({ onRefresh }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center gap-4 py-20 text-center">
      <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-brand-50">
        <Activity className="h-7 w-7 text-brand-600" strokeWidth={2} />
      </div>
      <div>
        <h2 className="text-lg font-semibold text-ink-900">No dashboard data yet</h2>
        <p className="mt-1 max-w-md text-sm text-ink-500">
          RecoverAI hasn't recorded any recovery activity. Once the backend processes
          subscription failures, metrics will appear here.
        </p>
      </div>
      <button
        type="button"
        onClick={onRefresh}
        className="inline-flex items-center gap-2 rounded-lg border border-ink-200 bg-white px-4 py-2 text-sm font-medium text-ink-700 shadow-sm transition hover:bg-ink-50 focus:outline-none focus:ring-2 focus:ring-brand-300"
      >
        Refresh
      </button>
    </div>
  );
}
