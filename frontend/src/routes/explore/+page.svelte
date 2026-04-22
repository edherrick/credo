<script lang="ts">
	import { resolve } from '$app/paths';
	import type { CredoSummary } from '$lib/types';

	let { data } = $props();
	const credos = $derived(data.credos as CredoSummary[]);
</script>

<svelte:head>
	<title>Explore · Credo</title>
</svelte:head>

<section class="page-header">
	<div class="page-header-inner">
		<h1 class="page-title">Explore</h1>
		<p class="page-sub">Browse credos built by the community</p>
	</div>
</section>

<section class="section">
	<div class="section-inner">
		{#if credos.length === 0}
			<p class="empty">No credos yet.</p>
		{:else}
			<div class="credo-grid">
				{#each credos as credo (credo.id)}
					<a href={resolve(`/credo/${credo.username}`)} class="credo-card">
						<div class="credo-card-top">
							<span class="credo-username">@{credo.username}</span>
						</div>
						<h2 class="credo-title">{credo.title}</h2>
						{#if credo.description}
							<p class="credo-desc">{credo.description}</p>
						{/if}
					</a>
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
		border-bottom: 3px solid var(--color-accent);
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

	.section {
		padding: var(--space-12) var(--space-6);
	}

	.section-inner {
		max-width: var(--max-width);
		margin: 0 auto;
	}

	.empty {
		color: var(--color-text-muted);
		font-size: 0.9rem;
	}

	.credo-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
		gap: var(--space-5);
	}

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
