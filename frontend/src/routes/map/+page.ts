import { getMetricValues, getMetricAggregate, getMetrics } from '$lib/api';
import type { MetricAggregateResponse } from '$lib/types';

export const ssr = false;

export async function load({ url }: { url: URL }) {
	const metricId = url.searchParams.get('metric') ?? 'median_home_price';
	const fips = url.searchParams.get('fips') ?? '17031';

	const [seriesResult, aggregateResult, metricsResult] = await Promise.allSettled([
		getMetricValues(fips, metricId),
		getMetricAggregate(metricId, '17'),
		getMetrics()
	]);

	const allValues =
		seriesResult.status === 'fulfilled' ? seriesResult.value.values : [];

	const aggregateData: MetricAggregateResponse | null =
		aggregateResult.status === 'fulfilled' ? aggregateResult.value : null;

	const metrics = metricsResult.status === 'fulfilled' ? metricsResult.value : [];

	const compareIds = (url.searchParams.get('compare') ?? '')
		.split(',')
		.filter(Boolean)
		.slice(0, 2);

	return { allValues, aggregateData, metrics, compareIds };
}
