<script lang="ts">
	import type { Snippet } from 'svelte';
	import PageHeader from '$lib/components/ui/PageHeader.svelte';

	// Shared presentation for a library building-block list (beliefs, issues, axes,
	// metrics). One source of truth for the navy header + card grid; each route maps
	// its data onto the generic Item shape.
	export interface BlockItem {
		id: string | number;
		title: string;
		desc?: string | null;
		tags?: (string | null | undefined)[];
		href?: string;
	}

	interface Props {
		eyebrow?: string;
		title: string;
		sub?: string;
		items: BlockItem[];
		empty?: string;
		/** optional controls (filters, search) rendered above the card list */
		toolbar?: Snippet;
		/** optional trailing control per card (e.g. a Save button) — non-link cards only */
		action?: Snippet<[BlockItem]>;
	}

	let {
		eyebrow = 'Library',
		title,
		sub,
		items,
		empty = 'Nothing here yet.',
		toolbar,
		action
	}: Props = $props();
</script>

{#snippet body(item: BlockItem)}
	{@const tags = (item.tags ?? []).filter(Boolean)}
	{#if tags.length}
		<div class="card-top">
			{#each tags as tag (tag)}<span class="tag">{tag}</span>{/each}
		</div>
	{/if}
	<h3 class="card-title">{item.title}</h3>
	{#if item.desc}<p class="card-desc">{item.desc}</p>{/if}
{/snippet}

<PageHeader {eyebrow} {title} {sub} />

<section class="list-section">
	<div class="list-inner">
		{#if toolbar}<div class="toolbar">{@render toolbar()}</div>{/if}
		{#if items.length === 0}
			<p class="empty">{empty}</p>
		{:else}
			<div class="card-list">
				{#each items as item (item.id)}
					{#if action}
						<div class="card has-action" class:card-clickable={!!item.href}>
							{#if item.href}
								<!-- eslint-disable-next-line svelte/no-navigation-without-resolve -- item.href is already resolve()'d by the caller -->
								<a href={item.href} class="card-main card-main-link">{@render body(item)}</a>
							{:else}
								<div class="card-main">{@render body(item)}</div>
							{/if}
							<div class="card-action">{@render action(item)}</div>
						</div>
					{:else if item.href}
						<!-- eslint-disable-next-line svelte/no-navigation-without-resolve -- item.href is already resolve()'d by the caller -->
						<a href={item.href} class="card card-link">{@render body(item)}</a>
					{:else}
						<div class="card">{@render body(item)}</div>
					{/if}
				{/each}
			</div>
		{/if}
	</div>
</section>

<style>
	.list-section {
		padding: var(--space-10) var(--space-6);
	}

	.list-inner {
		max-width: var(--max-width);
		margin: 0 auto;
	}

	.toolbar {
		margin-bottom: var(--space-6);
	}

	.empty {
		color: var(--color-text-muted);
		font-size: 0.9rem;
	}

	.card-list {
		display: flex;
		flex-direction: column;
		gap: var(--space-3);
		max-width: var(--max-width-text);
	}

	.card {
		border: 1px solid var(--color-border);
		border-radius: var(--radius-lg);
		padding: var(--space-5) var(--space-6);
		background: var(--color-bg);
		display: flex;
		flex-direction: column;
		gap: var(--space-2);
		color: inherit;
	}

	.card.has-action {
		flex-direction: row;
		align-items: flex-start;
		justify-content: space-between;
		gap: var(--space-4);
	}

	.card-main {
		display: flex;
		flex-direction: column;
		gap: var(--space-2);
		min-width: 0;
	}

	.card-main-link {
		color: inherit;
	}

	.card-action {
		flex-shrink: 0;
	}

	.card-link,
	.card-clickable {
		transition:
			border-color var(--transition-fast),
			box-shadow var(--transition-fast);
	}

	.card-link:hover,
	.card-clickable:hover {
		border-color: var(--color-accent);
		box-shadow: var(--shadow-accent);
	}

	.card-top {
		display: flex;
		align-items: center;
		gap: var(--space-2);
	}

	.card-title {
		font-size: 0.975rem;
		font-weight: 600;
		color: var(--color-text);
		line-height: 1.4;
	}

	.card-desc {
		font-size: 0.85rem;
		color: var(--color-text-muted);
		line-height: 1.6;
		display: -webkit-box;
		-webkit-box-orient: vertical;
		-webkit-line-clamp: 3;
		line-clamp: 3;
		overflow: hidden;
	}

	.tag {
		font-family: var(--font-mono);
		font-size: 0.7rem;
		font-weight: 600;
		letter-spacing: 0.06em;
		text-transform: uppercase;
		color: var(--color-text-faint);
	}
</style>
