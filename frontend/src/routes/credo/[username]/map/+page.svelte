<script lang="ts">
	import MetricMap from '$lib/components/MetricMap.svelte';
	import MetricChart from '$lib/components/MetricChart.svelte';

	let { data } = $props();

	const aggregate = $derived(data.aggregate);
	const credo = $derived(data.credo);

	const primaryAgenda = $derived(
		credo.agendas.find((a: { metric_id: string | null }) => a.metric_id)
	);
	const metricId = $derived(primaryAgenda?.metric_id ?? null);

	// Zip dates + avg_values into the format MetricMap expects
	const mapValues = $derived(
		aggregate
			? aggregate.dates.map((d: string, i: number) => ({
					period_start: d,
					value: aggregate.avg_values[i]
				}))
			: []
	);

	let selectedIndex = $state(0);
	// Start at the most-recent date once aggregate loads
	$effect(() => {
		if (aggregate?.dates.length) selectedIndex = aggregate.dates.length - 1;
	});

	// ── Resizable map / chart split ──────────────────────────
	const CHART_MIN = 160; // keeps room for the chart's x-axis labels
	const MAP_MIN = 200;

	let tabEl = $state<HTMLDivElement | null>(null);
	let chartHeight = $state(260);
	let dragging = $state(false);

	function clampChart(px: number): number {
		const max = tabEl ? tabEl.getBoundingClientRect().height - MAP_MIN : px;
		return Math.max(CHART_MIN, Math.min(max, px));
	}

	function onSplitterDown(e: PointerEvent) {
		dragging = true;
		(e.currentTarget as HTMLElement).setPointerCapture(e.pointerId);
		e.preventDefault();
	}

	function onSplitterMove(e: PointerEvent) {
		if (!dragging || !tabEl) return;
		// Distance from the pointer to the bottom of the tab = desired chart height.
		chartHeight = clampChart(tabEl.getBoundingClientRect().bottom - e.clientY);
	}

	function onSplitterUp() {
		dragging = false;
	}

	function onSplitterKey(e: KeyboardEvent) {
		const step = e.shiftKey ? 40 : 12;
		if (e.key === 'ArrowUp') {
			chartHeight = clampChart(chartHeight + step);
			e.preventDefault();
		} else if (e.key === 'ArrowDown') {
			chartHeight = clampChart(chartHeight - step);
			e.preventDefault();
		}
	}
</script>

<svelte:head>
	<title>{credo.title} · Map · Credo</title>
</svelte:head>

{#if !metricId || !aggregate}
	<section class="empty">
		<p class="empty-msg">No metric data available for this credo's agendas.</p>
	</section>
{:else}
	<div class="map-tab" bind:this={tabEl}>
		<div class="map-wrap">
			<MetricMap {metricId} stateFips="17" values={mapValues} {selectedIndex} />
		</div>

		<!-- Interactive splitter (WAI-ARIA window-splitter pattern); the a11y rules
		     below misclassify a focusable role="separator" as non-interactive. -->
		<!-- svelte-ignore a11y_no_noninteractive_tabindex -->
		<!-- svelte-ignore a11y_no_noninteractive_element_interactions -->
		<div
			class="splitter"
			class:dragging
			role="separator"
			aria-orientation="horizontal"
			aria-label="Resize map and chart"
			aria-valuenow={Math.round(chartHeight)}
			aria-valuemin={CHART_MIN}
			tabindex="0"
			onpointerdown={onSplitterDown}
			onpointermove={onSplitterMove}
			onpointerup={onSplitterUp}
			onkeydown={onSplitterKey}
		></div>

		<div class="chart-pane" style="height: {chartHeight}px">
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
		height: 100%;
		min-height: 0;
		display: flex;
		flex-direction: column;
	}

	.map-wrap {
		flex: 1;
		min-height: 200px;
		position: relative;
	}

	.splitter {
		flex-shrink: 0;
		height: 9px;
		cursor: row-resize;
		background: var(--color-surface);
		border-top: 1px solid var(--color-border);
		border-bottom: 1px solid var(--color-border);
		position: relative;
		transition: background var(--transition-fast);
	}

	/* Centre grip */
	.splitter::after {
		content: '';
		position: absolute;
		left: 50%;
		top: 50%;
		transform: translate(-50%, -50%);
		width: 32px;
		height: 2px;
		border-radius: 1px;
		background: var(--color-text-faint);
		opacity: 0.5;
		transition:
			background var(--transition-fast),
			opacity var(--transition-fast);
	}

	.splitter:hover,
	.splitter:focus-visible,
	.splitter.dragging {
		background: var(--color-accent);
		outline: none;
	}

	.splitter:hover::after,
	.splitter:focus-visible::after,
	.splitter.dragging::after {
		background: white;
		opacity: 0.95;
	}

	.chart-pane {
		flex-shrink: 0;
		min-height: 160px;
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
