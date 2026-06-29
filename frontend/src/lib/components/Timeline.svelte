<script lang="ts">
	import { Play, Pause, ZoomIn, ZoomOut } from 'lucide-svelte';

	interface Props {
		values: { period_start: string; value: number }[];
		selectedIndex: number;
		onchange: (index: number) => void;
		viewStart?: number;
		viewEnd?: number;
		zoomWindowSize?: number | null;
		onzoomin?: () => void;
		onzoomout?: () => void;
		onpan?: (deltaIndex: number) => void;
	}

	let {
		values,
		selectedIndex,
		onchange,
		viewStart = 0,
		viewEnd = values.length - 1,
		zoomWindowSize = null,
		onzoomin,
		onzoomout,
		onpan
	}: Props = $props();

	// playIndex overrides selectedIndex while playing or dragging
	let playIndex = $state<number | null>(null);
	const currentIndex = $derived(playIndex ?? selectedIndex);

	// Range handles — constrained to the visible view window
	let rangeStart = $state(0);
	let rangeEndOverride = $state<number | null>(null);
	const rangeEndRaw = $derived(rangeEndOverride ?? values.length - 1);

	// Clamp range handles so they stay visible within the current view
	const clampedRangeStart = $derived(Math.max(viewStart, Math.min(rangeStart, viewEnd - 1)));
	const clampedRangeEnd = $derived(Math.max(viewStart + 1, Math.min(rangeEndRaw, viewEnd)));

	let isPlaying = $state(false);
	let playTimer: ReturnType<typeof setInterval> | null = null;

	let trackNode: HTMLDivElement | null = null;

	function trackAttachment(node: HTMLDivElement) {
		trackNode = node;
		return () => {
			if (playTimer) {
				clearInterval(playTimer);
				playTimer = null;
			}
			trackNode = null;
		};
	}

	// Convert absolute index to % position within the current view window
	function indexToPercent(i: number): number {
		if (viewEnd === viewStart) return 0;
		return ((i - viewStart) / (viewEnd - viewStart)) * 100;
	}

	// Convert clientX to an absolute index within the view window
	function clientXToIndex(clientX: number): number {
		if (!trackNode) return viewStart;
		const { left, width } = trackNode.getBoundingClientRect();
		const ratio = Math.max(0, Math.min(1, (clientX - left) / width));
		return viewStart + Math.round(ratio * (viewEnd - viewStart));
	}

	function formatYear(d: string): string {
		return new Date(d + 'T00:00:00').getFullYear().toString();
	}

	function formatDate(d: string): string {
		return new Date(d + 'T00:00:00').toLocaleDateString('en-US', {
			year: 'numeric',
			month: 'short'
		});
	}

	// Label thinning — avoid crowding when many ticks are visible
	const labelStep = $derived(Math.max(1, Math.ceil((viewEnd - viewStart + 1) / 10)));

	// Visible slice of values for tick rendering
	const visibleValues = $derived(values.slice(viewStart, viewEnd + 1));

	// ── Playback ──────────────────────────────────────────────────

	function stopPlay() {
		isPlaying = false;
		if (playTimer) {
			clearInterval(playTimer);
			playTimer = null;
		}
	}

	function togglePlay() {
		if (isPlaying) {
			stopPlay();
			return;
		}

		let idx = currentIndex >= clampedRangeEnd ? clampedRangeStart : currentIndex;
		isPlaying = true;
		playIndex = idx;
		onchange(idx);

		playTimer = setInterval(() => {
			idx = idx < clampedRangeEnd ? idx + 1 : clampedRangeStart;
			playIndex = idx;
			onchange(idx);
		}, 900);
	}

	// ── Playhead drag ──────────────────────────────────────────────

	function onPlayheadDown(e: PointerEvent) {
		stopPlay();
		(e.currentTarget as HTMLElement).setPointerCapture(e.pointerId);
		e.stopPropagation();
		playIndex = Math.max(clampedRangeStart, Math.min(clampedRangeEnd, clientXToIndex(e.clientX)));
	}

	function onPlayheadMove(e: PointerEvent) {
		if (!(e.currentTarget as HTMLElement).hasPointerCapture(e.pointerId)) return;
		playIndex = Math.max(clampedRangeStart, Math.min(clampedRangeEnd, clientXToIndex(e.clientX)));
	}

	function onPlayheadUp(e: PointerEvent) {
		const idx = Math.max(clampedRangeStart, Math.min(clampedRangeEnd, clientXToIndex(e.clientX)));
		playIndex = null;
		onchange(idx);
	}

	// ── Range start handle drag ────────────────────────────────────

	function onRangeStartDown(e: PointerEvent) {
		stopPlay();
		(e.currentTarget as HTMLElement).setPointerCapture(e.pointerId);
		e.stopPropagation();
	}

	function onRangeStartMove(e: PointerEvent) {
		if (!(e.currentTarget as HTMLElement).hasPointerCapture(e.pointerId)) return;
		rangeStart = Math.max(viewStart, Math.min(clampedRangeEnd - 1, clientXToIndex(e.clientX)));
	}

	function onRangeStartUp(e: PointerEvent) {
		rangeStart = Math.max(viewStart, Math.min(clampedRangeEnd - 1, clientXToIndex(e.clientX)));
	}

	// ── Range end handle drag ──────────────────────────────────────

	function onRangeEndDown(e: PointerEvent) {
		stopPlay();
		(e.currentTarget as HTMLElement).setPointerCapture(e.pointerId);
		e.stopPropagation();
	}

	function onRangeEndMove(e: PointerEvent) {
		if (!(e.currentTarget as HTMLElement).hasPointerCapture(e.pointerId)) return;
		rangeEndOverride = Math.max(
			clampedRangeStart + 1,
			Math.min(viewEnd, clientXToIndex(e.clientX))
		);
	}

	function onRangeEndUp(e: PointerEvent) {
		rangeEndOverride = Math.max(
			clampedRangeStart + 1,
			Math.min(viewEnd, clientXToIndex(e.clientX))
		);
	}

	// ── Track background: click to seek, drag to pan ───────────────

	let _panStartX = $state<number | null>(null);
	let _panTotalDelta = 0;

	function onTrackPointerDown(e: PointerEvent) {
		const t = e.target as HTMLElement;
		if (t.closest('.range-handle') || t.closest('.playhead')) return;
		if (onpan && zoomWindowSize !== null) {
			// Pan mode when zoomed
			(e.currentTarget as HTMLElement).setPointerCapture(e.pointerId);
			_panStartX = e.clientX;
			_panTotalDelta = 0;
		}
	}

	function onTrackPointerMove(e: PointerEvent) {
		if (_panStartX === null) return;
		if (!(e.currentTarget as HTMLElement).hasPointerCapture(e.pointerId)) return;
		if (!trackNode) return;
		const { width } = trackNode.getBoundingClientRect();
		const viewLen = viewEnd - viewStart;
		const delta = -Math.round(((e.clientX - _panStartX) / width) * viewLen);
		if (delta !== 0) {
			_panTotalDelta += Math.abs(delta);
			onpan?.(delta);
			_panStartX = e.clientX;
		}
	}

	function onTrackPointerUp(_e: PointerEvent) {
		if (_panStartX === null) return;
		const wasPan = _panTotalDelta > 2;
		_panStartX = null;
		if (wasPan) return; // suppress click-to-seek after a pan
		// Fall through to seek (handled by onTrackClick)
	}

	function onTrackClick(e: MouseEvent) {
		if (_panTotalDelta > 2) {
			_panTotalDelta = 0;
			return;
		}
		_panTotalDelta = 0;
		const target = e.target as HTMLElement;
		if (target.closest('.range-handle') || target.closest('.playhead')) return;
		const idx = Math.max(clampedRangeStart, Math.min(clampedRangeEnd, clientXToIndex(e.clientX)));
		onchange(idx);
	}

	// ── Scroll wheel zoom ──────────────────────────────────────────

	function onTrackWheel(e: WheelEvent) {
		e.preventDefault();
		if (e.deltaY < 0) onzoomin?.();
		else onzoomout?.();
	}
