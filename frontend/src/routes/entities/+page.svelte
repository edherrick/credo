<script lang="ts">
	import { resolve } from '$app/paths';
	import { PageHeader } from '$lib/components/ui';
	import type { EntityDetail } from '$lib/types';

	let { data } = $props();
	const entities = $derived(data.entities as EntityDetail[]);

	const types = $derived([...new Set(entities.map((e) => e.type))].sort());

	let activeFilter = $state('all');

	const filtered = $derived(
		activeFilter === 'all' ? entities : entities.filter((e) => e.type === activeFilter)
	);
</script>

<svelte:head>
	<title>Entities — Credo</title>
</svelte:head>

<PageHeader
	eyebrow="The Commons"
	title="Entities"
	sub="Politicians, organizations, and corporations tracked in Credo."
/>

<div class="page">
	{#if types.length > 1}
		<div class="filters">
			<button
				class="pill"
				class:active={activeFilter === 'all'}
				onclick={() => (activeFilter = 'all')}>All</button
			>
			{#each types as type (type)}
				<button
					class="pill"
					class:active={activeFilter === type}
					data-type={type}
					onclick={() => (activeFilter = type)}>{type}</button
				>
			{/each}
		</div>
	{/if}

	{#if filtered.length === 0}
		<p class="empty">No entities on record yet.</p>
	{:else}
		<ul class="entity-list">
			{#each filtered as entity (entity.id)}
				<li>
					<a class="entity-card" href={resolve(`/entity/${entity.slug}`)}>
						<span class="type-badge" data-type={entity.type}>{entity.type}</span>
						<span class="entity-name">{entity.name}</span>
						{#if entity.description}
							<span class="entity-desc">{entity.description}</span>
						{/if}
					</a>
				</li>
			{/each}
		</ul>
	{/if}
</div>

<style>
	.page {
		max-width: 760px;
		margin: 0 auto;
		padding: var(--space-10) var(--space-6) var(--space-16);
	}

	/* ── Filters ─────────────────────────────────────────── */
	.filters {
		display: flex;
		gap: 0.5rem;
		flex-wrap: wrap;
		margin-bottom: 1.75rem;
	}

	.pill {
		font-size: 0.75rem;
		font-weight: 600;
		letter-spacing: 0.04em;
		text-transform: capitalize;
		padding: 0.3rem 0.9rem;
		border-radius: 999px;
		border: 1px solid var(--color-border);
		background: transparent;
		color: var(--color-text-muted);
		cursor: pointer;
		transition:
			color var(--transition-fast),
			border-color var(--transition-fast),
			background var(--transition-fast);
	}

	.pill:hover {
		color: var(--color-text);
		border-color: var(--color-border-strong);
	}

	.pill.active {
		color: var(--color-text);
		border-color: var(--color-border-strong);
		background: var(--color-surface);
	}

	.pill[data-type='politician'].active {
		border-color: var(--entity-politician);
		color: var(--entity-politician);
	}
	.pill[data-type='organization'].active {
		border-color: var(--entity-organization);
		color: var(--entity-organization);
	}
	.pill[data-type='corporation'].active {
		border-color: var(--entity-corporation);
		color: var(--entity-corporation);
	}

	/* ── List ────────────────────────────────────────────── */
	.empty {
		font-size: 0.9rem;
		color: var(--color-text-muted);
	}

	.entity-list {
		list-style: none;
		display: flex;
		flex-direction: column;
		gap: 0.75rem;
	}

	.entity-card {
		display: grid;
		grid-template-columns: auto 1fr;
		grid-template-rows: auto auto;
		column-gap: 0.875rem;
		align-items: center;
		padding: 1.1rem 1.5rem;
		background: var(--color-surface);
		border: 1px solid var(--color-border);
		border-left-width: 3px;
		border-radius: var(--radius-lg);
		text-decoration: none;
		transition: border-color var(--transition-fast);
	}

	.entity-card:hover {
		border-color: var(--color-border-strong);
	}

	/* Left accent by type */
	.entity-card:has(.type-badge[data-type='politician']) {
		border-left-color: var(--entity-politician);
	}
	.entity-card:has(.type-badge[data-type='organization']) {
		border-left-color: var(--entity-organization);
	}
	.entity-card:has(.type-badge[data-type='corporation']) {
		border-left-color: var(--entity-corporation);
	}

	/* ── Type badge ──────────────────────────────────────── */
	.type-badge {
		grid-row: 1;
		font-size: 0.62rem;
		font-weight: 700;
		letter-spacing: 0.1em;
		text-transform: uppercase;
		padding: 0.15rem 0.45rem;
		border-radius: var(--radius-sm);
		background: var(--color-border);
		color: var(--color-text-faint);
		white-space: nowrap;
	}

	.type-badge[data-type='politician'] {
		color: var(--entity-politician);
		background: color-mix(in srgb, var(--entity-politician) 12%, transparent);
	}
	.type-badge[data-type='organization'] {
		color: var(--entity-organization);
		background: color-mix(in srgb, var(--entity-organization) 12%, transparent);
	}
	.type-badge[data-type='corporation'] {
		color: var(--entity-corporation);
		background: color-mix(in srgb, var(--entity-corporation) 12%, transparent);
	}

	.entity-name {
		grid-row: 1;
		font-size: 1rem;
		font-weight: 600;
		color: var(--color-text);
	}

	.entity-desc {
		grid-column: 2;
		grid-row: 2;
		font-size: 0.83rem;
		color: var(--color-text-muted);
		line-height: 1.5;
		margin-top: 0.2rem;
	}
</style>
