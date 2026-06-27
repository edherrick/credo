<script lang="ts">
	import { resolve } from '$app/paths';
	import { auth } from '$lib/stores/auth';
	import { Plus } from 'lucide-svelte';
	import CredoCard from '$lib/components/CredoCard.svelte';
	import { Button, PageHeader } from '$lib/components/ui';
	import type { CredoSummary } from '$lib/types';

	let { data } = $props();
	const credos = $derived(data.credos as CredoSummary[]);
	const authed = $derived(!!$auth);
</script>

<svelte:head>
	<title>Explore · Credo</title>
</svelte:head>

<PageHeader title="Explore" sub="Browse credos built by the community">
	{#snippet actions()}
		{#if authed}
			<Button href={resolve('/credo/new')} variant="primary" size="sm">
				<Plus size={15} aria-hidden="true" /> New credo
			</Button>
		{/if}
	{/snippet}
</PageHeader>

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
