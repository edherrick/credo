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

	// ── Means taxonomy display ───────────────────────────────
	const MEANS_COLOR: Record<string, string> = {
		incentive:  'var(--score-hero)',
		penalty:    'var(--score-negative)',
		mandate:    '#3b82f6',
		boycott:    '#a855f7',
		divestment: '#f59e0b',
		zoning:     'var(--score-positive)',
		litigation: '#ef4444',
		petition:   '#6b7280',
		subsidy:    '#84cc16'
	};
</script>

<svelte:head>
	<title>{credo.title} · Credo</title>
</svelte:head>

<ActorModal entity={selectedActor} onclose={() => (selectedActor = null)} />

<!-- Credo summary — moved below the tabs so the tab layout stays consistent across tabs -->
{#if credo.description}
	<section class="section credo-intro">
		<div class="section-inner">
			<p class="credo-intro-lead">{credo.description}</p>
		</div>
	</section>
{/if}

<!-- Founding Beliefs -->
{#if credo.beliefs && credo.beliefs.length > 0}
	<section class="section section-alt">
		<div class="section-inner">
			<div class="section-header">
				<h2 class="section-title">Founding Beliefs</h2>
				<p class="section-sub">The foundational premises this credo takes as self-evidently true</p>
			</div>
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
		</div>
	</section>
{/if}

<!-- Agendas -->
{#if credo.agendas.length > 0}
	<section class="section">
		<div class="section-inner">
			<div class="section-header">
				<h2 class="section-title">Active Agendas</h2>
				<p class="section-sub">Goals with measurable targets and policy instruments</p>
			</div>

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
						<!-- Goal header -->
						<div class="agenda-goal-header">
							<div class="agenda-badge" class:lower={agenda.direction === 'lower'}>
								{#if agenda.direction === 'lower'}
									<TrendingDown size={12} aria-hidden="true" /> Lower
								{:else}
									<TrendingUp size={12} aria-hidden="true" /> Raise
								{/if}
							</div>
							<h3 class="agenda-title">{agenda.title}</h3>
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
									<span class="agenda-tag agenda-tag-geo"
										>+{agenda.geography_ids.length - 2} more</span
									>
								{/if}
							</div>
							<div class="agenda-meta">
								{#if agenda.target_value}
									<span class="agenda-target">
										Target: <strong>{formatCurrency(agenda.target_value)}</strong>
									</span>
								{/if}
								{#if agenda.target_date}
									<span class="agenda-date">by {agenda.target_date}</span>
								{/if}
							</div>
						</div>

						<!-- Means -->
						{#if agenda.means.length > 0}
							<div class="agenda-means">
								<div class="means-heading">How</div>
								<div class="means-list">
									{#each agenda.means as am (am.means_id)}
										{@const color = MEANS_COLOR[am.means.category.id] ?? '#6b7280'}
										<div class="means-item">
											<span
												class="means-badge"
												style="--badge-color: {color}"
											>{am.means.category.label}</span>
											<div class="means-body">
												<p class="means-title">{am.means.title}</p>
												{#if am.means.description}
													<p class="means-desc">{am.means.description}</p>
												{/if}
												{#if am.notes}
													<p class="means-target">{am.notes}</p>
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
		</div>
	</section>
{/if}

<!-- Actors -->
{#if credo.entities.length > 0}
	<section class="section section-alt">
		<div class="section-inner">
			<div class="section-header">
				<h2 class="section-title">Entities</h2>
				<p class="section-sub">
					Entities with a documented impact on this credo's metrics — click for full detail
				</p>
			</div>
			<div class="actor-grid">
				{#each credo.entities as entity (entity.id)}
					{@const tier = scoreTier(entity.impact_score)}
					<button
						class="actor-card actor-card--{tier}"
						onclick={() => (selectedActor = entity)}
					>
						<div class="actor-card-top">
							<span class="actor-type">{entity.type}</span>
							<span class="actor-score score--{tier}">
								<span class="score-dot" aria-hidden="true"></span>
								{tierLabel[tier]}
							</span>
						</div>
						<h3 class="actor-name">{entity.name}</h3>
						{#if entity.description}
							<p class="actor-desc">{entity.description}</p>
						{/if}
						{#if entity.events.length > 0}
							<span class="actor-events-hint">
								{entity.events.length} event{entity.events.length === 1 ? '' : 's'} →
							</span>
						{/if}
					</button>
				{/each}
			</div>
		</div>
	</section>
{/if}

<!-- Metrics -->
{#if metrics.length > 0}
	<section class="section">
		<div class="section-inner">
			<div class="section-header">
				<h2 class="section-title">Metrics</h2>
				<p class="section-sub">Tracked measurements that anchor this credo</p>
			</div>
			<div class="card-grid">
				{#each metrics as metric (metric.id)}
					<a href={resolve(`/map?metric=${metric.id}`)} class="metric-card">
						<div class="metric-card-top">
							<span class="metric-unit">{metric.unit}</span>
						</div>
						<h3 class="metric-name">{metric.display_name}</h3>
						{#if metric.description}
							<p class="metric-desc">{metric.description}</p>
						{/if}
						<div class="metric-arrow">
							View on map <ArrowRight size={13} aria-hidden="true" />
						</div>
					</a>
				{/each}
			</div>
		</div>
	</section>
{/if}

<style>
	/* ── Sections ────────────────────────────────────────── */
	.section {
		padding: var(--space-16) var(--space-6);
	}

	.section-alt {
		background: var(--color-surface);
		border-top: 1px solid var(--color-border);
		border-bottom: 1px solid var(--color-border);
	}

	.section-inner {
		max-width: var(--max-width);
		margin: 0 auto;
	}

	.section-header {
		margin-bottom: var(--space-8);
	}

	.section-title {
		font-family: var(--font-serif);
		font-size: 1.6rem;
		font-weight: 400;
		color: var(--color-text);
		margin-bottom: 0.35rem;
	}

	.section-sub {
		font-size: 0.9rem;
		color: var(--color-text-muted);
	}

	/* Credo summary lead — first block under the tabs on Overview.
	   Sits on a raised surface so it separates from the deep-navy header. */
	.credo-intro {
		background: var(--color-surface);
		border-bottom: 1px solid var(--color-border);
		padding-top: var(--space-10);
		padding-bottom: var(--space-10);
	}

	.credo-intro-lead {
		font-family: var(--font-serif);
		font-size: clamp(1.1rem, 2.2vw, 1.5rem);
		font-weight: 400;
		line-height: 1.6;
		color: var(--color-text);
		max-width: var(--max-width-text);
	}

	/* ── Founding beliefs ───────────────────────────────── */
	.beliefs-list {
		list-style: none;
		display: flex;
		flex-direction: column;
		gap: var(--space-6);
		padding: 0;
		margin: 0;
		max-width: var(--max-width-text);
	}

	.belief-item {
		display: flex;
		gap: var(--space-5);
		align-items: flex-start;
	}

	.belief-num {
		flex-shrink: 0;
		font-family: var(--font-mono);
		font-size: 1.1rem;
		font-weight: 700;
		color: var(--color-accent);
		opacity: 0.7;
		letter-spacing: -0.02em;
		padding-top: 0.1rem;
		min-width: 2rem;
	}

	.belief-body {
		display: flex;
		flex-direction: column;
		gap: var(--space-2);
	}

	.belief-title {
		font-size: 1rem;
		font-weight: 600;
		color: var(--color-text);
		line-height: 1.4;
	}

	.belief-statement {
		font-size: 0.875rem;
		color: var(--color-text-muted);
		line-height: 1.65;
		max-width: 600px;
	}

	.belief-meta {
		display: flex;
		flex-wrap: wrap;
		gap: var(--space-2);
		align-items: center;
	}

	.belief-source {
		font-size: 0.7rem;
		font-weight: 600;
		letter-spacing: 0.07em;
		text-transform: uppercase;
		padding: 0.15rem 0.5rem;
		border-radius: var(--radius-sm);
		background: var(--color-border);
		color: var(--color-text-faint);
	}

	.belief-notes {
		font-size: 0.8rem;
		color: var(--color-text-faint);
		font-style: italic;
	}

	/* ── Area filter ─────────────────────────────────────── */
	.area-filter {
		display: flex;
		flex-wrap: wrap;
		gap: var(--space-2);
		margin-bottom: var(--space-5);
	}

	.area-pill {
		font-size: 0.8rem;
		font-weight: 500;
		padding: 0.3rem 0.75rem;
		border-radius: var(--radius-full);
		border: 1px solid var(--color-border);
		background: var(--color-bg);
		color: var(--color-text-muted);
		cursor: pointer;
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

	/* ── Agenda cards ────────────────────────────────────── */
	.agenda-list {
		display: flex;
		flex-direction: column;
		gap: var(--space-5);
	}

	.agenda-card {
		background: var(--color-bg);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-lg);
		overflow: hidden;
	}

	.agenda-goal-header {
		padding: var(--space-5) var(--space-6);
		display: flex;
		flex-direction: column;
		gap: var(--space-2);
	}

	.agenda-badge {
		display: inline-flex;
		align-items: center;
		gap: 0.3rem;
		font-size: 0.7rem;
		font-weight: 600;
		letter-spacing: 0.08em;
		text-transform: uppercase;
		padding: 0.2rem 0.6rem;
		border-radius: var(--radius-sm);
		background: var(--color-border);
		color: var(--color-text-muted);
		width: fit-content;
	}

	.agenda-badge.lower {
		background: var(--color-warn-bg);
		color: var(--color-warn-text);
	}

	.agenda-title {
		font-size: 1rem;
		font-weight: 600;
		color: var(--color-text);
		line-height: 1.4;
	}

	.agenda-tags {
		display: flex;
		flex-wrap: wrap;
		gap: var(--space-2);
	}

	.agenda-tag {
		font-size: 0.72rem;
		padding: 0.15rem 0.5rem;
		border-radius: var(--radius-sm);
		background: var(--color-border);
		color: var(--color-text-muted);
	}

	.agenda-tag-geo {
		background: var(--color-surface);
		border: 1px solid var(--color-border);
	}

	.agenda-meta {
		display: flex;
		align-items: center;
		gap: var(--space-4);
		font-size: 0.85rem;
		color: var(--color-text-muted);
	}

	.agenda-target strong {
		color: var(--color-text);
	}

	/* ── Agenda means ────────────────────────────────────── */
	.agenda-means {
		border-top: 1px solid var(--color-border);
		background: var(--color-surface);
		padding: var(--space-4) var(--space-6) var(--space-5);
	}

	.means-heading {
		font-size: 0.65rem;
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
		font-size: 0.65rem;
		font-weight: 700;
		letter-spacing: 0.08em;
		text-transform: uppercase;
		padding: 0.2rem 0.5rem;
		border-radius: var(--radius-sm);
		color: white;
		background: var(--badge-color);
		margin-top: 0.15rem;
		min-width: 5.5rem;
		text-align: center;
	}

	.means-body {
		display: flex;
		flex-direction: column;
		gap: 0.25rem;
	}

	.means-title {
		font-size: 0.875rem;
		font-weight: 600;
		color: var(--color-text);
		line-height: 1.4;
	}

	.means-desc {
		font-size: 0.8rem;
		color: var(--color-text-muted);
		line-height: 1.55;
	}

	.means-target {
		font-size: 0.75rem;
		color: var(--color-text-faint);
		font-style: italic;
	}

	/* ── Actor grid ──────────────────────────────────────── */
	.actor-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
		gap: var(--space-4);
	}

	.actor-card {
		display: flex;
		flex-direction: column;
		gap: var(--space-2);
		background: var(--color-bg);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-lg);
		padding: var(--space-5) var(--space-6);
		border-left-width: 3px;
		text-align: left;
		cursor: pointer;
		transition:
			box-shadow var(--transition-base),
			transform var(--transition-base),
			border-color var(--transition-base);
	}

	.actor-card:hover {
		box-shadow: var(--shadow-accent);
		transform: translateY(-2px);
	}

	.actor-card--hero     { border-left-color: var(--score-hero); }
	.actor-card--positive { border-left-color: var(--score-positive); }
	.actor-card--neutral  { border-left-color: var(--color-border-strong); }
	.actor-card--negative { border-left-color: var(--score-negative); }
	.actor-card--villain  { border-left-color: var(--score-villain); }

	.actor-card-top {
		display: flex;
		align-items: center;
		justify-content: space-between;
	}

	.actor-type {
		font-size: 0.7rem;
		font-weight: 600;
		letter-spacing: 0.1em;
		text-transform: uppercase;
		color: var(--color-text-faint);
	}

	.actor-score {
		display: flex;
		align-items: center;
		gap: 0.35rem;
		font-size: 0.72rem;
		font-weight: 600;
		letter-spacing: 0.06em;
		text-transform: uppercase;
	}

	.score-dot {
		width: 7px;
		height: 7px;
		border-radius: 50%;
		flex-shrink: 0;
	}

	.score--hero     { color: var(--score-hero); }
	.score--hero .score-dot     { background: var(--score-hero); }
	.score--positive { color: var(--score-positive); }
	.score--positive .score-dot { background: var(--score-positive); }
	.score--neutral  { color: var(--color-text-muted); }
	.score--neutral .score-dot  { background: var(--color-text-muted); }
	.score--negative { color: var(--score-negative); }
	.score--negative .score-dot { background: var(--score-negative); }
	.score--villain  { color: var(--score-villain); }
	.score--villain .score-dot  { background: var(--score-villain); }

	.actor-name {
		font-size: 1rem;
		font-weight: 600;
		color: var(--color-text);
		line-height: 1.3;
	}

	.actor-desc {
		font-size: 0.82rem;
		color: var(--color-text-muted);
		line-height: 1.55;
	}

	.actor-events-hint {
		margin-top: auto;
		padding-top: var(--space-2);
		font-size: 0.75rem;
		font-weight: 500;
		color: var(--color-accent);
	}

	/* ── Metric cards ────────────────────────────────────── */
	.card-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
		gap: var(--space-4);
	}

	.metric-card {
		display: flex;
		flex-direction: column;
		gap: var(--space-2);
		background: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-lg);
		padding: var(--space-5) var(--space-6);
		transition:
			border-color var(--transition-base),
			box-shadow var(--transition-base),
			transform var(--transition-base);
		cursor: pointer;
	}

	.metric-card:hover {
		border-color: var(--color-accent);
		box-shadow: var(--shadow-accent);
		transform: translateY(-2px);
	}

	.metric-card-top {
		display: flex;
		align-items: center;
	}

	.metric-unit {
		font-size: 0.7rem;
		font-weight: 600;
		letter-spacing: 0.1em;
		text-transform: uppercase;
		color: var(--color-text-faint);
	}

	.metric-name {
		font-size: 1.05rem;
		font-weight: 600;
		color: var(--color-text);
		line-height: 1.3;
	}

	.metric-desc {
		font-size: 0.82rem;
		color: var(--color-text-muted);
		line-height: 1.55;
	}

	.metric-arrow {
		margin-top: auto;
		padding-top: var(--space-3);
		font-size: 0.8rem;
		font-weight: 500;
		color: var(--color-accent);
		opacity: 0;
		display: flex;
		align-items: center;
		gap: 0.25rem;
		transition: opacity var(--transition-fast);
	}

	.metric-card:hover .metric-arrow {
		opacity: 1;
	}
</style>
