<script lang="ts">
	import type { Snippet } from 'svelte';

	// The navy page header used across the commons + account areas: a mono eyebrow,
	// a serif title, an optional sub, and an optional right-aligned actions slot.
	// Single source for the page-header look — re-theme it here, not per route.
	interface Props {
		title: string;
		eyebrow?: string;
		sub?: string;
		actions?: Snippet;
	}

	let { title, eyebrow, sub, actions }: Props = $props();
</script>

<section class="page-header">
	<div class="inner">
		<div class="text">
			{#if eyebrow}<p class="eyebrow">{eyebrow}</p>{/if}
			<h1 class="title">{title}</h1>
			{#if sub}<p class="sub">{sub}</p>{/if}
		</div>
		{#if actions}<div class="actions">{@render actions()}</div>{/if}
	</div>
</section>

<style>
	.page-header {
		background: var(--color-navy);
		color: white;
		padding: var(--space-12) var(--space-6) var(--space-10);
	}

	.inner {
		max-width: var(--max-width);
		margin: 0 auto;
		display: flex;
		align-items: flex-end;
		justify-content: space-between;
		gap: var(--space-4);
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

	.title {
		font-family: var(--font-serif);
		font-size: clamp(1.75rem, 4vw, 2.5rem);
		font-weight: 400;
		line-height: 1.1;
	}

	.sub {
		font-size: 0.9rem;
		color: var(--text-on-navy);
		margin-top: var(--space-2);
	}

	.actions {
		flex-shrink: 0;
	}
</style>
