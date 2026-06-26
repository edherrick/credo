<script lang="ts">
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
	}

	let { eyebrow = 'Library', title, sub, items, empty = 'Nothing here yet.' }: Props = $props();
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

<section class="page-header">
	<div class="page-header-inner">
		{#if eyebrow}<p class="eyebrow">{eyebrow}</p>{/if}
		<h1 class="page-title">{title}</h1>
		{#if sub}<p class="page-sub">{sub}</p>{/if}
	</div>
</section>

<section class="list-section">
	<div class="list-inner">
		{#if items.length === 0}
			<p class="empty">{empty}</p>
		{:else}
			<div class="card-list">
				{#each items as item (item.id)}
					{#if item.href}
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
	.page-header {
		background: var(--color-navy);
		color: white;
		padding: var(--space-12) var(--space-6) var(--space-10);
	}

	.page-header-inner {
		max-width: var(--max-width);
		margin: 0 auto;
	}

	.eyebrow {
		font-family: var(--font-mono);
		font-size: 0.68rem;
		font-weight: 600;
		letter-spacing: 0.12em;
		text-transform: uppercase;
		color: var(--text-on-navy);
		margin-bottom: var(--space-2);
	}

	.page-title {
		font-family: var(--font-serif);
		font-size: clamp(1.75rem, 4vw, 2.5rem);
		font-weight: 400;
		margin-bottom: var(--space-2);
	}

	.page-sub {
		font-size: 0.9rem;
		color: var(--text-on-navy);
	}

	.list-section {
		padding: var(--space-10) var(--space-6);
	}

	.list-inner {
		max-width: var(--max-width);
		margin: 0 auto;
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

	.card-link {
		transition:
			border-color var(--transition-fast),
			box-shadow var(--transition-fast);
	}

	.card-link:hover {
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
