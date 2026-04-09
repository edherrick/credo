<script lang="ts">
	import { legislativeEvents } from '../data/legislativeEvents';
	import type { LegislativeEvent } from '../data/legislativeEvents';

	interface Props {
		dates: string[]; // full date array — used as the initial axis range
	}

	let { dates }: Props = $props();

	// Internal independent viewport
	let viewStart = $state(0);
	let _viewEnd = $state<number | null>(null);
	const viewEnd = $derived(_viewEnd ?? dates.length - 1);

	let trackNode = $state<HTMLDivElement | null>(null);
	let activeEventId = $state<string | null>(null);

	const startMs = $derived(
		dates.length ? new Date(dates[viewStart] + 'T00:00:00').getTime() : 0
	);
	const endMs = $derived(
		dates.length ? new Date(dates[viewEnd] + 'T00:00:00').getTime() : 1
	);

	function dateToPercent(isoDate: string): number {
		const ms = new Date(isoDate + 'T00:00:00').getTime();
		const ratio = (ms - startMs) / (endMs - startMs);
		return Math.max(0, Math.min(100, ratio * 100));
	}

	const visibleEvents = $derived(
		legislativeEvents.filter((e) => {
			const ms = new Date(e.date + 'T00:00:00').getTime();
			return ms >= startMs && ms <= endMs;
		})
	);

	// Year ticks for the axis
	const axisTicks = $derived((() => {
		if (!dates.length) return [];
		const startYear = new Date(dates[viewStart] + 'T00:00:00').getFullYear();
		const endYear = new Date(dates[viewEnd] + 'T00:00:00').getFullYear();
		const ticks: { date: string; label: string }[] = [];
		for (let y = startYear; y <= endYear; y++) {
			ticks.push({ date: `${y}-01-01`, label: String(y) });
		}
		return ticks;
	})());

	const TYPE_COLORS: Record<LegislativeEvent['type'], string> = {
		bill: 'var(--color-text)',
		rate: 'var(--color-accent)',
		policy: '#0d9488'
	};

	function toggleEvent(id: string) {
		activeEventId = activeEventId === id ? null : id;
	}

	function onWindowClick(e: MouseEvent) {
		if (activeEventId && !(e.target as HTMLElement).closest('.event-pin')) {
			activeEventId = null;
		}
	}

	// ── Pan ────────────────────────────────────────────────────────

	let _panStartX = $state<number | null>(null);
	let _panViewStart = 0;
	let _panViewEnd = 0;

	function onTrackDown(e: PointerEvent) {
		if ((e.target as HTMLElement).closest('.event-pin')) return;
		_panStartX = e.clientX;
		_panViewStart = viewStart;
		_panViewEnd = viewEnd;
		(e.currentTarget as HTMLElement).setPointerCapture(e.pointerId);
	}

	function onTrackMove(e: PointerEvent) {
		if (_panStartX === null) return;
		if (!(e.currentTarget as HTMLElement).hasPointerCapture(e.pointerId)) return;
		if (!trackNode) return;
		const { width } = trackNode.getBoundingClientRect();
		const viewLen = _panViewEnd - _panViewStart;
		const delta = -Math.round(((e.clientX - _panStartX) / width) * viewLen);
		const s = Math.max(0, Math.min(dates.length - 1 - viewLen, _panViewStart + delta));
		viewStart = s;
		_viewEnd = s + viewLen;
	}

	function onTrackUp() {
		_panStartX = null;
	}

	// ── Zoom ───────────────────────────────────────────────────────

	function onWheel(e: WheelEvent) {
		e.preventDefault();
		if (!trackNode) return;
		const { left, width } = trackNode.getBoundingClientRect();
		const mouseRatio = Math.max(0, Math.min(1, (e.clientX - left) / width));
		const currentLen = viewEnd - viewStart;
		const newLen = e.deltaY < 0
			? Math.max(2, Math.floor(currentLen / 1.5))
			: Math.min(dates.length - 1, Math.ceil(currentLen * 1.5));
		const anchor = viewStart + Math.round(mouseRatio * currentLen);
		const newStart = Math.max(0, Math.min(dates.length - 1 - newLen, Math.round(anchor - mouseRatio * newLen)));
		viewStart = newStart;
		_viewEnd = newStart + newLen;
	}

	function trackAttachment(node: HTMLDivElement) {
		trackNode = node;
		return () => { trackNode = null; };
	}
</script>

<svelte:window onclick={onWindowClick} />

