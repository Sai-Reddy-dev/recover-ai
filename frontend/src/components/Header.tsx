import { Activity, RefreshCw } from 'lucide-react';
import { formatTimestamp } from '@/lib/format';

interface HeaderProps {
  lastUpdated: Date | null;
  loading: boolean;
  onRefresh: () => void;
}

export function Header({ lastUpdated, loading, onRefresh }: HeaderProps) {
  return (
    <header className="sticky top-0 z-30 border-b border-ink-200 bg-white/80 backdrop-blur-md">
      <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-3 sm:px-6 lg:px-8">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-brand-600 to-brand-800 text-white shadow-sm">
            <Activity className="h-5 w-5" strokeWidth={2.2} />
          </div>
          <div>
            <h1 className="text-base font-semibold leading-tight text-ink-900 sm:text-lg">
              RecoverAI
            </h1>
            <p className="hidden text-xs text-ink-500 sm:block">
              AI Subscription Revenue Recovery
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {lastUpdated && (
            <p className="hidden text-xs text-ink-500 sm:block">
              Last updated{' '}
              <span className="font-medium text-ink-700">
                {formatTimestamp(lastUpdated.toISOString())}
              </span>
            </p>
          )}
          <button
            type="button"
            onClick={onRefresh}
            disabled={loading}
            className="inline-flex items-center gap-2 rounded-lg bg-brand-600 px-3 py-2 text-sm font-medium text-white shadow-sm transition hover:bg-brand-700 focus:outline-none focus:ring-2 focus:ring-brand-300 disabled:cursor-not-allowed disabled:opacity-60"
          >
            <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin-slow' : ''}`} />
            <span className="hidden sm:inline">Refresh</span>
          </button>
        </div>
      </div>
    </header>
  );
}
