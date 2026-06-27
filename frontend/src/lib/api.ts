import type {
	Agenda,
	Axis,
	Belief,
	AuthToken,
	Credo,
	CredoCreateInput,
	CredoSummary,
	CredoUpdateInput,
	EntityDetail,
	Geography,
	Issue,
	Metric,
	MetricAggregateResponse,
	MetricValuesResponse,
	User
} from './types';

const BASE = '/api/v1';

// Read helpers accept an optional `fetch` so SvelteKit `load` functions can pass
// their instrumented fetch (event.fetch). Defaults to the global fetch for use
// from components/event handlers.
type Fetch = typeof fetch;

function authHeaders(token: string): HeadersInit {
	return { Authorization: `Bearer ${token}` };
}

function jsonAuthHeaders(token: string): HeadersInit {
	return { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' };
}

export async function getGeographies(fetchFn: Fetch = fetch): Promise<Geography[]> {
	const res = await fetchFn(`${BASE}/geographies`);
	if (!res.ok) throw new Error('Failed to fetch geographies');
	return res.json();
}

export async function getMetrics(fetchFn: Fetch = fetch): Promise<Metric[]> {
	const res = await fetchFn(`${BASE}/metrics`);
	if (!res.ok) throw new Error('Failed to fetch metrics');
	return res.json();
}

export async function getMetricValues(
	fips: string,
	metricId: string,
	params?: { date_from?: string; date_to?: string },
	fetchFn: Fetch = fetch
): Promise<MetricValuesResponse> {
	const url = new URL(`${BASE}/geographies/${fips}/metrics/${metricId}/values`, location.origin);
	if (params?.date_from) url.searchParams.set('date_from', params.date_from);
	if (params?.date_to) url.searchParams.set('date_to', params.date_to);
	const res = await fetchFn(url.toString());
	if (!res.ok) throw new Error('Failed to fetch metric values');
	return res.json();
}

export async function getStateMetricGeoJSON(
	stateFips: string,
	metricId: string,
	date?: string,
	fetchFn: Fetch = fetch
	// eslint-disable-next-line @typescript-eslint/no-explicit-any
): Promise<any> {
	const url = new URL(`${BASE}/metrics/${metricId}/geojson`, location.origin);
	url.searchParams.set('state_fips', stateFips);
	if (date) url.searchParams.set('date', date);
	const res = await fetchFn(url.toString());
	if (!res.ok) throw new Error('Failed to fetch state GeoJSON');
	return res.json();
}

export async function getMetricGeoJSON(
	fips: string,
	metricId: string,
	date?: string,
	fetchFn: Fetch = fetch
	// eslint-disable-next-line @typescript-eslint/no-explicit-any
): Promise<any> {
	const url = new URL(`${BASE}/geographies/${fips}/metrics/${metricId}/geojson`, location.origin);
	if (date) url.searchParams.set('date', date);
	const res = await fetchFn(url.toString());
	if (!res.ok) throw new Error('Failed to fetch GeoJSON');
	return res.json();
}

export async function getMetricAggregate(
	metricId: string,
	stateFips: string,
	fetchFn: Fetch = fetch
): Promise<MetricAggregateResponse> {
	const url = new URL(`${BASE}/metrics/${metricId}/aggregate`, location.origin);
	url.searchParams.set('state_fips', stateFips);
	const res = await fetchFn(url.toString());
	if (!res.ok) throw new Error('Failed to fetch metric aggregate');
	return res.json();
}

export async function getAgendas(fetchFn: Fetch = fetch): Promise<Agenda[]> {
	const res = await fetchFn(`${BASE}/agendas`);
	if (!res.ok) throw new Error('Failed to fetch agendas');
	return res.json();
}

export async function getCredos(fetchFn: Fetch = fetch): Promise<CredoSummary[]> {
	const res = await fetchFn(`${BASE}/credos`);
	if (!res.ok) throw new Error('Failed to fetch credos');
	return res.json();
}

export async function getCredo(username: string, fetchFn: Fetch = fetch): Promise<Credo> {
	const res = await fetchFn(`${BASE}/credos/${username}`);
	if (!res.ok) throw new Error('Credo not found');
	return res.json();
}

export async function createCredo(token: string, input: CredoCreateInput): Promise<CredoSummary> {
	const res = await fetch(`${BASE}/credos`, {
		method: 'POST',
		headers: jsonAuthHeaders(token),
		body: JSON.stringify(input)
	});
	if (!res.ok) {
		const err = await res.json().catch(() => ({}));
		throw new Error(err.detail ?? 'Failed to create credo');
	}
	return res.json();
}

export async function updateCredo(
	token: string,
	username: string,
	input: CredoUpdateInput
): Promise<CredoSummary> {
	const res = await fetch(`${BASE}/credos/${username}`, {
		method: 'PATCH',
		headers: jsonAuthHeaders(token),
		body: JSON.stringify(input)
	});
	if (!res.ok) {
		const err = await res.json().catch(() => ({}));
		throw new Error(err.detail ?? 'Failed to update credo');
	}
	return res.json();
}

export async function deleteCredo(token: string, username: string): Promise<void> {
	const res = await fetch(`${BASE}/credos/${username}`, {
		method: 'DELETE',
		headers: authHeaders(token)
	});
	if (!res.ok) {
		const err = await res.json().catch(() => ({}));
		throw new Error(err.detail ?? 'Failed to delete credo');
	}
}

export async function getFollowing(token: string, fetchFn: Fetch = fetch): Promise<CredoSummary[]> {
	const res = await fetchFn(`${BASE}/credos/following`, { headers: authHeaders(token) });
	if (!res.ok) throw new Error('Failed to fetch followed credos');
	return res.json();
}

export async function followCredo(token: string, username: string): Promise<void> {
	const res = await fetch(`${BASE}/credos/${username}/follow`, {
		method: 'POST',
		headers: authHeaders(token)
	});
	if (!res.ok) throw new Error('Failed to follow credo');
}

export async function unfollowCredo(token: string, username: string): Promise<void> {
	const res = await fetch(`${BASE}/credos/${username}/follow`, {
		method: 'DELETE',
		headers: authHeaders(token)
	});
	if (!res.ok) throw new Error('Failed to unfollow credo');
}

export async function getBeliefs(fetchFn: Fetch = fetch): Promise<Belief[]> {
	const res = await fetchFn(`${BASE}/beliefs`);
	if (!res.ok) throw new Error('Failed to fetch beliefs');
	return res.json();
}

export async function getBelief(id: string, fetchFn: Fetch = fetch): Promise<Belief> {
	const res = await fetchFn(`${BASE}/beliefs/${id}`);
	if (!res.ok) throw new Error('Belief not found');
	return res.json();
}

export async function getSavedBeliefs(token: string, fetchFn: Fetch = fetch): Promise<Belief[]> {
	const res = await fetchFn(`${BASE}/beliefs/saved`, { headers: authHeaders(token) });
	if (!res.ok) throw new Error('Failed to fetch saved beliefs');
	return res.json();
}

export async function saveBelief(token: string, beliefId: string): Promise<void> {
	const res = await fetch(`${BASE}/beliefs/${beliefId}/save`, {
		method: 'POST',
		headers: authHeaders(token)
	});
	if (!res.ok) throw new Error('Failed to save belief');
}

export async function unsaveBelief(token: string, beliefId: string): Promise<void> {
	const res = await fetch(`${BASE}/beliefs/${beliefId}/save`, {
		method: 'DELETE',
		headers: authHeaders(token)
	});
	if (!res.ok) throw new Error('Failed to unsave belief');
}

export async function addBeliefToCredo(
	token: string,
	username: string,
	beliefId: string
): Promise<void> {
	const res = await fetch(`${BASE}/credos/${username}/beliefs`, {
		method: 'POST',
		headers: jsonAuthHeaders(token),
		body: JSON.stringify({ belief_id: beliefId })
	});
	if (!res.ok) {
		const err = await res.json().catch(() => ({}));
		throw new Error(err.detail ?? 'Failed to add belief to credo');
	}
}

export async function removeBeliefFromCredo(
	token: string,
	username: string,
	beliefId: string
): Promise<void> {
	const res = await fetch(`${BASE}/credos/${username}/beliefs/${beliefId}`, {
		method: 'DELETE',
		headers: authHeaders(token)
	});
	if (!res.ok) throw new Error('Failed to remove belief from credo');
}

export async function getIssues(fetchFn: Fetch = fetch): Promise<Issue[]> {
	const res = await fetchFn(`${BASE}/issues`);
	if (!res.ok) throw new Error('Failed to fetch issues');
	return res.json();
}

export async function getAxes(fetchFn: Fetch = fetch): Promise<Axis[]> {
	const res = await fetchFn(`${BASE}/axes`);
	if (!res.ok) throw new Error('Failed to fetch axes');
	return res.json();
}

export async function getEntities(fetchFn: Fetch = fetch): Promise<EntityDetail[]> {
	const res = await fetchFn(`${BASE}/entities`);
	if (!res.ok) throw new Error('Failed to fetch entities');
	return res.json();
}

export async function getEntity(slug: string, fetchFn: Fetch = fetch): Promise<EntityDetail> {
	const res = await fetchFn(`${BASE}/entities/${slug}`);
	if (!res.ok) throw new Error('Entity not found');
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
