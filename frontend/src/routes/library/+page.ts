export const ssr = false;

import { getBeliefs, getIssues, getAxes, getMetrics, getEntities } from '$lib/api';

export async function load() {
	const [beliefsRes, issuesRes, axesRes, metricsRes, entitiesRes] = await Promise.allSettled([
		getBeliefs(),
		getIssues(),
		getAxes(),
		getMetrics(),
		getEntities()
	]);

	return {
		beliefs: beliefsRes.status === 'fulfilled' ? beliefsRes.value : [],
		issues: issuesRes.status === 'fulfilled' ? issuesRes.value : [],
		axes: axesRes.status === 'fulfilled' ? axesRes.value : [],
		metrics: metricsRes.status === 'fulfilled' ? metricsRes.value : [],
		entities: entitiesRes.status === 'fulfilled' ? entitiesRes.value : []
	};
}
