<script lang="ts">
	import { resolve } from '$app/paths';
	import { ArrowRight, TrendingUp, TrendingDown } from 'lucide-svelte';
	import type { Entity, Geography, Metric } from '$lib/types';
	import ActorModal from '$lib/components/ActorModal.svelte';

	let { data } = $props();

	const credo = $derived(data.credo);
	const geographies = $derived(data.geographies as Geography[]);
	const metrics = $derived(data.metrics as Metric[]);

	// ── Area filter ──────────────────────────────────────────
	let selectedGeoId = $state<string | null>(null);

	const filteredAgendas = $derived(
		selectedGeoId
			? credo.agendas.filter((a) => a.geography_ids.includes(selectedGeoId!))
			: credo.agendas
	);

	const filterableGeos = $derived(
		geographies.filter((g) => credo.agendas.some((a) => a.geography_ids.includes(g.id)))
	);

	// ── Helpers ──────────────────────────────────────────────
	function geoForId(id: string): Geography | undefined {
		return geographies.find((g) => g.id === id);
	}

	function metricForId(id: string | null): Metric | undefined {
		return id ? metrics.find((m) => m.id === id) : undefined;
	}

	function formatCurrency(val: number | null): string {
		if (val === null || val === undefined) return '—';
		return new Intl.NumberFormat('en-US', {
			style: 'currency',
			currency: 'USD',
			maximumFractionDigits: 0
		}).format(val);
	}

	// ── Actor modal ──────────────────────────────────────────
	let selectedActor = $state<Entity | null>(null);

	type ScoreTier = 'hero' | 'positive' | 'neutral' | 'negative' | 'villain';

	function scoreTier(score: number): ScoreTier {
		if (score >= 60) return 'hero';
		if (score >= 20) return 'positive';
		if (score >= -19) return 'neutral';
		if (score >= -59) return 'negative';
		return 'villain';
	}

	const tierLabel: Record<ScoreTier, string> = {
		hero: 'Hero',
		positive: 'Positive',
		neutral: 'Neutral',
		negative: 'Negative',
		villain: 'Villain'
	};

	const tierColor: Record<ScoreTier, string> = {
		hero: '#22c55e',
		positive: '#14b8a6',
		neutral: '#6080a0',
		negative: '#f97316',
		villain: '#f03b20'
	};

	// ── Means taxonomy display ───────────────────────────────
	const MEANS_COLOR: Record<string, string> = {
		incentive:  '#22c55e',
		penalty:    '#f97316',
		mandate:    '#3b82f6',
		boycott:    '#a855f7',
		divestment: '#f59e0b',
		zoning:     '#14b8a6',
		litigation: '#ef4444',
		petition:   '#6b7280',
		subsidy:    '#84cc16'
	};
</script>

<svelte:head>
	<title>{credo.title} · Credo</title>
</svelte:head>

<ActorModal entity={selectedActor} onclose={() => (selectedActor = null)} />

