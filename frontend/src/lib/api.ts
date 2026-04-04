import type { Agenda, AuthToken, Geography, Metric, MetricValuesResponse, User } from './types';

const BASE = '/api/v1';

function authHeaders(token: string): HeadersInit {
	return { Authorization: `Bearer ${token}` };
}

export async function getGeographies(): Promise<Geography[]> {
	const res = await fetch(`${BASE}/geographies`);
	if (!res.ok) throw new Error('Failed to fetch geographies');
	return res.json();
}

export async function getMetrics(): Promise<Metric[]> {
	const res = await fetch(`${BASE}/metrics`);
	if (!res.ok) throw new Error('Failed to fetch metrics');
	return res.json();
}

export async function getMetricValues(
	fips: string,
	metricId: string,
	params?: { date_from?: string; date_to?: string }
): Promise<MetricValuesResponse> {
	const url = new URL(`${BASE}/geographies/${fips}/metrics/${metricId}/values`, location.origin);
	if (params?.date_from) url.searchParams.set('date_from', params.date_from);
	if (params?.date_to) url.searchParams.set('date_to', params.date_to);
	const res = await fetch(url.toString());
	if (!res.ok) throw new Error('Failed to fetch metric values');
	return res.json();
}

export async function getMetricGeoJSON(
	fips: string,
	metricId: string,
	date?: string
	// eslint-disable-next-line @typescript-eslint/no-explicit-any
): Promise<any> {
	const url = new URL(`${BASE}/geographies/${fips}/metrics/${metricId}/geojson`, location.origin);
	if (date) url.searchParams.set('date', date);
	const res = await fetch(url.toString());
	if (!res.ok) throw new Error('Failed to fetch GeoJSON');
	return res.json();
}

export async function getAgendas(): Promise<Agenda[]> {
	const res = await fetch(`${BASE}/agendas`);
	if (!res.ok) throw new Error('Failed to fetch agendas');
	return res.json();
}

export async function register(email: string, password: string, username: string): Promise<User> {
	const res = await fetch(`${BASE}/auth/register`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify({ email, password, username })
	});
	if (!res.ok) {
		const err = await res.json();
		throw new Error(err.detail ?? 'Registration failed');
	}
	return res.json();
}

export async function login(email: string, password: string): Promise<AuthToken> {
	const body = new URLSearchParams({ username: email, password });
	const res = await fetch(`${BASE}/auth/login`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
		body: body.toString()
	});
	if (!res.ok) throw new Error('Invalid credentials');
	return res.json();
}

export async function getMe(token: string): Promise<User> {
	const res = await fetch(`${BASE}/auth/me`, { headers: authHeaders(token) });
	if (!res.ok) throw new Error('Not authenticated');
	return res.json();
}
