<script lang="ts">
	import { ExternalLink } from 'lucide-svelte';
	import type { EntityEvent } from '$lib/types';

	let { data } = $props();
	const entity = $derived(data.entity);

	const SOURCE_TYPE_LABELS: Record<string, string> = {
		government: 'Government',
		wikipedia: 'Wikipedia',
		news: 'News',
		manual: 'Manual'
	};

	function sourceLabel(ev: EntityEvent): string {
		return SOURCE_TYPE_LABELS[ev.source_type] ?? ev.source_type;
	}

	function formatDate(d: string | null): string {
		if (!d) return '';
		return new Date(d).toLocaleDateString('en-US', {
			year: 'numeric',
			month: 'short'
		});
	}

	type ScoreTier = 'hero' | 'positive' | 'neutral' | 'negative' | 'villain';

	function impactTier(score: number | null): ScoreTier {
		if (score === null) return 'neutral';
		if (score >= 60) return 'hero';
		if (score >= 20) return 'positive';
		if (score >= -19) return 'neutral';
		if (score >= -59) return 'negative';
		return 'villain';
	}

	const tierColors: Record<ScoreTier, string> = {
		hero: '#22c55e',
		positive: '#14b8a6',
		neutral: '#6080a0',
		negative: '#f97316',
		villain: '#f03b20'
	};

	const tierLabels: Record<ScoreTier, string> = {
		hero: 'Hero',
		positive: 'Positive',
		neutral: 'Neutral',
		negative: 'Negative',
		villain: 'Villain'
	};
</script>

<svelte:head>
	<title>{entity.name} · Credo</title>
</svelte:head>