</script>

<div class="timeline">
	<button
		class="play-btn"
		class:playing={isPlaying}
		onclick={togglePlay}
		aria-label={isPlaying ? 'Pause' : 'Play through time range'}
		title={isPlaying ? 'Pause' : 'Play'}
	>
		{#if isPlaying}
			<Pause size={12} aria-hidden="true" />
		{:else}
			<Play size={12} aria-hidden="true" />
		{/if}
	</button>

	<div class="track-area">
		<div class="track-header">
			<span class="label-heading">Timeline</span>
			<div class="track-header-right">
				{#if zoomWindowSize !== null}
					<span class="zoom-indicator">{zoomWindowSize} pts</span>
				{/if}
				{#if onzoomin || onzoomout}
					<button
						class="zoom-btn"
						onclick={onzoomout}
						disabled={zoomWindowSize === null}
						aria-label="Zoom out"
						title="Zoom out"><ZoomOut size={10} aria-hidden="true" /></button
					>
					<button class="zoom-btn" onclick={onzoomin} aria-label="Zoom in" title="Zoom in"
						><ZoomIn size={10} aria-hidden="true" /></button
					>
				{/if}
				<span class="label-current">
					{values[currentIndex] ? formatDate(values[currentIndex].period_start) : ''}
				</span>
			</div>
		</div>

		<div
			class="track-wrap"
			class:panning={_panStartX !== null}
			{@attach trackAttachment}
			onclick={onTrackClick}
			onpointerdown={onTrackPointerDown}
			onpointermove={onTrackPointerMove}
			onpointerup={onTrackPointerUp}
			onwheel={onTrackWheel}
			role="presentation"
		>
			<!-- Base track line -->
			<div class="track-line"></div>

			<!-- Active range highlight -->
			<div
				class="range-band"
				style="left: {indexToPercent(clampedRangeStart)}%; right: {100 -
					indexToPercent(clampedRangeEnd)}%"
			></div>

			<!-- Tick marks — only visible range -->
			{#each visibleValues as _v, i (viewStart + i)}
				<div
					class="tick-mark"
					class:active={viewStart + i === currentIndex}
					style="left: {indexToPercent(viewStart + i)}%"
				></div>
			{/each}

			<!-- Range start bracket handle -->
			<div
				class="range-handle left"
				style="left: {indexToPercent(clampedRangeStart)}%"
				onpointerdown={onRangeStartDown}
				onpointermove={onRangeStartMove}
				onpointerup={onRangeStartUp}
				role="slider"
				aria-label="Range start"
				aria-valuenow={clampedRangeStart}
				aria-valuemin={viewStart}
				aria-valuemax={clampedRangeEnd - 1}
				tabindex="0"
			>
				<div class="handle-bar"></div>
				<div class="handle-tab top"></div>
				<div class="handle-tab bottom"></div>
			</div>

			<!-- Range end bracket handle -->
			<div
				class="range-handle right"
				style="left: {indexToPercent(clampedRangeEnd)}%"
				onpointerdown={onRangeEndDown}
				onpointermove={onRangeEndMove}
				onpointerup={onRangeEndUp}
				role="slider"
				aria-label="Range end"
				aria-valuenow={clampedRangeEnd}
				aria-valuemin={clampedRangeStart + 1}
				aria-valuemax={viewEnd}
				tabindex="0"
			>
				<div class="handle-bar"></div>
				<div class="handle-tab top"></div>
				<div class="handle-tab bottom"></div>
			</div>

			<!-- Playhead -->
			<div
				class="playhead"
				class:playing={isPlaying}
				style="left: {indexToPercent(currentIndex)}%"
				onpointerdown={onPlayheadDown}
				onpointermove={onPlayheadMove}
				onpointerup={onPlayheadUp}
				role="slider"
				aria-label="Current time"
				aria-valuenow={currentIndex}
				aria-valuemin={clampedRangeStart}
				aria-valuemax={clampedRangeEnd}
				tabindex="0"
			></div>
		</div>

		<!-- Year labels below track — thinned to avoid overlap -->
		<div class="tick-labels">
			{#each visibleValues as v, i (v.period_start)}
				{#if i % labelStep === 0}
					<div
						class="tick-label"
						class:active={viewStart + i === currentIndex}
						style="left: {indexToPercent(viewStart + i)}%"
					>
						{formatYear(v.period_start)}
					</div>
				{/if}
			{/each}
		</div>
	</div>
</div>

<style>
	.timeline {
		display: flex;
		align-items: center;
		gap: 1rem;
		padding: 0.7rem 1rem 0.9rem;
		user-select: none;
	}

	/* ── Play/pause button ─────────────────────────── */
	.play-btn {
		flex-shrink: 0;
		width: 32px;
		height: 32px;
		border-radius: 50%;
		border: 1.5px solid var(--color-border-strong);
		background: white;
		color: var(--color-text-muted);
		display: flex;
		align-items: center;
		justify-content: center;
		cursor: pointer;
		transition:
			border-color var(--transition-fast),
			color var(--transition-fast),
			background var(--transition-fast);
	}

	.play-btn:hover {
		border-color: var(--color-accent);
		color: var(--color-accent);
	}

	.play-btn.playing {
		background: var(--color-accent);
		border-color: var(--color-accent);
		color: white;
	}

	/* ── Track area ────────────────────────────────── */
	.track-area {
		flex: 1;
		min-width: 0;
	}

	.track-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 0.45rem;
	}

	.track-header-right {
		display: flex;
		align-items: center;
		gap: 0.35rem;
	}

	.label-heading {
		font-size: 0.6rem;
		font-weight: 700;
		letter-spacing: 0.1em;
		text-transform: uppercase;
		color: var(--color-text-faint);
	}

	.label-current {
		font-size: 0.8rem;
		font-weight: 600;
		color: var(--color-text);
	}

	.zoom-indicator {
		font-size: 0.6rem;
		color: var(--color-text-faint);
		font-variant-numeric: tabular-nums;
	}

	/* ── Zoom buttons ──────────────────────────────── */
	.zoom-btn {
		display: flex;
		align-items: center;
		justify-content: center;
		width: 18px;
		height: 18px;
		border-radius: var(--radius-sm);
		border: 1px solid var(--color-border);
		background: var(--color-bg);
		color: var(--color-text-muted);
		cursor: pointer;
		padding: 0;
		transition:
			border-color var(--transition-fast),
			color var(--transition-fast);
	}

	.zoom-btn:hover:not(:disabled) {
		border-color: var(--color-accent);
		color: var(--color-accent);
	}

	.zoom-btn:disabled {
		opacity: 0.35;
		cursor: default;
	}

	/* ── Interactive track ─────────────────────────── */
	.track-wrap {
		position: relative;
		height: 32px;
		cursor: pointer;
	}

	.track-wrap.panning {
		cursor: grabbing;
	}

	.track-line {
		position: absolute;
		top: 50%;
		left: 0;
		right: 0;
		height: 3px;
		margin-top: -1.5px;
		background: var(--color-border);
		border-radius: 2px;
		pointer-events: none;
	}

	/* ── Range highlight band ──────────────────────── */
	.range-band {
		position: absolute;
		top: 50%;
		height: 3px;
		margin-top: -1.5px;
		background: color-mix(in srgb, var(--color-accent) 25%, transparent);
		pointer-events: none;
	}

	/* ── Tick marks ────────────────────────────────── */
	.tick-mark {
		position: absolute;
		top: 50%;
		transform: translate(-50%, -50%);
		width: 2px;
		height: 10px;
		background: var(--color-border-strong);
		border-radius: 1px;
		pointer-events: none;
		transition: background var(--transition-fast);
	}

	.tick-mark.active {
		background: var(--color-accent);
		height: 14px;
	}

	/* ── Range bracket handles ─────────────────────── */
	.range-handle {
		position: absolute;
		top: 50%;
		width: 16px;
		height: 28px;
		cursor: ew-resize;
		z-index: 20;
	}

	.range-handle.left {
		transform: translate(-100%, -50%);
	}

	.range-handle.right {
		transform: translate(0, -50%);
	}

	.handle-bar {
		position: absolute;
		top: 0;
		bottom: 0;
		width: 3px;
		background: var(--color-accent);
		border-radius: 2px;
		opacity: 0.75;
		transition: opacity var(--transition-fast);
	}

	.range-handle.left .handle-bar {
		right: 0;
	}
	.range-handle.right .handle-bar {
		left: 0;
	}

	.handle-tab {
		position: absolute;
		height: 3px;
		width: 7px;
		background: var(--color-accent);
		border-radius: 1px;
		opacity: 0.75;
		transition: opacity var(--transition-fast);
	}

	.range-handle.left .handle-tab {
		right: 0;
	}
	.range-handle.right .handle-tab {
		left: 0;
	}
	.handle-tab.top {
		top: 0;
	}
	.handle-tab.bottom {
		bottom: 0;
	}

	.range-handle:hover .handle-bar,
	.range-handle:hover .handle-tab,
	.range-handle:active .handle-bar,
	.range-handle:active .handle-tab {
		opacity: 1;
	}

	/* ── Playhead ──────────────────────────────────── */
	.playhead {
		position: absolute;
		top: 50%;
		transform: translate(-50%, -50%);
		width: 15px;
		height: 15px;
		border-radius: 50%;
		background: var(--color-accent);
		border: 2px solid white;
		box-shadow: 0 1px 5px rgba(240, 59, 32, 0.4);
		cursor: grab;
		z-index: 30;
		transition:
			transform var(--transition-fast),
			box-shadow var(--transition-fast);
	}

	.playhead:hover {
		transform: translate(-50%, -50%) scale(1.25);
		box-shadow: 0 2px 8px rgba(240, 59, 32, 0.55);
	}

	.playhead:active,
	.playhead.playing {
		cursor: grabbing;
	}

	/* ── Year labels ───────────────────────────────── */
	.tick-labels {
		position: relative;
		height: 1.1rem;
		margin-top: 0.25rem;
	}

	.tick-label {
		position: absolute;
		transform: translateX(-50%);
		font-size: 0.65rem;
		font-weight: 500;
		color: var(--color-text-faint);
		white-space: nowrap;
		transition:
			color var(--transition-fast),
			font-weight var(--transition-fast);
		pointer-events: none;
	}

	.tick-label.active {
		color: var(--color-accent);
		font-weight: 700;
	}
</style>
