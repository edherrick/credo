<script lang="ts">
	import MetricMap from '$lib/components/MetricMap.svelte';
	import MetricChart from '$lib/components/MetricChart.svelte';

	let { data } = $props();

	const aggregate = $derived(data.aggregate);
	const credo = $derived(data.credo);

	const primaryAgenda = $derived(credo.agendas.find((a: { metric_id: string | null }) => a.metric_id));
	const metricId = $derived(primaryAgenda?.metric_id ?? null);

	// Zip dates + avg_values into the format MetricMap expects
	const mapValues = $derived(
		aggregate
			? aggregate.dates.map((d: string, i: number) => ({ period_start: d, value: aggregate.avg_values[i] }))
			: []
	);

	let selectedIndex = $state(0);
	// Start at the most-recent date once aggregate loads
	$effect(() => {
		if (aggregate?.dates.length) selectedIndex = aggregate.dates.length - 1;
	});
</script>

<svelte:head>
	<title>{credo.title} · Map · Credo</title>
</svelte:head>

{#if !metricId || !aggregate}
	<section class="empty">
		<p class="empty-msg">No metric data available for this credo's agendas.</p>
	</section>
{:else}
	<div class="map-tab">
		<div class="map-wrap">
			<MetricMap
				{metricId}
				stateFips="17"
				values={mapValues}
				{selectedIndex}
				onchange={(i) => (selectedIndex = i)}
			/>
		</div>
		<div class="chart-wrap">
			<MetricChart
				dates={aggregate.dates}
				avgValues={aggregate.avg_values}
				counties={aggregate.counties}
				{selectedIndex}
				onchange={(i) => (selectedIndex = i)}
			/>
		</div>
	</div>
{/if}

<style>
	.map-tab {
		display: flex;
		flex-direction: column;
		height: calc(100vh - var(--nav-height) - 110px); /* subtract nav + credo header + tab bar */
		min-height: 500px;
	}

	.map-wrap {
		flex: 1;
		min-height: 300px;
		position: relative;
	}

	.chart-wrap {
		height: 220px;
		flex-shrink: 0;
		border-top: 1px solid var(--color-border);
	}

	.empty {
		padding: var(--space-16) var(--space-6);
		text-align: center;
	}

	.empty-msg {
		color: var(--color-text-muted);
		font-size: 0.9rem;
	}
</style>