<div class="events-track">
	<div class="events-gutter-label">Events</div>
	<div
		class="track-inner"
		class:panning={_panStartX !== null}
		{@attach trackAttachment}
		onpointerdown={onTrackDown}
		onpointermove={onTrackMove}
		onpointerup={onTrackUp}
		onwheel={onWheel}
		role="presentation"
	>
		<!-- Axis baseline -->
		<div class="axis-line"></div>

		<!-- Year tick marks + labels -->
		{#each axisTicks as tick (tick.label)}
			<div class="axis-tick" style="left: {dateToPercent(tick.date)}%">
				<div class="tick-mark"></div>
				<div class="tick-label">{tick.label}</div>
			</div>
		{/each}

		<!-- Event pins -->
		{#each visibleEvents as event (event.id)}
			<button
				class="event-pin"
				class:active={activeEventId === event.id}
				style="left: {dateToPercent(event.date)}%; --pin-color: {TYPE_COLORS[event.type]}"
				onclick={() => toggleEvent(event.id)}
				title={event.title}
				aria-label={event.title}
				aria-expanded={activeEventId === event.id}
			>
				<div class="pin-stem"></div>
				<div class="pin-dot"></div>

				{#if activeEventId === event.id}
					<div class="popover">
						<div class="popover-type">{event.type}</div>
						<div class="popover-title">{event.title}</div>
						<div class="popover-desc">{event.description}</div>
						<div class="popover-date">{new Date(event.date + 'T00:00:00').toLocaleDateString('en-US', { year: 'numeric', month: 'short' })}</div>
					</div>
				{/if}
			</button>
		{/each}
	</div>
</div>

<style>
	.events-track {
		width: 100%;
		height: 100%;
		min-height: 60px;
		position: relative;
	}

	.events-gutter-label {
		position: absolute;
		left: 0;
		top: 8px;
		width: var(--track-inset-left, 52px);
		padding-right: 6px;
		text-align: right;
		font-size: 0.55rem;
		font-weight: 700;
		letter-spacing: 0.1em;
		text-transform: uppercase;
		color: var(--color-text-faint);
		pointer-events: none;
	}

	.track-inner {
		position: absolute;
		top: 0;
		bottom: 0;
		left: var(--track-inset-left, 52px);
		right: var(--track-inset-right, 16px);
		cursor: grab;
		overflow: hidden;
	}

	.track-inner.panning {
		cursor: grabbing;
	}

	/* ── Axis ─────────────────────────────────────────────────── */
	.axis-line {
		position: absolute;
		left: 0;
		right: 0;
		bottom: 20px;
		height: 1px;
		background: var(--color-border-strong);
		pointer-events: none;
	}

	.axis-tick {
		position: absolute;
		bottom: 20px;
		transform: translateX(-50%);
		display: flex;
		flex-direction: column;
		align-items: center;
		pointer-events: none;
	}

	.tick-mark {
		width: 1px;
		height: 4px;
		background: var(--color-border-strong);
	}

	.tick-label {
		font-size: 0.6rem;
		color: var(--color-text-faint);
		margin-top: 2px;
		white-space: nowrap;
	}

	.event-pin {
		position: absolute;
		bottom: 21px;
		transform: translateX(-50%);
		display: flex;
		flex-direction: column;
		align-items: center;
		background: none;
		border: none;
		padding: 0;
		cursor: pointer;
		z-index: 10;
	}

	.pin-stem {
		width: 1.5px;
		height: 14px;
		background: var(--pin-color);
		opacity: 0.7;
	}

	.pin-dot {
		width: 7px;
		height: 7px;
		border-radius: 50%;
		background: var(--pin-color);
		margin-top: 2px;
		transition: transform var(--transition-fast);
	}

	.event-pin:hover .pin-dot,
	.event-pin.active .pin-dot {
		transform: scale(1.4);
	}

	.event-pin:hover .pin-stem,
	.event-pin.active .pin-stem {
		opacity: 1;
	}

	.popover {
		position: absolute;
		bottom: calc(100% + 6px);
		left: 50%;
		transform: translateX(-50%);
		background: var(--color-surface);
		border: 1px solid var(--color-border-strong);
		border-radius: 8px;
		padding: 0.6rem 0.8rem;
		box-shadow: var(--shadow-lg);
		min-width: 200px;
		max-width: 260px;
		text-align: left;
		z-index: 50;
		pointer-events: none;
	}

	.popover-type {
		font-size: 0.6rem;
		font-weight: 700;
		letter-spacing: 0.1em;
		text-transform: uppercase;
		color: var(--pin-color);
		margin-bottom: 0.2rem;
	}

	.popover-title {
		font-size: 0.8rem;
		font-weight: 600;
		color: var(--color-text);
		margin-bottom: 0.3rem;
		line-height: 1.3;
	}

	.popover-desc {
		font-size: 0.72rem;
		color: var(--color-text-muted);
		line-height: 1.4;
		margin-bottom: 0.3rem;
	}

	.popover-date {
		font-size: 0.65rem;
		color: var(--color-text-faint);
	}
</style>
