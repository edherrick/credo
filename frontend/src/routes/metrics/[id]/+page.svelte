<script lang="ts">
	import { resolve } from '$app/paths';
	import { goto } from '$app/navigation';
	import { ArrowLeft, ChevronDown, PanelRight, Map as MapIcon } from 'lucide-svelte';
	import { SvelteSet, SvelteMap } from 'svelte/reactivity';
	import { untrack } from 'svelte';
	import { getMetricAggregate } from '$lib/api';
	import type { MetricSeries } from '$lib/types';
	import MetricMap from '$lib/components/MetricMap.svelte';
	import MetricChart from '$lib/components/MetricChart.svelte';
	import EventsTrack from '$lib/components/EventsTrack.svelte';
	import MetricPanel from '$lib/components/MetricPanel.svelte';

	let { data } = $props();

	const allValues = $derived(data.allValues);
	const aggregateData = $derived(data.aggregateData);
	const metrics = $derived(data.metrics ?? []);
	const metricId = $derived(data.metricId);
	const metricName = $derived(metrics.find((m) => m.id === metricId)?.display_name ?? 'Metric');

	// ── Map collapse ─────────────────────────────────────────────
	let mapCollapsed = $state(false);

	// ── Selected index ───────────────────────────────────────────
	let selectedIndexOverride = $state<number | null>(null);
	const selectedIndex = $derived(selectedIndexOverride ?? Math.max(0, allValues.length - 1));

	// ── Panel collapse / resize ──────────────────────────────────
	// Chart panel: uses CSS flex:1 to fill available panels area — no fixed height needed.
	// Events panel: fixed height at the bottom; between-panel handle adjusts it only.
	let chartCollapsed = $state(false);
	let panelEvents = $state({ collapsed: false, height: 68 }); // 28px header + 40px track

	const EVENTS_MIN = 50; // minimum events panel height

	let _resizeDragStartY = 0;
	let _resizeDragStartH = 0;

	function onResizeDown(e: PointerEvent) {
		(e.currentTarget as HTMLElement).setPointerCapture(e.pointerId);
		e.stopPropagation();
		_resizeDragStartY = e.clientY;
		_resizeDragStartH = panelEvents.height;
	}

	function onResizeMove(e: PointerEvent) {
		if (!(e.currentTarget as HTMLElement).hasPointerCapture(e.pointerId)) return;
		// Drag up = handle moves up = events panel grows (its top moves up)
		const delta = _resizeDragStartY - e.clientY;
		panelEvents.height = Math.max(EVENTS_MIN, _resizeDragStartH + delta);
	}

	// ── Map/panels split drag handle ────────────────────────────
	let panelsAreaHeight = $state<number | null>(null);
	let _splitDragStartY = 0;
	let _splitDragStartPanelsH = 0;

	function onSplitDown(e: PointerEvent) {
		(e.currentTarget as HTMLElement).setPointerCapture(e.pointerId);
		_splitDragStartY = e.clientY;
		_splitDragStartPanelsH =
			panelsAreaHeight ?? (e.currentTarget as HTMLElement).parentElement!.offsetHeight;
		e.stopPropagation();
	}

	function onSplitMove(e: PointerEvent) {
		if (!(e.currentTarget as HTMLElement).hasPointerCapture(e.pointerId)) return;
		// Clamp: panels can't grow past (page height − header − min map height)
		const panelsEl = (e.currentTarget as HTMLElement).parentElement!;
		const pageEl = panelsEl.parentElement!;
		const headerEl = pageEl.querySelector('.map-header') as HTMLElement | null;
		const headerH = headerEl?.offsetHeight ?? 70;
		const maxPanels = pageEl.offsetHeight - headerH - 120; // 120 = MAP_MIN_HEIGHT
		const delta = _splitDragStartY - e.clientY; // drag up = more panel height
		panelsAreaHeight = Math.max(60, Math.min(maxPanels, _splitDragStartPanelsH + delta));
	}

	// ── Compare metrics ──────────────────────────────────────────
	const MAX_COMPARE = 2;
	// Read compare IDs from load data once (URL param ?compare=); state manages from here
	let compareMetricIds = $state<string[]>(untrack(() => data.compareIds ?? []));
	const compareSeriesMap = new SvelteMap<string, MetricSeries>();

	$effect(() => {
		const ids = [...compareMetricIds];
		for (const id of ids) {
			if (!compareSeriesMap.has(id)) {
				getMetricAggregate(id, '17')
					.then((res) => {
						compareSeriesMap.set(id, {
							metricId: res.metric_id,
							label: metrics.find((m) => m.id === id)?.display_name ?? id,
							dates: res.dates,
							avgValues: res.avg_values
						});
					})
					.catch(() => {});
			}
		}
		for (const id of compareSeriesMap.keys()) {
			if (!ids.includes(id)) compareSeriesMap.delete(id);
		}
	});

	$effect(() => {
		// Sync compareMetricIds to URL without triggering a load fn re-run
		const compare = compareMetricIds.join(',');
		const search = compare ? `?compare=${compare}` : '';
		history.replaceState({}, '', `${location.pathname}${search}`);
	});

	function toggleCompare(id: string) {
		const idx = compareMetricIds.indexOf(id);
		if (idx >= 0) compareMetricIds = compareMetricIds.filter((x) => x !== id);
		else if (compareMetricIds.length < MAX_COMPARE) compareMetricIds = [...compareMetricIds, id];
	}

	// ── Metric side panel ────────────────────────────────────────
	let metricPanelOpen = $state(false);
	const hiddenCountyIds = new SvelteSet<string>();

	function toggleCounty(id: string) {
		if (hiddenCountyIds.has(id)) hiddenCountyIds.delete(id);
		else hiddenCountyIds.add(id);
	}
