<script lang="ts">
	import { page } from '$app/state';
	import { resolve } from '$app/paths';
	import type { Belief, Issue, Axis, Metric, EntityDetail } from '$lib/types';

	let { data } = $props();

	const beliefs = $derived(data.beliefs as Belief[]);
	const issues = $derived(data.issues as Issue[]);
	const axes = $derived(data.axes as Axis[]);
	const metrics = $derived(data.metrics as Metric[]);
	const entities = $derived(data.entities as EntityDetail[]);

	const TABS = ['beliefs', 'issues', 'metrics', 'axes', 'entities'] as const;
	type Tab = (typeof TABS)[number];

	const activeTab = $derived((page.url.searchParams.get('tab') ?? 'beliefs') as Tab);

	function tabHref(tab: Tab) {
		return resolve(`/library?tab=${tab}`);
	}
</script>

<svelte:head>
	<title>Library · Credo</title>
</svelte:head>

<section class="page-header">
	<div class="page-header-inner">
		<h1 class="page-title">Library</h1>
		<p class="page-sub">Shared components available to any credo</p>
	</div>
</section>

<nav class="tab-bar">
	<div class="tab-bar-inner">
		{#each TABS as tab}
			<a href={tabHref(tab)} class:active={activeTab === tab} class="tab-link">
				{tab.charAt(0).toUpperCase() + tab.slice(1)}
			</a>
		{/each}
	</div>
</nav>

<section class="section">
	<div class="section-inner">

		{#if activeTab === 'beliefs'}
			{#if beliefs.length === 0}
				<p class="empty">No beliefs in the library yet.</p>
			{:else}
				<ol class="belief-list">
					{#each beliefs as belief (belief.id)}
						<li class="belief-item">
							<div class="belief-body">
								<div class="belief-top">
									<p class="belief-title">{belief.title}</p>
									{#if belief.source}
										<span class="badge">{belief.source}</span>
									{/if}
									{#if belief.canonical}
										<span class="badge badge-canonical">canonical</span>
									{/if}
								</div>
								<p class="belief-statement">{belief.statement}</p>
								<span class="category-tag">{belief.category}</span>
							</div>
						</li>
					{/each}
				</ol>
			{/if}

		{:else if activeTab === 'issues'}
			{#if issues.length === 0}
				<p class="empty">No issues in the library yet.</p>
			{:else}
				<div class="card-list">
					{#each issues as issue (issue.id)}
						<div class="list-card">
							<div class="list-card-top">
								{#if issue.category}
									<span class="category-tag">{issue.category}</span>
								{/if}
								{#if issue.canonical}
									<span class="badge badge-canonical">canonical</span>
								{/if}
							</div>
							<h3 class="list-card-title">{issue.title}</h3>
							{#if issue.description}
								<p class="list-card-desc">{issue.description}</p>
							{/if}
						</div>
					{/each}
				</div>
			{/if}

		{:else if activeTab === 'metrics'}
			{#if metrics.length === 0}
				<p class="empty">No metrics in the library yet.</p>
			{:else}
				<div class="card-list">
					{#each metrics as metric (metric.id)}
						<div class="list-card">
							<div class="list-card-top">
								<span class="category-tag">{metric.unit}</span>
							</div>
							<h3 class="list-card-title">{metric.display_name}</h3>
							{#if metric.description}
								<p class="list-card-desc">{metric.description}</p>
							{/if}
							{#if metric.data_source}
								<p class="list-card-source">Source: {metric.data_source}</p>
							{/if}
						</div>
					{/each}
				</div>
			{/if}

		{:else if activeTab === 'axes'}
			{#if axes.length === 0}
				<p class="empty">No axes in the library yet.</p>
			{:else}
				<div class="card-list">
					{#each axes as axis (axis.id)}
						<div class="list-card">
							<div class="list-card-top">
								<span class="category-tag">{axis.family}</span>
								{#if axis.canonical}
									<span class="badge badge-canonical">canonical</span>
								{/if}
							</div>
							<h3 class="list-card-title">{axis.label}</h3>
							{#if axis.description}
								<p class="list-card-desc">{axis.description}</p>
							{/if}
						</div>
					{/each}
				</div>
			{/if}

		{:else if activeTab === 'entities'}
			{#if entities.length === 0}
				<p class="empty">No entities in the library yet.</p>
			{:else}
				<div class="card-list">
					{#each entities as entity (entity.id)}
						<a href={resolve(`/entity/${entity.slug ?? entity.id}`)} class="list-card list-card-link">
							<div class="list-card-top">
								<span class="category-tag">{entity.type}</span>
							</div>
							<h3 class="list-card-title">{entity.name}</h3>
							{#if entity.description}
								<p class="list-card-desc">{entity.description}</p>
							{/if}
						</a>
					{/each}
				</div>
			{/if}
		{/if}

	</div>
</section>

<style>
	.page-header {
		background: var(--color-navy);
		color: white;
		padding: var(--space-12) var(--space-6) var(--space-10);
	}

	.page-header-inner {
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
		font-size: 0.9rem;
		color: rgba(255, 255, 255, 0.55);
	}

	/* ── Tab bar ───────────────────────────────────── */
	.tab-bar {
		background: var(--color-navy);
		border-bottom: 1px solid rgba(255, 255, 255, 0.08);
		position: sticky;
		top: var(--nav-height);
		z-index: 50;
	}

	.tab-bar-inner {
		max-width: var(--max-width);
		margin: 0 auto;
		padding: 0 var(--space-6);
		display: flex;
		gap: var(--space-1);
	}

	.tab-link {
		display: block;
		padding: var(--space-3) var(--space-4);
		font-size: 0.875rem;
		font-weight: 500;
		color: rgba(255, 255, 255, 0.5);
		border-bottom: 2px solid transparent;
		margin-bottom: -1px;
		transition:
			color var(--transition-fast),
			border-color var(--transition-fast);
	}

	.tab-link:hover {
		color: rgba(255, 255, 255, 0.85);
	}

	.tab-link.active {
		color: white;
		border-bottom-color: var(--color-accent);
	}

	/* ── Content ───────────────────────────────────── */
	.section {
		padding: var(--space-10) var(--space-6);
	}

	.section-inner {
		max-width: var(--max-width);
		margin: 0 auto;
	}

	.empty {
		color: var(--color-text-muted);
		font-size: 0.9rem;
	}

	/* ── Beliefs list ──────────────────────────────── */
	.belief-list {
		list-style: none;
		padding: 0;
		margin: 0;
		display: flex;
		flex-direction: column;
		gap: var(--space-4);
		max-width: var(--max-width-text);
	}

	.belief-item {
		border: 1px solid var(--color-border);
		border-radius: var(--radius-lg);
		padding: var(--space-5) var(--space-6);
		background: var(--color-bg);
	}

	.belief-body {
		display: flex;
		flex-direction: column;
		gap: var(--space-2);
	}

	.belief-top {
		display: flex;
		align-items: center;
		flex-wrap: wrap;
		gap: var(--space-2);
	}

	.belief-title {
		font-size: 0.975rem;
		font-weight: 600;
		color: var(--color-text);
		flex: 1;
	}

	.belief-statement {
		font-size: 0.875rem;
		color: var(--color-text-muted);
		line-height: 1.65;
	}

	/* ── Generic card list ─────────────────────────── */
	.card-list {
		display: flex;
		flex-direction: column;
		gap: var(--space-3);
		max-width: var(--max-width-text);
	}

	.list-card {
		border: 1px solid var(--color-border);
		border-radius: var(--radius-lg);
		padding: var(--space-5) var(--space-6);
		background: var(--color-bg);
		display: flex;
		flex-direction: column;
		gap: var(--space-2);
	}

	.list-card-link {
		transition:
			border-color var(--transition-fast),
			box-shadow var(--transition-fast);
	}

	.list-card-link:hover {
		border-color: var(--color-accent);
		box-shadow: var(--shadow-accent);
	}

	.list-card-top {
		display: flex;
		align-items: center;
		gap: var(--space-2);
	}

	.list-card-title {
		font-size: 0.975rem;
		font-weight: 600;
		color: var(--color-text);
		line-height: 1.4;
	}

	.list-card-desc {
		font-size: 0.85rem;
		color: var(--color-text-muted);
		line-height: 1.6;
	}

	.list-card-source {
		font-size: 0.78rem;
		color: var(--color-text-faint);
	}

	/* ── Badges / tags ─────────────────────────────── */
	.badge {
		font-size: 0.68rem;
		font-weight: 600;
		letter-spacing: 0.07em;
		text-transform: uppercase;
		padding: 0.15rem 0.45rem;
		border-radius: var(--radius-sm);
		background: var(--color-border);
		color: var(--color-text-faint);
		flex-shrink: 0;
	}

	.badge-canonical {
		background: color-mix(in srgb, var(--color-accent) 12%, transparent);
		color: var(--color-accent);
	}

	.category-tag {
		font-size: 0.7rem;
		font-weight: 600;
		letter-spacing: 0.06em;
		text-transform: uppercase;
		color: var(--color-text-faint);
	}
</style>
