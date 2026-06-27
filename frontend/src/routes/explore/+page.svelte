<script lang="ts">
	import { resolve } from '$app/paths';
	import { auth } from '$lib/stores/auth';
	import { Plus } from 'lucide-svelte';
	import CredoCard from '$lib/components/CredoCard.svelte';
	import type { CredoSummary } from '$lib/types';

	let { data } = $props();
	const credos = $derived(data.credos as CredoSummary[]);
	const authed = $derived(!!$auth);
</script>

<svelte:head>
	<title>Explore · Credo</title>
</svelte:head>

<section class="page-header">
	<div class="page-header-inner">
		<div class="page-header-text">
			<h1 class="page-title">Explore</h1>
			<p class="page-sub">Browse credos built by the community</p>
		</div>
		{#if authed}
			<a href={resolve('/credo/new')} class="new-credo-btn">
				<Plus size={15} aria-hidden="true" /> New credo
			</a>
		{/if}
	</div>
</section>

<section class="section">
	<div class="section-inner">
		{#if credos.length === 0}
			<p class="empty">No credos yet.</p>
		{:else}
			<div class="credo-grid">
				{#each credos as credo (credo.id)}
					<CredoCard {credo} />
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
		display: flex;
		align-items: flex-end;
		justify-content: space-between;
		gap: var(--space-4);
	}

	.new-credo-btn {
		display: inline-flex;
		align-items: center;
		gap: 0.35rem;
		flex-shrink: 0;
		background: var(--color-accent);
		color: white;
		font-size: 0.85rem;
		font-weight: 510;
		padding: 0.5rem var(--space-4);
		border-radius: var(--radius-md);
		transition: background var(--transition-fast);
	}

	.new-credo-btn:hover {
		background: var(--color-accent-dark);
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
</style>
