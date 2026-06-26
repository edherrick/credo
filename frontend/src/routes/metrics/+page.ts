export const ssr = false;

import { getMetrics } from '$lib/api';

export async function load({ fetch }: { fetch: typeof globalThis.fetch }) {
	try {
		return { metrics: await getMetrics(fetch) };
	} catch {
		return { metrics: [] };
	}
}
