import { getMetricValues, getMetricAggregate, getMetrics } from '$lib/api';
import type { MetricAggregateResponse } from '$lib/types';

export const ssr = false;

export async function load({
	params,
	url,
	fetch
}: {
	params: { id: string };
	url: URL;
	fetch: typeof globalThis.fetch;
}) {
	const metricId = params.id;
	const fips = url.searchParams.get('fips') ?? '17031';

	const [seriesResult, aggregateResult, metricsResult] = await Promise.allSettled([
		getMetricValues(fips, metricId, undefined, fetch),
		getMetricAggregate(metricId, '17', fetch),
		getMetrics(fetch)
	]);

	const allValues = seriesResult.status === 'fulfilled' ? seriesResult.value.values : [];

	const aggregateData: MetricAggregateResponse | null =
		aggregateResult.status === 'fulfilled' ? aggregateResult.value : null;

	const metrics = metricsResult.status === 'fulfilled' ? metricsResult.value : [];

	const compareIds = (url.searchParams.get('compare') ?? '').split(',').filter(Boolean).slice(0, 2);

	return { metricId, allValues, aggregateData, metrics, compareIds };
}
