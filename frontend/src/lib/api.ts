import type { DashboardData } from '@/types/dashboard';

const API_BASE = import.meta.env.VITE_API_BASE ?? 'http://127.0.0.1:8000';

export async function fetchDashboard(signal?: AbortSignal): Promise<DashboardData> {
  const url = `${API_BASE}/dashboard`.replace(/\/+$/, '');
  const res = await fetch(url, {
    signal,
    headers: { Accept: 'application/json' },
  });

  if (!res.ok) {
    throw new Error(`Request failed (${res.status})`);
  }

  const data = (await res.json()) as DashboardData;
  return data;
}
