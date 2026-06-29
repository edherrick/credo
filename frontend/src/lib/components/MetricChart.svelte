<script lang="ts">
	import type { CountySeries, MetricSeries } from '../types';
	import { compareSeriesColors } from '$lib/theme';

	interface Props {
		dates: string[];
		avgValues: number[];
		counties: CountySeries[];
		compareSeries?: MetricSeries[];
		selectedIndex: number;
		onchange: (index: number) => void;
		hiddenCountyIds?: Set<string>;
	}

	let {
		dates,
		avgValues,
		counties,
		compareSeries = [],
		selectedIndex,
		onchange,
		hiddenCountyIds = new Set()
	}: Props = $props();

	// Internal viewport — independent of any external controller
	// _viewEnd is null until first interaction; falls back to full range
	let viewStart = $state(0);
	let _viewEnd = $state<number | null>(null);
	const viewEnd = $derived(_viewEnd ?? dates.length - 1);

	// Pixel dimensions set by ResizeObserver
	let svgWidth = $state(0);
	let svgHeight = $state(0);
	let svgNode = $state<SVGSVGElement | null>(null);

	const INSET_LEFT = 52;
	const PAD_TOP = 10;
	const PAD_BOTTOM = 30; // extra space for x-axis labels

	const COMPARE_COLORS = compareSeriesColors(); // teal, purple (--cat-teal/--cat-purple)

	const INSET_RIGHT = $derived(compareSeries.length > 0 ? 48 : 16);

	const viewLen = $derived(viewEnd - viewStart + 1);
	const viewDates = $derived(dates.slice(viewStart, viewEnd + 1));
	const viewAvgValues = $derived(avgValues.slice(viewStart, viewEnd + 1));
	const viewCounties = $derived(
		counties
			.filter((c) => !hiddenCountyIds.has(c.id))
			.map((c) => ({ ...c, values: c.values.slice(viewStart, viewEnd + 1) }))
	);

	const trackWidth = $derived(Math.max(0, svgWidth - INSET_LEFT - INSET_RIGHT));

	// Align each compare series to the primary date axis, then slice to view window
	const viewAlignedCompareSeries = $derived(
		compareSeries.map((s) => {
			const lookup = new Map(s.dates.map((d, i) => [d, s.avgValues[i]]));
			const aligned = dates.map((d) => lookup.get(d) ?? null);
			return { ...s, viewValues: aligned.slice(viewStart, viewEnd + 1) };
		})
	);

	const allVals = $derived(
		[
			...viewAvgValues,
			...viewCounties.flatMap((c) => c.values),
			...viewAlignedCompareSeries.flatMap((s) => s.viewValues)
		].filter((v): v is number => v !== null)
	);
	const rawMin = $derived(allVals.length ? Math.min(...allVals) : 0);
	const rawMax = $derived(allVals.length ? Math.max(...allVals) : 1);
	const valueRange = $derived(rawMax - rawMin || 1);
	const minVal = $derived(rawMin - valueRange * 0.05);
	const maxVal = $derived(rawMax + valueRange * 0.05);
	const drawRange = $derived(maxVal - minVal);
	const drawHeight = $derived(Math.max(0, svgHeight - PAD_TOP - PAD_BOTTOM));

	// Index within the current view window
	const localSelectedIndex = $derived(
		selectedIndex >= viewStart && selectedIndex <= viewEnd ? selectedIndex - viewStart : -1
	);

	function dateToX(i: number): number {
		if (viewDates.length <= 1) return INSET_LEFT;
		return INSET_LEFT + (i / (viewDates.length - 1)) * trackWidth;
	}

	function valueToY(v: number): number {
		return PAD_TOP + drawHeight - ((v - minVal) / drawRange) * drawHeight;
	}

	function xToIndex(clientX: number): number {
		if (!svgNode) return viewStart;
		const rect = svgNode.getBoundingClientRect();
		const x = clientX - rect.left - INSET_LEFT;
		const ratio = Math.max(0, Math.min(1, x / trackWidth));
		return viewStart + Math.round(ratio * (viewLen - 1));
	}

	function clampView(start: number, end: number) {
		const len = end - start;
		const s = Math.max(0, Math.min(dates.length - 1 - len, start));
		viewStart = s;
		_viewEnd = s + len;
	}

	function toSegments(values: (number | null)[]): string[] {
		const segments: string[] = [];
		let current: string[] = [];
		for (let i = 0; i < values.length; i++) {
			const v = values[i];
			if (v === null) {
				if (current.length > 1) segments.push(current.join(' '));
				current = [];
			} else {
				current.push(`${dateToX(i)},${valueToY(v)}`);
			}
		}
		if (current.length > 1) segments.push(current.join(' '));
		return segments;
	}

	function formatK(v: number): string {
		return `$${Math.round(v / 1000)}k`;
	}

	function formatYear(d: string): string {
		return new Date(d + 'T00:00:00').getFullYear().toString();
	}

	const yTicks = $derived([
		{ v: rawMin, label: formatK(rawMin) },
		{ v: (rawMin + rawMax) / 2, label: formatK((rawMin + rawMax) / 2) },
		{ v: rawMax, label: formatK(rawMax) }
	]);

	// X-axis tick thinning — show at most ~8 labels
	const labelStep = $derived(Math.max(1, Math.ceil(viewLen / 8)));

	// ── Pointer state ──────────────────────────────────────────────

	let _mode = $state<'idle' | 'cursor' | 'pan'>('idle');
	let _panStartX = 0;
	let _panViewStart = 0;
	let _panViewEnd = 0;
	let _panTotalDelta = 0;
	let _cursorActive = $state(false);

	function onCursorDown(e: PointerEvent) {
		_mode = 'cursor';
		_cursorActive = true;
		(e.currentTarget as SVGElement).setPointerCapture(e.pointerId);
		e.stopPropagation();
	}

	function onCursorMove(e: PointerEvent) {
		if (_mode !== 'cursor') return;
		if (!(e.currentTarget as SVGElement).hasPointerCapture(e.pointerId)) return;
		onchange(xToIndex(e.clientX));
	}

	function onCursorUp(e: PointerEvent) {
		if (_mode !== 'cursor') return;
		onchange(xToIndex(e.clientX));
		_mode = 'idle';
		_cursorActive = false;
	}

	function onChartDown(e: PointerEvent) {
		if (_mode !== 'idle') return;
		_mode = 'pan';
		_panStartX = e.clientX;
		_panViewStart = viewStart;
		_panViewEnd = viewEnd;
		_panTotalDelta = 0;
		(e.currentTarget as SVGElement).setPointerCapture(e.pointerId);
	}

	function onChartMove(e: PointerEvent) {
		if (_mode !== 'pan') return;
		if (!(e.currentTarget as SVGElement).hasPointerCapture(e.pointerId)) return;
		const deltaX = e.clientX - _panStartX;
		const indexDelta = -Math.round((deltaX / trackWidth) * (viewLen - 1));
		if (indexDelta !== 0) _panTotalDelta += Math.abs(indexDelta);
		clampView(_panViewStart + indexDelta, _panViewEnd + indexDelta);
	}

	function onChartUp(e: PointerEvent) {
		if (_mode !== 'pan') return;
		const wasPan = _panTotalDelta > 1;
		_mode = 'idle';
		if (!wasPan) {
			// treat as click-to-seek
			onchange(xToIndex(e.clientX));
		}
	}

	function onWheel(e: WheelEvent) {
		e.preventDefault();
		if (!svgNode) return;
		const rect = svgNode.getBoundingClientRect();
		const mouseRatio = Math.max(0, Math.min(1, (e.clientX - rect.left - INSET_LEFT) / trackWidth));

		const currentLen = viewEnd - viewStart;
		const newLen =
			e.deltaY < 0
				? Math.max(3, Math.floor(currentLen / 1.5))
				: Math.min(dates.length - 1, Math.ceil(currentLen * 1.5));

		const anchor = viewStart + Math.round(mouseRatio * currentLen);
		const newStart = Math.round(anchor - mouseRatio * newLen);
		clampView(newStart, newStart + newLen);
	}

	function chartAttachment(node: HTMLDivElement) {
		const ro = new ResizeObserver((entries) => {
			const entry = entries[0];
			svgWidth = entry.contentRect.width;
			svgHeight = entry.contentRect.height;
		});
		ro.observe(node);
		return () => ro.disconnect();
	}
