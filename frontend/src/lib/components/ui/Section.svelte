<script lang="ts">
	import type { Snippet } from 'svelte';

	interface Props {
		title?: string;
		/** mono uppercase overline — the cartographic label voice */
		eyebrow?: string;
		sub?: string;
		/** raised surface background */
		alt?: boolean;
		children: Snippet;
	}

	let { title, eyebrow, sub, alt = false, children }: Props = $props();
</script>

<section class="section" class:alt>
	<div class="inner">
		{#if eyebrow || title || sub}
			<header class="head">
				{#if eyebrow}<div class="eyebrow">{eyebrow}</div>{/if}
				{#if title}<h2 class="title">{title}</h2>{/if}
				{#if sub}<p class="sub">{sub}</p>{/if}
			</header>
		{/if}
		{@render children()}
	</div>
</section>

<style>
	.section {
		padding: var(--space-16) var(--space-6);
	}

	.alt {
		background: var(--color-surface);
		border-top: 1px solid var(--color-border);
		border-bottom: 1px solid var(--color-border);
	}

	.inner {
		max-width: var(--max-width);
		margin: 0 auto;
	}

	.head {
		margin-bottom: var(--space-8);
	}

	.eyebrow {
		font-family: var(--font-mono);
		font-size: 0.68rem;
		font-weight: 600;
		letter-spacing: 0.12em;
		text-transform: uppercase;
		color: var(--color-text-faint);
		margin-bottom: var(--space-2);
	}

	.title {
		font-family: var(--font-serif);
		font-size: 1.6rem;
		font-weight: 400;
		line-height: 1.2;
		color: var(--color-text);
	}

	.sub {
		font-size: 0.9rem;
		color: var(--color-text-muted);
		margin-top: 0.35rem;
	}
</style>
