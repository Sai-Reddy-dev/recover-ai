const lakhGroups = (n: number) => {
  const sign = n < 0 ? '-' : '';
  let int = Math.abs(Math.trunc(n)).toString();
  let lastThree = int.slice(-3);
  const rest = int.slice(0, -3);
  if (rest) {
    lastThree = ',' + lastThree;
    int = rest.replace(/\B(?=(\d{2})+(?!\d))/g, ',') + lastThree;
  } else {
    int = lastThree;
  }
  return sign + int;
};

export function formatINR(value: number): string {
  if (!Number.isFinite(value)) return '₹0';
  return `₹${lakhGroups(value)}`;
}

export function formatNumber(value: number): string {
  if (!Number.isFinite(value)) return '0';
  return new Intl.NumberFormat('en-IN').format(value);
}

export function formatPercent(value: number): string {
  if (!Number.isFinite(value)) return '0%';
  return `${value.toFixed(1)}%`;
}

export function formatCompactINR(value: number): string {
  if (!Number.isFinite(value)) return '₹0';
  if (Math.abs(value) >= 1_00_00_000) return `₹${(value / 1_00_00_000).toFixed(2)}Cr`;
  if (Math.abs(value) >= 1_00_000) return `₹${(value / 1_00_000).toFixed(2)}L`;
  if (Math.abs(value) >= 1_000) return `₹${(value / 1_000).toFixed(1)}K`;
  return `₹${Math.trunc(value)}`;
}

export function formatRelativeTime(iso: string): string {
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return '';
  const diffMs = Date.now() - date.getTime();
  const sec = Math.round(diffMs / 1000);
  if (sec < 60) return `${sec}s ago`;
  const min = Math.round(sec / 60);
  if (min < 60) return `${min}m ago`;
  const hr = Math.round(min / 60);
  if (hr < 24) return `${hr}h ago`;
  const day = Math.round(hr / 24);
  if (day < 30) return `${day}d ago`;
  return date.toLocaleDateString('en-IN', { day: 'numeric', month: 'short' });
}

export function formatTimestamp(iso: string): string {
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return '';
  return date.toLocaleString('en-IN', {
    day: '2-digit',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
  });
}
