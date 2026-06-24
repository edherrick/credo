export const ssr = false;

import { getBeliefs, getIssues, getAxes, getMetrics, getEntities } from '$lib/api';

export async function load({ fetch }: { fetch: typeof globalThis.fetch }) {
	const [beliefsRes, issuesRes, axesRes, metricsRes, entitiesRes] = await Promise.allSettled([
		getBeliefs(fetch),
		getIssues(fetch),
		getAxes(fetch),
		getMetrics(fetch),
		getEntities(fetch)
	]);

	return {
		beliefs: beliefsRes.status === 'fulfilled' ? beliefsRes.value : [],
		issues: issuesRes.status === 'fulfilled' ? issuesRes.value : [],
		axes: axesRes.status === 'fulfilled' ? axesRes.value : [],
		metrics: metricsRes.status === 'fulfilled' ? metricsRes.value : [],
		entities: entitiesRes.status === 'fulfilled' ? entitiesRes.value : []
	};
}
