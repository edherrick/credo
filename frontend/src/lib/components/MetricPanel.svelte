<script lang="ts">
	import type { Metric, CountySeries } from '../types';

	const MAX_COMPARE = 2;

	interface Props {
		metrics: Metric[];
		selectedMetricId: string;
		compareMetricIds: string[];
		counties: CountySeries[];
		hiddenCountyIds: Set<string>;
		onSelectMetric: (id: string) => void;
		onToggleCounty: (id: string) => void;
		onToggleCompare: (id: string) => void;
	}

	let {
		metrics,
		selectedMetricId,
		compareMetricIds,
		counties,
		hiddenCountyIds,
		onSelectMetric,
		onToggleCounty,
		onToggleCompare
	}: Props = $props();
</script>

<aside class="metric-panel">
	<!-- Metrics section -->
	<div class="panel-section">
		<div class="section-heading">
			<span>Metrics</span>
			{#if compareMetricIds.length > 0}
				<span class="compare-status" class:at-limit={compareMetricIds.length >= MAX_COMPARE}>
					{compareMetricIds.length + 1} overlaid
				</span>
			{/if}
		</div>
		<div class="metric-list">
			{#each metrics as metric (metric.id)}
				{@const isPrimary = metric.id === selectedMetricId}
				{@const isCompared = compareMetricIds.includes(metric.id)}
				{@const atLimit = compareMetricIds.length >= MAX_COMPARE && !isCompared}
				<div class="metric-row" class:selected={isPrimary}>
					<input
						type="checkbox"
						class="compare-check"
						checked={isPrimary || isCompared}
						disabled={isPrimary || atLimit}
						onchange={() => onToggleCompare(metric.id)}
						aria-label="Compare {metric.display_name}"
					/>
					<button
						class="metric-item"
						onclick={() => onSelectMetric(metric.id)}
						title={metric.description ?? metric.display_name}
					>
						<div class="metric-item-top">
							<span class="metric-name">{metric.display_name}</span>
							<span class="metric-unit">{metric.unit}</span>
						</div>
						{#if metric.description}
							<div class="metric-desc">{metric.description}</div>
						{/if}
					</button>
				</div>
			{/each}
			{#if metrics.length === 0}
				<div class="empty-state">No metrics available</div>
			{/if}
		</div>
	</div>

	<!-- Counties section -->
	{#if counties.length > 0}
		<div class="panel-section">
			<div class="section-heading"><span>Counties</span></div>
			<div class="county-list">
				{#each counties as county (county.id)}
					<label class="county-item">
						<input
							type="checkbox"
							checked={!hiddenCountyIds.has(county.id)}
							onchange={() => onToggleCounty(county.id)}
						/>
						<span class="county-name">{county.name}</span>
					</label>
				{/each}
			</div>
		</div>
	{/if}
</aside>

<style>
	.metric-panel {
		width: 240px;
		flex-shrink: 0;
		overflow-y: auto;
		border-left: 1px solid var(--color-border);
		background: var(--color-surface);
		display: flex;
		flex-direction: column;
	}

	.panel-section {
		border-bottom: 1px solid var(--color-border);
		padding: 0.75rem 0;
	}

	.section-heading {
		display: flex;
		align-items: center;
		justify-content: space-between;
		font-size: 0.6rem;
		font-weight: 700;
		letter-spacing: 0.12em;
		text-transform: uppercase;
		color: var(--color-text-faint);
		padding: 0 0.875rem 0.5rem;
	}

	.compare-status {
		font-size: 0.6rem;
		font-weight: 600;
		letter-spacing: 0.05em;
		color: var(--color-accent);
		text-transform: none;
	}

	.compare-status.at-limit {
		color: #d97706; /* amber — warning that limit is reached */
	}

	/* ── Metric rows ───────────────────────────────── */
	.metric-list {
		display: flex;
		flex-direction: column;
		gap: 1px;
	}

	.metric-row {
		display: flex;
		align-items: stretch;
		border-left: 3px solid transparent;
		transition: border-color var(--transition-fast);
	}

	.metric-row.selected {
		border-left-color: var(--color-accent);
		background: color-mix(in srgb, var(--color-accent) 6%, transparent);
	}

	.compare-check {
		flex-shrink: 0;
		width: 32px;
		display: flex;
		align-items: center;
		justify-content: center;
		cursor: pointer;
		accent-color: var(--color-accent);
		margin: 0;
		appearance: auto;
		width: 13px;
		height: 13px;
		margin: auto 0 auto 0.6rem;
	}

	.compare-check:disabled {
		opacity: 0.35;
		cursor: not-allowed;
	}

	.metric-item {
		flex: 1;
		display: flex;
		flex-direction: column;
		gap: 0.2rem;
		padding: 0.5rem 0.875rem 0.5rem 0.5rem;
		background: none;
		border: none;
		text-align: left;
		cursor: pointer;
		transition: background var(--transition-fast);
		min-width: 0;
	}

	.metric-row:hover .metric-item {
		background: var(--color-bg);
	}

	.metric-row.selected .metric-item {
		background: transparent;
	}

	.metric-row.selected:hover .metric-item {
		background: color-mix(in srgb, var(--color-accent) 4%, transparent);
	}

	.metric-item-top {
		display: flex;
		align-items: baseline;
		justify-content: space-between;
		gap: 0.5rem;
	}

	.metric-name {
		font-size: 0.82rem;
		font-weight: 600;
		color: var(--color-text);
		line-height: 1.3;
	}

	.metric-unit {
		font-size: 0.65rem;
		color: var(--color-text-faint);
		font-family: var(--font-mono);
		white-space: nowrap;
		flex-shrink: 0;
	}

	.metric-desc {
		font-size: 0.72rem;
		color: var(--color-text-muted);
		line-height: 1.35;
		overflow: hidden;
		display: -webkit-box;
		-webkit-line-clamp: 2;
		-webkit-box-orient: vertical;
	}

	.empty-state {
		padding: 0.5rem 0.875rem;
		font-size: 0.8rem;
		color: var(--color-text-faint);
	}

	/* ── County list ───────────────────────────────── */
	.county-list {
		display: flex;
		flex-direction: column;
		gap: 1px;
	}

	.county-item {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.4rem 0.875rem;
		cursor: pointer;
		transition: background var(--transition-fast);
	}

	.county-item:hover {
		background: var(--color-bg);
	}

	.county-item input[type='checkbox'] {
		accent-color: var(--color-accent);
		width: 13px;
		height: 13px;
		flex-shrink: 0;
		cursor: pointer;
	}

	.county-name {
		font-size: 0.78rem;
		color: var(--color-text-muted);
		line-height: 1.3;
	}
</style>
