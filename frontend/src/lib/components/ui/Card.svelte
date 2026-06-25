<script lang="ts">
	import type { Snippet } from 'svelte';

	interface Props {
		href?: string;
		interactive?: boolean;
		children: Snippet;
	}

	let { href, interactive = false, children }: Props = $props();
</script>

{#if href}
	<a {href} class="card interactive">{@render children()}</a>
{:else}
	<div class="card" class:interactive>{@render children()}</div>
{/if}

<style>
	.card {
		display: block;
		background: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-lg);
		padding: var(--space-6);
		color: inherit;
	}

	.interactive {
		transition:
			border-color var(--transition-base),
			box-shadow var(--transition-base),
			transform var(--transition-base);
	}

	.interactive:hover {
		border-color: var(--color-accent);
		box-shadow: var(--shadow-accent);
		transform: translateY(-2px);
	}
</style>
