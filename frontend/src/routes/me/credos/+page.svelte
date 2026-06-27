<script lang="ts">
	import { resolve } from '$app/paths';
	import { auth } from '$lib/stores/auth';
	import { Plus } from 'lucide-svelte';
	import CredoCard from '$lib/components/CredoCard.svelte';
	import { Button, EmptyState } from '$lib/components/ui';
	import type { CredoSummary } from '$lib/types';

	let { data } = $props();

	const mine = $derived(
		(data.credos as CredoSummary[]).filter((c) => c.owner_id && c.owner_id === $auth?.user.id)
	);
</script>

<svelte:head><title>Your credos · Credo</title></svelte:head>

<div class="credos">
	<div class="credos-bar">
		<p class="count">{mine.length} {mine.length === 1 ? 'credo' : 'credos'}</p>
		<Button href={resolve('/credo/new')} variant="primary" size="sm">
			<Plus size={15} aria-hidden="true" /> New credo
		</Button>
	</div>

	{#if mine.length === 0}
		<EmptyState
			message="No credos yet — create your first to start tracking beliefs, agendas and outcomes."
		>
			<Button href={resolve('/credo/new')} variant="primary">
				<Plus size={15} aria-hidden="true" /> New credo
			</Button>
		</EmptyState>
	{:else}
		<div class="credo-grid">
			{#each mine as credo (credo.id)}
				<CredoCard {credo} />
			{/each}
		</div>
	{/if}
</div>

<style>
	.credos {
		display: flex;
		flex-direction: column;
		gap: var(--space-6);
	}

	.credos-bar {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: var(--space-4);
	}

	.count {
		font-family: var(--font-mono);
		font-size: 0.78rem;
		letter-spacing: 0.06em;
		text-transform: uppercase;
		color: var(--color-text-muted);
	}

	.credo-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
		gap: var(--space-5);
	}
</style>