</script>

<div
	class="chart-wrap"
	class:panning={_mode === 'pan'}
	class:cursor-drag={_cursorActive}
	{@attach chartAttachment}
>
	{#if svgWidth > 0 && viewDates.length > 1}
		<svg
			bind:this={svgNode}
			width={svgWidth}
			height={svgHeight}
			onpointerdown={onChartDown}
			onpointermove={onChartMove}
			onpointerup={onChartUp}
			onwheel={onWheel}
			role="img"
			aria-label="Metric chart"
		>
			<!-- Grid: horizontal lines at Y-tick positions -->
			{#each yTicks as tick (tick.v)}
				<line
					x1={INSET_LEFT}
					y1={valueToY(tick.v)}
					x2={svgWidth - INSET_RIGHT}
					y2={valueToY(tick.v)}
					stroke="var(--color-border)"
					stroke-width="1"
					stroke-dasharray="3 4"
					opacity="0.6"
					pointer-events="none"
				/>
			{/each}

			<!-- Grid: vertical lines at label step positions -->
			{#each viewDates as _d, i (viewStart + i)}
				{#if i % labelStep === 0}
					<line
						x1={dateToX(i)}
						y1={PAD_TOP}
						x2={dateToX(i)}
						y2={svgHeight - PAD_BOTTOM}
						stroke="var(--color-border)"
						stroke-width="1"
						stroke-dasharray="3 4"
						opacity="0.4"
						pointer-events="none"
					/>
				{/if}
			{/each}

			<!-- County lines (faint — behind avg line) -->
			{#each viewCounties as county (county.id)}
				{#each toSegments(county.values) as seg, si (`${county.id}-${si}`)}
					<polyline
						points={seg}
						fill="none"
						stroke="var(--color-border-strong)"
						stroke-width="1"
						opacity="0.22"
					/>
				{/each}
			{/each}

			<!-- Average line (primary metric) -->
			{#each toSegments(viewAvgValues) as seg, si (`avg-${si}`)}
				<polyline
					points={seg}
					fill="none"
					stroke="var(--color-accent)"
					stroke-width="2.5"
					stroke-linejoin="round"
					stroke-linecap="round"
				/>
			{/each}

			<!-- Compare series overlay lines -->
			{#each viewAlignedCompareSeries as series, ci (series.metricId)}
				{@const color = COMPARE_COLORS[ci % COMPARE_COLORS.length]}
				{#each toSegments(series.viewValues) as seg, si (`cmp-${ci}-${si}`)}
					<polyline
						points={seg}
						fill="none"
						stroke={color}
						stroke-width="2"
						stroke-linejoin="round"
						stroke-linecap="round"
						opacity="0.85"
					/>
				{/each}
				<!-- Right-edge label -->
				{#if svgHeight > 0}
					{@const lastVal = [...series.viewValues].reverse().find((v) => v !== null)}
					{#if lastVal !== undefined}
						<text
							x={svgWidth - INSET_RIGHT + 4}
							y={valueToY(lastVal)}
							font-size="0.55rem"
							fill={color}
							dominant-baseline="middle"
							pointer-events="none">{series.label.split(' ').slice(0, 2).join(' ')}</text
						>
					{/if}
				{/if}
			{/each}

			<!-- Cursor vertical line + draggable hit area -->
			{#if localSelectedIndex >= 0}
				{@const cx = dateToX(localSelectedIndex)}
				<line
					x1={cx}
					y1={PAD_TOP}
					x2={cx}
					y2={svgHeight - PAD_BOTTOM}
					stroke="var(--color-accent)"
					stroke-width="1.5"
					stroke-dasharray="3 3"
					opacity="0.7"
					pointer-events="none"
				/>
				<!-- Wide invisible hit area for dragging -->
				<rect
					x={cx - 8}
					y={PAD_TOP}
					width={16}
					height={svgHeight - PAD_TOP - PAD_BOTTOM}
					fill="transparent"
					style="cursor: ew-resize;"
					role="presentation"
					onpointerdown={onCursorDown}
					onpointermove={onCursorMove}
					onpointerup={onCursorUp}
				/>
				<!-- Cursor handle dot -->
				<circle {cx} cy={PAD_TOP + 4} r={4} fill="var(--color-accent)" pointer-events="none" />
			{/if}

			<!-- Y-axis labels -->
			{#each yTicks as tick (tick.v)}
				<text x={INSET_LEFT - 6} y={valueToY(tick.v) + 4} text-anchor="end" class="y-label"
					>{tick.label}</text
				>
			{/each}

			<!-- Section label -->
			{#if svgHeight > 0}
				<text
					x={7}
					y={svgHeight / 2}
					transform="rotate(-90, 7, {svgHeight / 2})"
					text-anchor="middle"
					class="chart-gutter-label">{compareSeries.length > 0 ? 'Comparison' : 'Metro Avg.'}</text
				>
			{/if}

			<!-- X-axis date labels -->
			{#each viewDates as d, i (viewStart + i)}
				{#if i % labelStep === 0}
					<text
						x={dateToX(i)}
						y={svgHeight - 6}
						text-anchor="middle"
						class="x-label"
						class:x-label-active={viewStart + i === selectedIndex}>{formatYear(d)}</text
					>
				{/if}
			{/each}

			<!-- X-axis baseline -->
			<line
				x1={INSET_LEFT}
				y1={svgHeight - PAD_BOTTOM}
				x2={svgWidth - INSET_RIGHT}
				y2={svgHeight - PAD_BOTTOM}
				stroke="var(--color-border)"
				stroke-width="1"
			/>
		</svg>
	{/if}
</div>

<style>
	.chart-wrap {
		width: 100%;
		height: 100%;
		cursor: crosshair;
		user-select: none;
	}

	.chart-wrap.panning {
		cursor: grabbing;
	}

	.chart-wrap.cursor-drag {
		cursor: ew-resize;
	}

	svg {
		display: block;
	}

	.y-label {
		font-size: 0.6rem;
		fill: var(--color-text-faint);
		font-family: inherit;
	}

	.x-label {
		font-size: 0.6rem;
		fill: var(--color-text-faint);
		font-family: inherit;
		pointer-events: none;
	}

	.x-label-active {
		fill: var(--color-accent);
		font-weight: 700;
	}

	.chart-gutter-label {
		font-size: 0.55rem;
		font-weight: 700;
		letter-spacing: 0.1em;
		text-transform: uppercase;
		fill: var(--color-text-faint);
		font-family: inherit;
	}
</style>
