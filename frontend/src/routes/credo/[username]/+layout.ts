import { error } from '@sveltejs/kit';
import { getCredo, getGeographies, getMetrics } from '$lib/api';

export const ssr = false;

export async function load({ params, fetch }: { params: { username: string }; fetch: typeof globalThis.fetch }) {
	const [credoResult, geosResult, metricsResult] = await Promise.allSettled([
		getCredo(params.username, fetch),
		getGeographies(fetch),
		getMetrics(fetch)
	]);

	if (credoResult.status === 'rejected') {
		throw error(404, `No credo found for @${params.username}`);
	}

	return {
		credo: credoResult.value,
		geographies: geosResult.status === 'fulfilled' ? geosResult.value : [],
		metrics: metricsResult.status === 'fulfilled' ? metricsResult.value : []
	};
}
