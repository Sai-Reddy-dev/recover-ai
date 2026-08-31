import { useCallback, useEffect, useRef, useState } from 'react';
import type { DashboardData } from '@/types/dashboard';
import { fetchDashboard } from '@/lib/api';
import { Header } from '@/components/Header';
import { KpiCards } from '@/components/KpiCards';
import { RecoveryPerformance } from '@/components/RecoveryPerformance';
import { RecoveryByAction } from '@/components/RecoveryByAction';
import { OperationalStatus } from '@/components/OperationalStatus';
import { PaymentDegradationSection } from '@/components/PaymentDegradationSection';
import { AuditTrail } from '@/components/AuditTrail';
import { DashboardSkeleton } from '@/components/DashboardSkeleton';
import { ErrorState } from '@/components/ErrorState';
import { EmptyState } from '@/components/EmptyState';

type Status = 'loading' | 'success' | 'error' | 'empty';

function hasData(data: DashboardData | null): data is DashboardData {
  if (!data) return false;
  const s = data.summary;
  return (
    s.revenue_at_risk > 0 ||
    s.revenue_recovered > 0 ||
    s.recovery_rate > 0 ||
    s.recovered_subscriptions > 0 ||
    s.recovered_cases > 0 ||
    data.cases.active > 0 ||
    data.cases.failed > 0 ||
    data.cases.stopped > 0 ||
    data.recovery_by_action.length > 0 ||
    data.recent_audit_events.length > 0 ||
    data.payment_degradation.degraded_methods > 0 ||
    data.payment_degradation.affected_subscriptions > 0
  );
}

export function Dashboard() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [status, setStatus] = useState<Status>('loading');
  const [error, setError] = useState<string>('');
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [refreshing, setRefreshing] = useState(false);
  const abortRef = useRef<AbortController | null>(null);

  const load = useCallback(async () => {
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    setRefreshing(true);
    try {
      const result = await fetchDashboard(controller.signal);
      setData(result);
      setLastUpdated(new Date());
      setStatus(hasData(result) ? 'success' : 'empty');
      setError('');
    } catch (err) {
      if (controller.signal.aborted) return;
      const message = err instanceof Error ? err.message : 'Something went wrong';
      setError(message);
      setStatus('error');
    } finally {
      if (!controller.signal.aborted) setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    load();
    return () => abortRef.current?.abort();
  }, [load]);

  const handleRefresh = useCallback(() => {
    load();
  }, [load]);

  return (
    <div className="min-h-screen bg-ink-50">
      <Header lastUpdated={lastUpdated} loading={refreshing} onRefresh={handleRefresh} />

      <main className="mx-auto max-w-7xl px-4 py-6 sm:px-6 sm:py-8 lg:px-8">
        {status === 'loading' && <DashboardSkeleton />}

        {status === 'error' && <ErrorState message={error} onRetry={handleRefresh} />}

        {status === 'empty' && <EmptyState onRefresh={handleRefresh} />}

        {status === 'success' && data && (
          <div className="flex flex-col gap-6">
            <KpiCards summary={data.summary} />

            <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
              <RecoveryPerformance summary={data.summary} />
              <RecoveryByAction data={data.recovery_by_action} />
            </div>

            <OperationalStatus cases={data.cases} degradation={data.payment_degradation} />

            <PaymentDegradationSection data={data.payment_degradation} />

            <AuditTrail events={data.recent_audit_events} />
          </div>
        )}
      </main>

      <footer className="border-t border-ink-200 bg-white">
        <div className="mx-auto max-w-7xl px-4 py-4 sm:px-6 lg:px-8">
          <p className="text-center text-xs text-ink-400">
            RecoverAI · AI Subscription Revenue Recovery
          </p>
        </div>
      </footer>
    </div>
  );
}
