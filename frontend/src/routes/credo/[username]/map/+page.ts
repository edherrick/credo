import { getMetricAggregate } from '$lib/api';
import type { MetricAggregateResponse } from '$lib/types';

export async function load({ parent, fetch }: { parent: () => Promise<{ credo: { agendas: { metric_id: string | null }[] } }>; fetch: typeof globalThis.fetch }): Promise<{ aggregate: MetricAggregateResponse | null }> {
	const { credo } = await parent();
	const primaryAgenda = credo.agendas.find((a) => a.metric_id);
	if (!primaryAgenda?.metric_id) return { aggregate: null };

	try {
		const aggregate = await getMetricAggregate(primaryAgenda.metric_id, '17', fetch);
		return { aggregate };
	} catch {
		return { aggregate: null };
	}
}