<!-- Header -->
<div class="entity-header">
	<div class="header-inner">
		<div class="header-meta">
			<span class="type-badge">{entity.type}</span>
		</div>
		<h1 class="entity-name">{entity.name}</h1>
		{#if entity.description}
			<p class="entity-desc">{entity.description}</p>
		{/if}
		{#if entity.wikidata_id}
			<a
				class="wikidata-link"
				href="https://www.wikidata.org/wiki/{entity.wikidata_id}"
				target="_blank"
				rel="noopener noreferrer"
			>
				Wikidata <ExternalLink size={11} />
			</a>
		{/if}
		<div class="claim-prompt">
			Is this you? <a href="/claim" class="claim-link">Claim this page →</a>
		</div>
	</div>
	<div class="header-rule"></div>
</div>

<!-- Body -->
<div class="entity-body">
	<div class="body-inner">

		<!-- Timeline -->
		<div class="main-col">
			<div class="col-header">
				<h2 class="col-title">Community-Documented Actions</h2>
				{#if entity.events.length > 0}
					<span class="col-count">{entity.events.length} event{entity.events.length === 1 ? '' : 's'} · sourced from public records</span>
				{/if}
			</div>

			{#if entity.events.length === 0}
				<p class="empty">No documented actions on record yet.</p>
			{:else}
				<ol class="timeline">
					{#each entity.events as ev, i (ev.id)}
						{@const score = ev.event_impact_score}
						{@const tier = impactTier(score)}
						{@const color = tierColors[tier]}
						<li class="timeline-item">
							<div class="timeline-dot" style="--dot-color:{color};"></div>
							{#if i < entity.events.length - 1}
								<div class="timeline-line"></div>
							{/if}
							<div class="timeline-content">
								<div class="event-meta">
									{#if ev.event_date}
										<span class="event-date">{formatDate(ev.event_date)}</span>
									{/if}
									<span class="event-source">{sourceLabel(ev)}</span>
								</div>
								<h3 class="event-title">{ev.title}</h3>
								{#if ev.description}
									<p class="event-desc">{ev.description}</p>
								{/if}
								<div class="event-footer">
									{#if score !== null}
										<span class="impact-badge" style="--impact-color:{color};--impact-bg:{color}1a;">
											{score > 0 ? '+' : ''}{score} impact
										</span>
									{/if}
									{#if ev.source_url}
										<a
											class="source-link"
											href={ev.source_url}
											target="_blank"
											rel="noopener noreferrer"
										>
											View source <ExternalLink size={11} />
										</a>
									{/if}
								</div>
							</div>
						</li>
					{/each}
				</ol>
			{/if}
		</div>

		<!-- Sidebar -->
		<aside class="side-col">
			<!-- Impact score placeholder — real scoring TBD -->
			<div class="sidebar-card">
				<h3 class="sidebar-label">Community Impact Score</h3>
				<p class="sidebar-hint">Impact scoring is calculated from documented actions. Add events to generate a score.</p>
			</div>

			<!-- Entity type info -->
			<div class="sidebar-card">
				<h3 class="sidebar-label">Entity Info</h3>
				<div class="info-rows">
					<div class="info-row">
						<span class="info-key">Type</span>
						<span class="info-val">{entity.type}</span>
					</div>
					{#if entity.wikidata_id}
						<div class="info-row">
							<span class="info-key">Wikidata</span>
							<a
								class="info-link"
								href="https://www.wikidata.org/wiki/{entity.wikidata_id}"
								target="_blank"
								rel="noopener noreferrer"
							>{entity.wikidata_id} ↗</a>
						</div>
					{/if}
				</div>
			</div>
		</aside>

	</div>
</div>

<style>
	/* ── Header ──────────────────────────────────────── */
	.entity-header {
		background: var(--color-navy);
		color: white;
		padding: var(--space-12) var(--space-6) var(--space-10);
		position: relative;
		overflow: hidden;
	}

	.entity-header::before {
		content: '';
		position: absolute;
		inset: 0;
		background-image:
			linear-gradient(rgba(255, 255, 255, 0.022) 1px, transparent 1px),
			linear-gradient(90deg, rgba(255, 255, 255, 0.022) 1px, transparent 1px);
		background-size: 52px 52px;
		pointer-events: none;
	}

	.header-inner {
		position: relative;
		z-index: 1;
		max-width: var(--max-width);
		margin: 0 auto;
	}

	.header-meta {
		display: flex;
		gap: var(--space-3);
		align-items: center;
		margin-bottom: var(--space-4);
	}

	.type-badge {
		font-size: 0.625rem;
		font-weight: 700;
		letter-spacing: 0.12em;
		text-transform: uppercase;
		color: var(--color-text-faint);
		background: var(--color-border);
		padding: 0.2rem 0.6rem;
		border-radius: var(--radius-sm);
	}

	.entity-name {
		font-family: var(--font-serif);
		font-size: clamp(1.75rem, 4vw, 2.25rem);
		font-weight: 400;
		color: white;
		line-height: 1.2;
		margin-bottom: var(--space-4);
	}

	.entity-desc {
		font-size: 0.875rem;
		color: rgba(255, 255, 255, 0.6);
		max-width: 560px;
		line-height: 1.75;
		margin-bottom: var(--space-4);
	}

	.wikidata-link {
		display: inline-flex;
		align-items: center;
		gap: 0.25rem;
		font-size: 0.6875rem;
		font-family: var(--font-mono);
		color: var(--color-text-faint);
		margin-bottom: var(--space-4);
	}

	.wikidata-link:hover {
		color: var(--color-text-muted);
	}

	.claim-prompt {
		font-size: 0.75rem;
		color: rgba(255, 255, 255, 0.35);
		margin-top: var(--space-2);
	}

	.claim-link {
		color: rgba(255, 255, 255, 0.55);
		font-weight: 500;
		transition: color var(--transition-fast);
	}

	.claim-link:hover {
		color: white;
	}

	.header-rule {
		position: absolute;
		bottom: 0;
		left: 0;
		right: 0;
		height: 3px;
		background: linear-gradient(
			90deg,
			#14b8a6 0%,
			rgba(20, 184, 166, 0.25) 50%,
			transparent 100%
		);
	}

	/* ── Body ────────────────────────────────────────── */
	.entity-body {
		padding: var(--space-12) var(--space-6) var(--space-20);
	}

	.body-inner {
		max-width: var(--max-width);
		margin: 0 auto;
		display: grid;
		grid-template-columns: 1fr 280px;
		gap: var(--space-10);
	}

	@media (max-width: 800px) {
		.body-inner { grid-template-columns: 1fr; }
	}

	/* ── Timeline ────────────────────────────────────── */
	.col-header {
		display: flex;
		justify-content: space-between;
		align-items: baseline;
		gap: var(--space-4);
		margin-bottom: var(--space-8);
		flex-wrap: wrap;
	}

	.col-title {
		font-family: var(--font-serif);
		font-size: 1.375rem;
		font-weight: 400;
		color: var(--color-text);
	}

	.col-count {
		font-size: 0.75rem;
		color: var(--color-text-muted);
	}

	.empty {
		font-size: 0.875rem;
		color: var(--color-text-muted);
		padding: var(--space-10) 0;
		text-align: center;
		border: 1px dashed var(--color-border);
		border-radius: var(--radius-lg);
	}

	.timeline {
		list-style: none;
		display: flex;
		flex-direction: column;
	}

	.timeline-item {
		display: flex;
		gap: var(--space-5);
		position: relative;
		padding-bottom: var(--space-8);
	}

	.timeline-item:last-child {
		padding-bottom: 0;
	}

	.timeline-dot {
		width: 11px;
		height: 11px;
		border-radius: 50%;
		background: var(--dot-color);
		flex-shrink: 0;
		margin-top: 0.2rem;
	}

	.timeline-line {
		position: absolute;
		left: 5px;
		top: 16px;
		bottom: 0;
		width: 1px;
		background: var(--color-border);
	}

	.timeline-content {
		flex: 1;
		min-width: 0;
	}

	.event-meta {
		display: flex;
		align-items: center;
		gap: var(--space-3);
		margin-bottom: var(--space-2);
	}

	.event-date {
		font-size: 0.6875rem;
		font-weight: 600;
		color: var(--color-text-faint);
		font-family: var(--font-mono);
		letter-spacing: 0.04em;
	}

	.event-source {
		font-size: 0.625rem;
		font-weight: 600;
		letter-spacing: 0.08em;
		text-transform: uppercase;
		color: var(--color-text-faint);
		background: var(--color-border);
		padding: 0.125rem 0.4rem;
		border-radius: var(--radius-sm);
	}

	.event-title {
		font-size: 0.9375rem;
		font-weight: 600;
		color: var(--color-text);
		line-height: 1.45;
		margin-bottom: var(--space-2);
	}

	.event-desc {
		font-size: 0.8125rem;
		color: var(--color-text-muted);
		line-height: 1.6;
		margin-bottom: var(--space-3);
	}

	.event-footer {
		display: flex;
		align-items: center;
		gap: var(--space-4);
		flex-wrap: wrap;
	}

	.impact-badge {
		font-size: 0.6875rem;
		font-weight: 700;
		color: var(--impact-color);
		background: var(--impact-bg);
		padding: 0.2rem 0.625rem;
		border-radius: var(--radius-sm);
	}

	.source-link {
		display: inline-flex;
		align-items: center;
		gap: 0.2rem;
		font-size: 0.6875rem;
		font-family: var(--font-mono);
		color: var(--color-text-faint);
		transition: color var(--transition-fast);
	}

	.source-link:hover {
		color: var(--color-text-muted);
		text-decoration: underline;
	}

	/* ── Sidebar ─────────────────────────────────────── */
	.side-col {
		display: flex;
		flex-direction: column;
		gap: var(--space-4);
	}

	.sidebar-card {
		background: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-lg);
		padding: var(--space-5);
	}

	.sidebar-label {
		font-size: 0.625rem;
		font-weight: 700;
		letter-spacing: 0.1em;
		text-transform: uppercase;
		color: var(--color-text-faint);
		margin-bottom: var(--space-4);
	}

	.sidebar-hint {
		font-size: 0.75rem;
		color: var(--color-text-muted);
		line-height: 1.55;
	}

	.info-rows {
		display: flex;
		flex-direction: column;
	}

	.info-row {
		display: grid;
		grid-template-columns: 80px 1fr;
		gap: var(--space-2);
		padding: var(--space-2) 0;
		border-bottom: 1px solid var(--color-border);
	}

	.info-key {
		font-size: 0.75rem;
		font-weight: 600;
		color: var(--color-text-muted);
	}

	.info-val {
		font-size: 0.75rem;
		color: var(--color-text);
	}

	.info-link {
		font-size: 0.75rem;
		color: var(--color-accent);
		font-family: var(--font-mono);
	}

	.info-link:hover {
		text-decoration: underline;
	}
</style>
