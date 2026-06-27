<script lang="ts">
	import { resolve } from '$app/paths';
	import type { CredoSummary } from '$lib/types';

	interface Props {
		credo: CredoSummary;
	}

	let { credo }: Props = $props();
</script>

<a href={resolve(`/credo/${credo.username}`)} class="credo-card">
	<div class="credo-card-top">
		<span class="credo-username">@{credo.username}</span>
	</div>
	<h2 class="credo-title">{credo.title}</h2>
	{#if credo.description}
		<p class="credo-desc">{credo.description}</p>
	{/if}
</a>

<style>
	.credo-card {
		display: flex;
		flex-direction: column;
		gap: var(--space-2);
		background: var(--color-bg);
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

	.credo-card-top {
		margin-bottom: var(--space-1);
	}

	.credo-username {
		font-family: var(--font-mono);
		font-size: 0.72rem;
		font-weight: 600;
		letter-spacing: 0.08em;
		text-transform: uppercase;
		color: var(--color-accent);
	}

	.credo-title {
		font-family: var(--font-serif);
		font-size: 1.15rem;
		font-weight: 400;
		color: var(--color-text);
		line-height: 1.35;
	}

	.credo-desc {
		font-size: 0.82rem;
		color: var(--color-text-muted);
		line-height: 1.6;
	}
</style>
