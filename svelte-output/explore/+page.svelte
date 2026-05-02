<script lang="ts">
	import { resolve } from '$app/paths';
	import type { CredoSummary } from '$lib/types';

	let { data } = $props();
	const credos = $derived(data.credos as CredoSummary[]);

	const topics = ['All', 'Housing', 'Transit', 'Healthcare', 'Climate', 'Safety'];
	let selectedTopic = $state('All');
	let searchQuery = $state('');
	let viewMode = $state<'grid' | 'list'>('grid');

	const filtered = $derived(
		credos.filter((c) => {
			const matchesSearch =
				!searchQuery ||
				c.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
				c.username.toLowerCase().includes(searchQuery.toLowerCase()) ||
				(c.description?.toLowerCase().includes(searchQuery.toLowerCase()) ?? false);
			return matchesSearch;
		})
	);
</script>

<svelte:head>
	<title>Explore · Credo</title>
</svelte:head>

<!-- Page header -->
<section class="page-header">
	<div class="page-header-inner">
		<h1 class="page-title">Explore</h1>
		<p class="page-sub">Browse community-built credos — grounded in evidence, open to all.</p>
	</div>
	<div class="header-rule"></div>
</section>

<!-- Search + filter bar -->
<div class="filter-bar">
	<div class="filter-bar-inner">
		<div class="search-wrap">
			<span class="search-icon" aria-hidden="true">⌕</span>
			<input
				type="search"
				class="search-input"
				placeholder="Search credos, topics, or locations…"
				bind:value={searchQuery}
			/>
		</div>
		<div class="topic-pills">
			{#each topics as topic}
				<button
					class="topic-pill"
					class:active={selectedTopic === topic}
					onclick={() => (selectedTopic = topic)}
				>{topic}</button>
			{/each}
		</div>
		<div class="view-toggle">
			<button
				class="view-btn"
				class:active={viewMode === 'grid'}
				onclick={() => (viewMode = 'grid')}
				aria-label="Grid view"
			>⊞</button>
			<button
				class="view-btn"
				class:active={viewMode === 'list'}
				onclick={() => (viewMode = 'list')}
				aria-label="List view"
			>≡</button>
		</div>
	</div>
</div>

<!-- Results -->
<section class="results">
	<div class="results-inner">
		<div class="results-meta">
			<span>Showing <strong>{filtered.length}</strong> credo{filtered.length === 1 ? '' : 's'}</span>
		</div>

		{#if filtered.length === 0}
			<p class="empty">No credos found{searchQuery ? ` for "${searchQuery}"` : ''}.</p>
		{:else if viewMode === 'grid'}
			<div class="credo-grid">
				{#each filtered as credo (credo.id)}
					<a href={resolve(`/credo/${credo.username}`)} class="credo-card">
						<div class="credo-username">@{credo.username}</div>
						<h2 class="credo-title">{credo.title}</h2>
						{#if credo.description}
							<p class="credo-desc">{credo.description}</p>
						{/if}
					</a>
				{/each}
			</div>
		{:else}
			<div class="credo-list">
				{#each filtered as credo (credo.id)}
					<a href={resolve(`/credo/${credo.username}`)} class="credo-list-item">
						<div>
							<div class="credo-username">@{credo.username}</div>
							<h2 class="credo-title-sm">{credo.title}</h2>
						</div>
						{#if credo.description}
							<p class="credo-desc-sm">{credo.description}</p>
						{/if}
						<span class="list-arrow" aria-hidden="true">→</span>
					</a>
				{/each}
			</div>
		{/if}
	</div>
</section>

<style>
	/* ── Header ──────────────────────────────────────── */
	.page-header {
		background: var(--color-navy);
		color: white;
		padding: var(--space-12) var(--space-6) var(--space-10);
		position: relative;
		overflow: hidden;
	}

	.page-header::before {
		content: '';
		position: absolute;
		inset: 0;
		background-image:
			linear-gradient(rgba(255, 255, 255, 0.022) 1px, transparent 1px),
			linear-gradient(90deg, rgba(255, 255, 255, 0.022) 1px, transparent 1px);
		background-size: 52px 52px;
		pointer-events: none;
	}

	.page-header-inner {
		position: relative;
		z-index: 1;
		max-width: var(--max-width);
		margin: 0 auto;
	}

	.page-title {
		font-family: var(--font-serif);
		font-size: clamp(1.75rem, 4vw, 2.5rem);
		font-weight: 400;
		margin-bottom: var(--space-2);
	}

	.page-sub {
		font-size: 0.875rem;
		color: rgba(255, 255, 255, 0.55);
	}

	.header-rule {
		position: absolute;
		bottom: 0;
		left: 0;
		right: 0;
		height: 3px;
		background: linear-gradient(
			90deg,
			var(--color-accent) 0%,
			var(--choropleth-2) 45%,
			transparent 100%
		);
	}

	/* ── Filter bar ──────────────────────────────────── */
	.filter-bar {
		background: var(--color-surface);
		border-bottom: 1px solid var(--color-border);
		padding: var(--space-4) var(--space-6);
		position: sticky;
		top: var(--nav-height);
		z-index: 40;
	}

	.filter-bar-inner {
		max-width: var(--max-width);
		margin: 0 auto;
		display: flex;
		gap: var(--space-3);
		align-items: center;
		flex-wrap: wrap;
	}

	.search-wrap {
		flex: 1;
		min-width: 200px;
		position: relative;
		display: flex;
		align-items: center;
	}

	.search-icon {
		position: absolute;
		left: 0.75rem;
		font-size: 1rem;
		color: var(--color-text-faint);
		pointer-events: none;
	}

	.search-input {
		width: 100%;
		background: var(--color-bg);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-md);
		padding: 0.5625rem 0.875rem 0.5625rem 2.25rem;
		font-size: 0.8125rem;
		color: var(--color-text);
		font-family: inherit;
		outline: none;
		transition: border-color var(--transition-fast);
	}

	.search-input::placeholder {
		color: var(--color-text-faint);
	}

	.search-input:focus {
		border-color: var(--color-accent);
	}

	.topic-pills {
		display: flex;
		gap: var(--space-2);
		flex-wrap: wrap;
	}

	.topic-pill {
		font-size: 0.75rem;
		font-weight: 500;
		padding: 0.375rem 0.875rem;
		border-radius: 99px;
		border: 1px solid var(--color-border);
		background: transparent;
		color: var(--color-text-muted);
		cursor: pointer;
		font-family: inherit;
		transition:
			border-color var(--transition-fast),
			color var(--transition-fast),
			background var(--transition-fast);
		white-space: nowrap;
	}

	.topic-pill:hover {
		border-color: var(--color-accent);
		color: var(--color-accent);
	}

	.topic-pill.active {
		background: rgba(240, 59, 32, 0.1);
		border-color: var(--color-accent);
		color: var(--color-accent);
	}

	.view-toggle {
		display: flex;
		gap: 4px;
		flex-shrink: 0;
	}

	.view-btn {
		width: 32px;
		height: 32px;
		border-radius: var(--radius-md);
		border: 1px solid var(--color-border);
		background: transparent;
		color: var(--color-text-muted);
		font-size: 0.875rem;
		cursor: pointer;
		font-family: inherit;
		display: flex;
		align-items: center;
		justify-content: center;
		transition: border-color var(--transition-fast), color var(--transition-fast), background var(--transition-fast);
	}

	.view-btn.active {
		border-color: var(--color-accent);
		color: var(--color-accent);
		background: rgba(240, 59, 32, 0.08);
	}

	/* ── Results ─────────────────────────────────────── */
	.results {
		padding: var(--space-8) var(--space-6) var(--space-16);
	}

	.results-inner {
		max-width: var(--max-width);
		margin: 0 auto;
	}

	.results-meta {
		font-size: 0.8125rem;
		color: var(--color-text-muted);
		margin-bottom: var(--space-6);
	}

	.results-meta strong {
		color: var(--color-text);
	}

	.empty {
		color: var(--color-text-muted);
		font-size: 0.875rem;
		padding: var(--space-12) 0;
		text-align: center;
	}

	/* Grid */
	.credo-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
		gap: var(--space-5);
	}

	.credo-card {
		display: flex;
		flex-direction: column;
		gap: var(--space-2);
		background: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-lg);
		padding: var(--space-6);
		transition:
			border-color var(--transition-base),
			box-shadow var(--transition-base),
			transform var(--transition-base);
	}

	.credo-card:hover {
		border-color: var(--color-accent);
		box-shadow: var(--shadow-accent);
		transform: translateY(-2px);
	}

	.credo-username {
		font-size: 0.625rem;
		font-weight: 700;
		letter-spacing: 0.1em;
		text-transform: uppercase;
		color: var(--color-accent);
		margin-bottom: var(--space-1);
	}

	.credo-title {
		font-family: var(--font-serif);
		font-size: 1.0625rem;
		font-weight: 400;
		color: var(--color-text);
		line-height: 1.35;
	}

	.credo-desc {
		font-size: 0.8125rem;
		color: var(--color-text-muted);
		line-height: 1.6;
		flex: 1;
	}

	/* List */
	.credo-list {
		display: flex;
		flex-direction: column;
		gap: 2px;
	}

	.credo-list-item {
		display: flex;
		align-items: center;
		gap: var(--space-6);
		padding: var(--space-4) var(--space-5);
		background: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-md);
		transition: border-color var(--transition-fast), background var(--transition-fast);
	}

	.credo-list-item:hover {
		border-color: var(--color-border-strong);
		background: var(--color-bg);
	}

	.credo-title-sm {
		font-size: 0.9375rem;
		font-weight: 600;
		color: var(--color-text);
		line-height: 1.3;
	}

	.credo-desc-sm {
		flex: 1;
		font-size: 0.8125rem;
		color: var(--color-text-muted);
		line-height: 1.5;
	}

	.list-arrow {
		color: var(--color-text-faint);
		font-size: 0.875rem;
		flex-shrink: 0;
	}
</style>
