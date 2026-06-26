export const ssr = false;

import { getBeliefs, getIssues, getAxes, getMetrics, getEntities } from '$lib/api';

export async function load({ fetch }: { fetch: typeof globalThis.fetch }) {
	const [beliefs, issues, axes, metrics, entities] = await Promise.allSettled([
		getBeliefs(fetch),
		getIssues(fetch),
		getAxes(fetch),
		getMetrics(fetch),
		getEntities(fetch)
	]);

	const count = (r: PromiseSettledResult<unknown[]>) =>
		r.status === 'fulfilled' ? r.value.length : 0;

	return {
		counts: {
			beliefs: count(beliefs),
			issues: count(issues),
			axes: count(axes),
			metrics: count(metrics),
			entities: count(entities)
		}
	};
}