</script>

<svelte:head>
	<title>{metricName} · Credo</title>
</svelte:head>

<div class="map-page">
	<div class="map-header">
		<div>
			<h1 class="map-title">{metricName}</h1>
			<p class="map-sub">Chicago Metro Area · 7 counties · Illinois</p>
		</div>
		<div class="header-actions">
			<button
				class="panel-toggle-btn"
				class:active={mapCollapsed}
				onclick={() => (mapCollapsed = !mapCollapsed)}
				aria-label={mapCollapsed ? 'Expand map' : 'Collapse map'}
				title={mapCollapsed ? 'Show map' : 'Hide map'}
			>
				<MapIcon size={14} aria-hidden="true" />
			</button>
			<button
				class="panel-toggle-btn"
				class:active={metricPanelOpen}
				onclick={() => (metricPanelOpen = !metricPanelOpen)}
				aria-label={metricPanelOpen ? 'Close metrics panel' : 'Open metrics panel'}
				aria-expanded={metricPanelOpen}
				title="Metrics & layers"
			>
				<PanelRight size={14} aria-hidden="true" />
			</button>
			<a href={resolve('/metrics')} class="back-link">
				<ArrowLeft size={14} aria-hidden="true" /> All metrics
			</a>
		</div>
	</div>

	<div class="map-body" class:collapsed={mapCollapsed}>
		<div class="map-content">
			<MetricMap
				stateFips="17"
				{metricId}
				values={allValues}
				{selectedIndex}
				collapsed={mapCollapsed}
				onchange={(i) => (selectedIndexOverride = i)}
			/>
		</div>
		{#if metricPanelOpen}
			<MetricPanel
				{metrics}
				selectedMetricId={metricId}
				{compareMetricIds}
				counties={aggregateData?.counties ?? []}
				{hiddenCountyIds}
				onSelectMetric={(id) => goto(resolve(`/metrics/${id}`))}
				onToggleCounty={toggleCounty}
				onToggleCompare={toggleCompare}
			/>
		{/if}
	</div>

	<!-- Stacked temporal panels — all share the same X-axis -->
	{#if allValues.length > 1}
		<div class="panels-below" style={panelsAreaHeight ? `height: ${panelsAreaHeight}px` : ''}>
			<!-- Split handle — drag to resize map vs panels area -->
			<div
				class="split-handle"
				onpointerdown={onSplitDown}
				onpointermove={onSplitMove}
				onpointerup={() => {}}
				role="separator"
				aria-orientation="horizontal"
				aria-label="Resize map vs panels"
			></div>

			<!-- MetricChart panel — flex:1, fills all space above events -->
			<div class="panel-row chart-panel" class:chart-collapsed={chartCollapsed}>
				<div class="panel-header">
					<span class="panel-label">Trend</span>
					<button
						class="collapse-btn"
						class:expanded={!chartCollapsed}
						onclick={() => (chartCollapsed = !chartCollapsed)}
						aria-label={chartCollapsed ? 'Expand chart' : 'Collapse chart'}
					>
						<ChevronDown size={12} aria-hidden="true" />
					</button>
				</div>
				{#if !chartCollapsed}
					<div class="panel-content">
						{#if aggregateData && aggregateData.dates.length > 1}
							<MetricChart
								dates={aggregateData.dates}
								avgValues={aggregateData.avg_values}
								counties={aggregateData.counties}
								compareSeries={[...compareSeriesMap.values()]}
								{selectedIndex}
								onchange={(i) => (selectedIndexOverride = i)}
								{hiddenCountyIds}
							/>
						{/if}
					</div>
				{/if}
			</div>

			<!-- Separator — drag to resize events panel below -->
			<div
				class="resize-handle"
				onpointerdown={onResizeDown}
				onpointermove={onResizeMove}
				onpointerup={() => {}}
				role="separator"
				aria-orientation="horizontal"
				aria-label="Resize events panel"
			></div>

			<!-- EventsTrack panel — fixed height at bottom -->
			<div class="panel-row" style="height: {panelEvents.collapsed ? 28 : panelEvents.height}px">
				<div class="panel-header">
					<span class="panel-label">Events</span>
					<button
						class="collapse-btn"
						class:expanded={!panelEvents.collapsed}
						onclick={() => (panelEvents.collapsed = !panelEvents.collapsed)}
						aria-label={panelEvents.collapsed ? 'Expand events' : 'Collapse events'}
					>
						<ChevronDown size={12} aria-hidden="true" />
					</button>
				</div>
				{#if !panelEvents.collapsed}
					<div class="panel-content">
						<EventsTrack dates={allValues.map((v) => v.period_start)} />
					</div>
				{/if}
			</div>
		</div>
	{/if}
</div>

<style>
	.map-page {
		display: flex;
		flex-direction: column;
		height: calc(100vh - 56px);
		overflow: hidden;
	}

	/* ── Header ──────────────────────────────────────────────────── */
	.map-header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 1rem 1.5rem;
		background: var(--color-surface);
		border-bottom: 1px solid var(--color-border);
		flex-shrink: 0;
	}

	.map-title {
		font-family: var(--font-serif);
		font-size: 1.25rem;
		font-weight: 400;
		color: var(--color-text);
	}

	.map-sub {
		font-size: 0.8rem;
		color: var(--color-text-faint);
		margin-top: 0.1rem;
	}

	.header-actions {
		display: flex;
		align-items: center;
		gap: 0.75rem;
	}

	.back-link {
		display: inline-flex;
		align-items: center;
		gap: 0.3rem;
		font-size: 0.85rem;
		font-weight: 500;
		color: var(--color-text-muted);
		transition: color var(--transition-fast);
	}

	.back-link:hover {
		color: var(--color-text);
	}

	.panel-toggle-btn {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		width: 30px;
		height: 30px;
		border-radius: var(--radius-md);
		border: 1px solid var(--color-border);
		background: var(--color-bg);
		color: var(--color-text-muted);
		cursor: pointer;
		transition:
			background var(--transition-fast),
			border-color var(--transition-fast),
			color var(--transition-fast);
	}

	.panel-toggle-btn:hover {
		border-color: var(--color-accent);
		color: var(--color-accent);
	}

	.panel-toggle-btn.active {
		background: var(--color-accent);
		border-color: var(--color-accent);
		color: white;
	}

	/* ── Map body ─────────────────────────────────────────────────── */
	.map-body {
		flex: 1;
		display: flex;
		flex-direction: row;
		min-height: 120px;
		overflow: hidden;
		transition:
			min-height var(--transition-base),
			flex var(--transition-base);
	}

	.map-body.collapsed {
		flex: 0;
		min-height: 0;
		overflow: hidden;
	}

	.map-content {
		flex: 1;
		min-width: 0;
		padding: 1rem 1.5rem;
		background: var(--color-bg);
		overflow: hidden;
	}

	.map-content :global(.map-wrap) {
		height: 100%;
		border-radius: 10px;
	}

	.map-content :global(.map) {
		height: 100%;
	}

	/* ── Stacked temporal panels ─────────────────────────────────── */
	.panels-below {
		--track-inset-left: 52px;
		--track-inset-right: 16px;
		flex-shrink: 0;
		background: var(--color-surface);
		display: flex;
		flex-direction: column;
		overflow: hidden;
	}

	/* ── Split handle (map vs panels) ────────────────────────────── */
	.split-handle {
		height: 7px;
		cursor: ns-resize;
		flex-shrink: 0;
		background: transparent;
		border-top: 3px solid var(--color-accent);
		transition: background var(--transition-fast);
	}

	.split-handle:hover {
		background: color-mix(in srgb, var(--color-accent) 20%, transparent);
	}

	.panel-row {
		overflow: hidden;
		border-bottom: 1px solid var(--color-border);
		display: flex;
		flex-direction: column;
		flex-shrink: 0;
	}

	/* Chart panel fills all remaining space in panels-below */
	.chart-panel {
		flex: 1;
		min-height: 28px;
	}

	/* When chart is collapsed, shrink back to header height */
	.chart-panel.chart-collapsed {
		flex: 0 0 28px;
	}

	.panel-header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 0 1rem 0 1.25rem;
		height: 28px;
		flex-shrink: 0;
		background: var(--color-bg);
		border-bottom: 1px solid var(--color-border);
	}

	.panel-label {
		font-size: 0.6rem;
		font-weight: 700;
		letter-spacing: 0.12em;
		text-transform: uppercase;
		color: var(--color-accent);
	}

	.collapse-btn {
		display: flex;
		align-items: center;
		justify-content: center;
		width: 20px;
		height: 20px;
		border: none;
		background: none;
		color: var(--color-text-faint);
		cursor: pointer;
		border-radius: var(--radius-sm);
		transition:
			color var(--transition-fast),
			background var(--transition-fast);
	}

	.collapse-btn:hover {
		color: var(--color-text-muted);
		background: var(--color-border);
	}

	.collapse-btn :global(svg) {
		transition: transform var(--transition-fast);
	}

	.collapse-btn.expanded :global(svg) {
		transform: rotate(180deg);
	}

	.panel-content {
		flex: 1;
		min-height: 0;
		overflow: hidden;
	}

	/* ── Resize handle ────────────────────────────────────────────── */
	.resize-handle {
		height: 5px;
		cursor: ns-resize;
		flex-shrink: 0;
		background: transparent;
		transition: background var(--transition-fast);
	}

	.resize-handle:hover {
		background: var(--color-accent);
		opacity: 0.3;
	}
</style>