<div class="overview">
	<div class="overview-inner">

		<!-- Main column -->
		<div class="main-col">

			<!-- Founding Beliefs -->
			{#if credo.beliefs && credo.beliefs.length > 0}
			<section class="content-section">
				<h2 class="section-title">Founding Beliefs</h2>
				<p class="section-sub">The foundational premises this credo takes as self-evidently true</p>
				<ol class="beliefs-list">
					{#each credo.beliefs as cb, i}
						<li class="belief-item">
							<span class="belief-num" aria-hidden="true">{String(i + 1).padStart(2, '0')}</span>
							<div class="belief-body">
								<p class="belief-title">{cb.belief.title}</p>
								<p class="belief-statement">{cb.belief.statement}</p>
								<div class="belief-meta">
									{#if cb.belief.source}
										<span class="belief-source">{cb.belief.source}</span>
									{/if}
									{#if cb.notes}
										<span class="belief-notes">{cb.notes}</span>
									{/if}
								</div>
							</div>
						</li>
					{/each}
				</ol>
			</section>
			{/if}

			<!-- Agendas -->
			{#if credo.agendas.length > 0}
			<section class="content-section">
				<h2 class="section-title">Active Agendas</h2>
				<p class="section-sub">Goals with measurable targets and policy instruments</p>

				{#if filterableGeos.length > 1}
					<div class="area-filter">
						<button
							class="area-pill"
							class:active={selectedGeoId === null}
							onclick={() => (selectedGeoId = null)}
						>All areas</button>
						{#each filterableGeos as geo (geo.id)}
							<button
								class="area-pill"
								class:active={selectedGeoId === geo.id}
								onclick={() => (selectedGeoId = selectedGeoId === geo.id ? null : geo.id)}
							>{geo.name}</button>
						{/each}
					</div>
				{/if}

				<div class="agenda-list">
					{#each filteredAgendas as agenda (agenda.id)}
						<div class="agenda-card">
							<div class="agenda-header">
								<div class="agenda-badge" class:lower={agenda.direction === 'lower'}>
									{#if agenda.direction === 'lower'}
										<TrendingDown size={11} aria-hidden="true" /> Lower
									{:else}
										<TrendingUp size={11} aria-hidden="true" /> Raise
									{/if}
								</div>

								<div class="agenda-tags">
									{#if agenda.metric_id}
										{@const m = metricForId(agenda.metric_id)}
										{#if m}<span class="agenda-tag">{m.display_name}</span>{/if}
									{/if}
									{#each agenda.geography_ids.slice(0, 2) as gid}
										{@const g = geoForId(gid)}
										{#if g}<span class="agenda-tag agenda-tag-geo">{g.name}</span>{/if}
									{/each}
									{#if agenda.geography_ids.length > 2}
										<span class="agenda-tag agenda-tag-geo">+{agenda.geography_ids.length - 2} more</span>
									{/if}
								</div>

								<h3 class="agenda-title">{agenda.title}</h3>

								{#if agenda.target_value || agenda.target_date}
									<div class="agenda-target-row">
										{#if agenda.target_value}
											<span>Target: <strong>{formatCurrency(agenda.target_value)}</strong></span>
										{/if}
										{#if agenda.target_date}
											<span>by <strong>{agenda.target_date}</strong></span>
										{/if}
									</div>
								{/if}
							</div>

							{#if agenda.means.length > 0}
								<div class="agenda-means">
									<div class="means-heading">How</div>
									<div class="means-list">
										{#each agenda.means as am (am.means_id)}
											{@const color = MEANS_COLOR[am.means.category.id] ?? '#6b7280'}
											<div class="means-item">
												<span class="means-badge" style="--badge-color:{color}">{am.means.category.label}</span>
												<div class="means-body">
													<p class="means-title">{am.means.title}</p>
													{#if am.means.description}
														<p class="means-desc">{am.means.description}</p>
													{/if}
													{#if am.notes}
														<p class="means-notes">{am.notes}</p>
													{/if}
												</div>
											</div>
										{/each}
									</div>
								</div>
							{/if}
						</div>
					{/each}
				</div>
			</section>
			{/if}

		</div>

		<!-- Sidebar -->
		<aside class="side-col">

			<!-- Entities -->
			{#if credo.entities.length > 0}
			<div class="sidebar-card">
				<h3 class="sidebar-label">Entities</h3>
				<p class="sidebar-hint">Click for full detail</p>
				<div class="entity-list">
					{#each credo.entities as entity (entity.id)}
						{@const tier = scoreTier(entity.impact_score)}
						<button
							class="entity-row"
							onclick={() => (selectedActor = entity)}
						>
							<div class="entity-row-left">
								<p class="entity-name">{entity.name}</p>
								<p class="entity-type">{entity.type}</p>
							</div>
							<div class="entity-score" style="--score-color:{tierColor[tier]};">
								<span class="score-dot" aria-hidden="true"></span>
								{tierLabel[tier]}
							</div>
						</button>
					{/each}
				</div>
			</div>
			{/if}

			<!-- Metrics -->
			{#if metrics.length > 0}
			<div class="sidebar-card">
				<h3 class="sidebar-label">Tracked Metrics</h3>
				<div class="metric-list">
					{#each metrics as metric (metric.id)}
						<a href={resolve(`/map?metric=${metric.id}`)} class="metric-row">
							<div>
								<p class="metric-name">{metric.display_name}</p>
								<p class="metric-unit">{metric.unit}</p>
							</div>
							<span class="metric-arrow" aria-hidden="true">
								<ArrowRight size={12} />
							</span>
						</a>
					{/each}
				</div>
			</div>
			{/if}

			<!-- Data sources placeholder -->
			<div class="sidebar-card sidebar-card--faint">
				<h3 class="sidebar-label">Data Sources</h3>
				<p class="sidebar-hint">Evidence and data sources linked to beliefs and agendas will appear here.</p>
			</div>

		</aside>
	</div>
</div>

<style>
	/* ── Layout ──────────────────────────────────────── */
	.overview {
		padding: var(--space-12) var(--space-6) var(--space-20);
	}

	.overview-inner {
		max-width: var(--max-width);
		margin: 0 auto;
		display: grid;
		grid-template-columns: 1fr 288px;
		gap: var(--space-12);
		align-items: start;
	}

	@media (max-width: 900px) {
		.overview-inner {
			grid-template-columns: 1fr;
		}
	}

	/* ── Section ─────────────────────────────────────── */
	.content-section {
		margin-bottom: var(--space-14);
	}

	.section-title {
		font-family: var(--font-serif);
		font-size: 1.5rem;
		font-weight: 400;
		color: var(--color-text);
		margin-bottom: 0.3rem;
	}

	.section-sub {
		font-size: 0.8125rem;
		color: var(--color-text-muted);
		margin-bottom: var(--space-8);
	}

	/* ── Beliefs ─────────────────────────────────────── */
	.beliefs-list {
		list-style: none;
		display: flex;
		flex-direction: column;
		gap: var(--space-7);
		padding: 0;
		margin: 0;
	}

	.belief-item {
		display: flex;
		gap: var(--space-5);
		align-items: flex-start;
		padding-bottom: var(--space-7);
		border-bottom: 1px solid var(--color-border);
	}

	.belief-item:last-child {
		border-bottom: none;
		padding-bottom: 0;
	}

	.belief-num {
		flex-shrink: 0;
		font-family: var(--font-mono);
		font-size: 1rem;
		font-weight: 700;
		color: var(--color-accent);
		opacity: 0.65;
		letter-spacing: -0.02em;
		padding-top: 0.15rem;
		min-width: 1.75rem;
	}

	.belief-body {
		display: flex;
		flex-direction: column;
		gap: var(--space-2);
	}

	.belief-title {
		font-size: 0.9375rem;
		font-weight: 600;
		color: var(--color-text);
		line-height: 1.4;
	}

	.belief-statement {
		font-size: 0.875rem;
		color: var(--color-text-muted);
		line-height: 1.7;
		max-width: 600px;
	}

	.belief-meta {
		display: flex;
		flex-wrap: wrap;
		gap: var(--space-2);
		align-items: center;
		margin-top: var(--space-1);
	}

	.belief-source {
		font-size: 0.625rem;
		font-weight: 700;
		letter-spacing: 0.07em;
		text-transform: uppercase;
		padding: 0.15rem 0.5rem;
		border-radius: var(--radius-sm);
		background: var(--color-border);
		color: var(--color-text-faint);
	}

	.belief-notes {
		font-size: 0.75rem;
		color: var(--color-text-faint);
		font-style: italic;
	}

	/* ── Area filter ─────────────────────────────────── */
	.area-filter {
		display: flex;
		flex-wrap: wrap;
		gap: var(--space-2);
		margin-bottom: var(--space-5);
	}

	.area-pill {
		font-size: 0.75rem;
		font-weight: 500;
		padding: 0.3rem 0.75rem;
		border-radius: 99px;
		border: 1px solid var(--color-border);
		background: var(--color-bg);
		color: var(--color-text-muted);
		cursor: pointer;
		font-family: inherit;
		transition:
			border-color var(--transition-fast),
			color var(--transition-fast),
			background var(--transition-fast);
	}

	.area-pill:hover {
		border-color: var(--color-accent);
		color: var(--color-accent);
	}

	.area-pill.active {
		background: var(--color-accent);
		border-color: var(--color-accent);
		color: white;
	}

	/* ── Agenda cards ────────────────────────────────── */
	.agenda-list {
		display: flex;
		flex-direction: column;
		gap: var(--space-4);
	}

	.agenda-card {
		background: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-lg);
		overflow: hidden;
	}

	.agenda-header {
		padding: var(--space-5) var(--space-6);
		display: flex;
		flex-direction: column;
		gap: var(--space-2);
	}

	.agenda-badge {
		display: inline-flex;
		align-items: center;
		gap: 0.3rem;
		font-size: 0.625rem;
		font-weight: 700;
		letter-spacing: 0.08em;
		text-transform: uppercase;
		padding: 0.2rem 0.6rem;
		border-radius: var(--radius-sm);
		background: rgba(34, 197, 94, 0.12);
		color: #22c55e;
		width: fit-content;
	}

	.agenda-badge.lower {
		background: var(--color-warn-bg);
		color: var(--color-warn-text);
	}

	.agenda-tags {
		display: flex;
		flex-wrap: wrap;
		gap: var(--space-2);
	}

	.agenda-tag {
		font-size: 0.6875rem;
		padding: 0.15rem 0.5rem;
		border-radius: var(--radius-sm);
		background: var(--color-border);
		color: var(--color-text-muted);
	}

	.agenda-tag-geo {
		background: var(--color-bg);
		border: 1px solid var(--color-border);
	}

	.agenda-title {
		font-size: 1rem;
		font-weight: 600;
		color: var(--color-text);
		line-height: 1.4;
	}

	.agenda-target-row {
		display: flex;
		align-items: center;
		gap: var(--space-4);
		font-size: 0.8125rem;
		color: var(--color-text-muted);
	}

	.agenda-target-row strong {
		color: var(--color-text);
	}

	/* ── Means ───────────────────────────────────────── */
	.agenda-means {
		border-top: 1px solid var(--color-border);
		background: var(--color-bg);
		padding: var(--space-4) var(--space-6) var(--space-5);
	}

	.means-heading {
		font-size: 0.5625rem;
		font-weight: 700;
		letter-spacing: 0.12em;
		text-transform: uppercase;
		color: var(--color-text-faint);
		margin-bottom: var(--space-3);
	}

	.means-list {
		display: flex;
		flex-direction: column;
		gap: var(--space-4);
	}

	.means-item {
		display: flex;
		gap: var(--space-3);
		align-items: flex-start;
	}

	.means-badge {
		flex-shrink: 0;
		font-size: 0.5625rem;
		font-weight: 700;
		letter-spacing: 0.08em;
		text-transform: uppercase;
		padding: 0.2rem 0.5rem;
		border-radius: var(--radius-sm);
		color: white;
		background: var(--badge-color);
		margin-top: 0.15rem;
		min-width: 5rem;
		text-align: center;
	}

	.means-body {
		display: flex;
		flex-direction: column;
		gap: 0.2rem;
	}

	.means-title {
		font-size: 0.875rem;
		font-weight: 600;
		color: var(--color-text);
		line-height: 1.4;
	}

	.means-desc {
		font-size: 0.75rem;
		color: var(--color-text-muted);
		line-height: 1.55;
	}

	.means-notes {
		font-size: 0.6875rem;
		color: var(--color-text-faint);
		font-style: italic;
	}

	/* ── Sidebar ─────────────────────────────────────── */
	.side-col {
		display: flex;
		flex-direction: column;
		gap: var(--space-4);
		position: sticky;
		top: calc(var(--nav-height) + 52px + var(--space-12));
	}

	.sidebar-card {
		background: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-lg);
		padding: var(--space-5);
	}

	.sidebar-card--faint {
		background: transparent;
	}

	.sidebar-label {
		font-size: 0.5625rem;
		font-weight: 700;
		letter-spacing: 0.12em;
		text-transform: uppercase;
		color: var(--color-text-faint);
		margin-bottom: var(--space-1);
	}

	.sidebar-hint {
		font-size: 0.75rem;
		color: var(--color-text-faint);
		line-height: 1.5;
		margin-bottom: var(--space-3);
	}

	/* Entities */
	.entity-list {
		display: flex;
		flex-direction: column;
		margin-top: var(--space-3);
	}

	.entity-row {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: var(--space-3) 0;
		border-bottom: 1px solid var(--color-border);
		background: transparent;
		border-left: none;
		border-right: none;
		border-top: none;
		width: 100%;
		text-align: left;
		cursor: pointer;
		font-family: inherit;
		transition: background var(--transition-fast);
		border-radius: 0;
	}

	.entity-row:last-child {
		border-bottom: none;
	}

	.entity-row:hover {
		background: rgba(255, 255, 255, 0.02);
	}

	.entity-name {
		font-size: 0.8125rem;
		font-weight: 500;
		color: var(--color-text);
		margin-bottom: 0.15rem;
	}

	.entity-type {
		font-size: 0.625rem;
		font-weight: 600;
		color: var(--color-text-faint);
		text-transform: uppercase;
		letter-spacing: 0.07em;
	}

	.entity-score {
		display: flex;
		align-items: center;
		gap: 0.35rem;
		font-size: 0.6875rem;
		font-weight: 600;
		color: var(--score-color);
		flex-shrink: 0;
	}

	.score-dot {
		width: 6px;
		height: 6px;
		border-radius: 50%;
		background: currentColor;
		flex-shrink: 0;
	}

	/* Metrics */
	.metric-list {
		display: flex;
		flex-direction: column;
		margin-top: var(--space-3);
	}

	.metric-row {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: var(--space-3) 0;
		border-bottom: 1px solid var(--color-border);
		transition: opacity var(--transition-fast);
	}

	.metric-row:last-child {
		border-bottom: none;
	}

	.metric-row:hover {
		opacity: 0.8;
	}

	.metric-name {
		font-size: 0.8125rem;
		font-weight: 500;
		color: var(--color-text);
		margin-bottom: 0.1rem;
	}

	.metric-unit {
		font-size: 0.625rem;
		color: var(--color-text-faint);
		font-family: var(--font-mono);
	}

	.metric-arrow {
		color: var(--color-accent);
		flex-shrink: 0;
		opacity: 0;
		transition: opacity var(--transition-fast);
	}

	.metric-row:hover .metric-arrow {
		opacity: 1;
	}
</style>
