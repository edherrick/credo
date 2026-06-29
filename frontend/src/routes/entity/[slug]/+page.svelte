<script lang="ts">
	import { ExternalLink } from 'lucide-svelte';
	import type { EntityEvent } from '$lib/types';

	let { data } = $props();
	const entity = $derived(data.entity);

	const SOURCE_TYPE_LABELS: Record<string, string> = {
		government: 'Campaign site',
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
			month: 'long',
			day: 'numeric'
		});
	}
</script>

<svelte:head>
	<title>{entity.name} — Credo</title>
</svelte:head>

<div class="page">
	<header class="entity-header">
		<span class="type-badge">{entity.type}</span>
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
				Wikidata <ExternalLink size={12} />
			</a>
		{/if}
	</header>

	<section class="stances-section">
		<h2 class="section-heading">Policy Positions</h2>

		{#if entity.events.length === 0}
			<p class="empty">No positions on record yet.</p>
		{:else}
			<ul class="stance-list">
				{#each entity.events as ev (ev.id)}
					<li class="stance-card">
						<div class="stance-meta">
							{#if ev.event_date}
								<span class="stance-date">{formatDate(ev.event_date)}</span>
							{/if}
							<span class="stance-source-type">{sourceLabel(ev)}</span>
						</div>
						<h3 class="stance-title">{ev.title}</h3>
						{#if ev.description}
							<p class="stance-desc">{ev.description}</p>
						{/if}
						{#if ev.source_url}
							<!-- eslint-disable-next-line svelte/no-navigation-without-resolve -- external source URL -->
							<a class="stance-link" href={ev.source_url} target="_blank" rel="noopener noreferrer">
								View source <ExternalLink size={11} />
							</a>
						{/if}
					</li>
				{/each}
			</ul>
		{/if}
	</section>
</div>

<style>
	.page {
		max-width: 760px;
		margin: 0 auto;
		padding: 3rem 1.5rem 5rem;
	}

	/* ── Header ────────────────────────────────────────── */
	.entity-header {
		padding-bottom: 2rem;
		border-bottom: 1px solid var(--color-border);
		margin-bottom: 2.5rem;
		border-left: 4px solid var(--color-accent);
		padding-left: 1.25rem;
	}

	.type-badge {
		display: inline-block;
		font-size: 0.68rem;
		font-weight: 700;
		letter-spacing: 0.12em;
		text-transform: uppercase;
		color: var(--color-text-faint);
		margin-bottom: 0.6rem;
	}

	.entity-name {
		font-family: var(--font-serif);
		font-size: 2.25rem;
		font-weight: 400;
		color: var(--color-text);
		line-height: 1.2;
		margin-bottom: 0.75rem;
	}

	.entity-desc {
		font-size: 0.95rem;
		color: var(--color-text-muted);
		line-height: 1.65;
		margin-bottom: 1rem;
	}

	.wikidata-link {
		display: inline-flex;
		align-items: center;
		gap: 0.3rem;
		font-size: 0.72rem;
		font-family: var(--font-mono);
		color: var(--color-text-faint);
		text-decoration: none;
	}

	.wikidata-link:hover {
		color: var(--color-text-muted);
	}

	/* ── Section ────────────────────────────────────────── */
	.section-heading {
		font-size: 0.7rem;
		font-weight: 700;
		letter-spacing: 0.12em;
		text-transform: uppercase;
		color: var(--color-text-faint);
		margin-bottom: 1.5rem;
	}

	.empty {
		font-size: 0.9rem;
		color: var(--color-text-muted);
	}

	/* ── Stance cards ────────────────────────────────────── */
	.stance-list {
		list-style: none;
		display: flex;
		flex-direction: column;
		gap: 1rem;
	}

	.stance-card {
		background: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-lg);
		padding: 1.25rem 1.5rem;
		display: flex;
		flex-direction: column;
		gap: 0.4rem;
		transition: border-color var(--transition-fast);
	}

	.stance-card:hover {
		border-color: var(--color-border-strong);
	}

	.stance-meta {
		display: flex;
		align-items: center;
		gap: 0.6rem;
	}

	.stance-date {
		font-size: 0.72rem;
		color: var(--color-text-faint);
		font-family: var(--font-mono);
	}

	.stance-source-type {
		font-size: 0.65rem;
		font-weight: 600;
		letter-spacing: 0.08em;
		text-transform: uppercase;
		color: var(--color-text-faint);
		background: var(--color-border);
		padding: 0.1rem 0.4rem;
		border-radius: var(--radius-sm);
	}

	.stance-title {
		font-size: 0.95rem;
		font-weight: 600;
		color: var(--color-text);
		line-height: 1.35;
	}

	.stance-desc {
		font-size: 0.875rem;
		color: var(--color-text-muted);
		line-height: 1.6;
	}

	.stance-link {
		display: inline-flex;
		align-items: center;
		gap: 0.25rem;
		font-size: 0.72rem;
		font-family: var(--font-mono);
		color: var(--color-text-faint);
		text-decoration: none;
		margin-top: 0.2rem;
	}

	.stance-link:hover {
		color: var(--color-text-muted);
		text-decoration: underline;
	}
</style>
