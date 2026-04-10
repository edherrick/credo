import { error } from '@sveltejs/kit';
import { getCredo, getGeographies, getMetrics } from '$lib/api';

export const ssr = false;

export async function load({ params }: { params: { username: string } }) {
	const [credoResult, geosResult, metricsResult] = await Promise.allSettled([
		getCredo(params.username),
		getGeographies(),
		getMetrics()
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
