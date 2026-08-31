import type { AuditEvent } from '@/types/dashboard';
import { eventLabel, eventSeverity, type AuditSeverity } from '@/lib/labels';
import { formatRelativeTime, formatTimestamp } from '@/lib/format';

interface AuditTrailProps {
  events: AuditEvent[];
}

const SEVERITY_STYLE: Record<AuditSeverity, { dot: string; chip: string; text: string }> = {
  critical: { dot: 'bg-rose-500', chip: 'bg-rose-50 text-rose-700', text: 'text-rose-600' },
  warning: { dot: 'bg-amber-500', chip: 'bg-amber-50 text-amber-700', text: 'text-amber-600' },
  info: { dot: 'bg-brand-500', chip: 'bg-brand-50 text-brand-700', text: 'text-brand-600' },
  success: { dot: 'bg-emerald-500', chip: 'bg-emerald-50 text-emerald-700', text: 'text-emerald-600' },
  neutral: { dot: 'bg-ink-400', chip: 'bg-ink-100 text-ink-600', text: 'text-ink-500' },
};

function AuditItem({ event, isLast }: { event: AuditEvent; isLast: boolean }) {
  const severity = eventSeverity(event.event_type);
  const style = SEVERITY_STYLE[severity];

  return (
    <li className="relative pl-8">
      <span
        className={`absolute left-3 top-1.5 h-3 w-3 rounded-full ring-4 ring-white ${style.dot}`}
        aria-hidden
      />
      {!isLast && (
        <span className="absolute left-[17px] top-5 h-[calc(100%-8px)] w-px bg-ink-200" aria-hidden />
      )}
      <div className="pb-6">
        <div className="flex flex-wrap items-center gap-2">
          <span className={`inline-flex items-center rounded-md px-2 py-0.5 text-xs font-medium ${style.chip}`}>
            {eventLabel(event.event_type)}
          </span>
          <span className="text-xs text-ink-500">
            {formatRelativeTime(event.created_at)}
          </span>
        </div>
        <p className="mt-1.5 text-sm text-ink-800">{event.message}</p>
        <p className="mt-1 text-xs text-ink-400">
          <span className="font-medium text-ink-500">{event.actor}</span>
          {' · '}
          {formatTimestamp(event.created_at)}
        </p>
      </div>
    </li>
  );
}

export function AuditTrail({ events }: AuditTrailProps) {
  return (
    <section className="card card-pad flex flex-col gap-5">
      <div>
        <h2 className="text-base font-semibold text-ink-900">Audit Trail</h2>
        <p className="mt-0.5 text-sm text-ink-500">Recent RecoverAI activity and decisions</p>
      </div>
      {events.length === 0 ? (
        <div className="flex h-40 items-center justify-center text-sm text-ink-400">
          No recent activity recorded
        </div>
      ) : (
        <ol className="relative">
          {events.map((event, i) => (
            <AuditItem key={`${event.created_at}-${i}`} event={event} isLast={i === events.length - 1} />
          ))}
        </ol>
      )}
    </section>
  );
}
