<script lang="ts">
	import { onMount } from 'svelte';
	import { resolve } from '$app/paths';
	import { auth } from '$lib/stores/auth';
	import { getFollowing } from '$lib/api';
	import CredoCard from '$lib/components/CredoCard.svelte';
	import { Button, EmptyState } from '$lib/components/ui';
	import type { CredoSummary } from '$lib/types';

	let credos = $state<CredoSummary[]>([]);
	let loading = $state(true);

	// The /me layout guards auth, so $auth is populated by the time this renders.
	onMount(async () => {
		const token = $auth?.token;
		if (!token) return;
		try {
			credos = await getFollowing(token);
		} catch {
			credos = [];
		} finally {
			loading = false;
		}
	});
</script>

<svelte:head><title>Following · Credo</title></svelte:head>

<div class="following">
	{#if loading}
		<p class="loading">Loading…</p>
	{:else if credos.length === 0}
		<EmptyState message="You're not following any credos yet. Explore the community to find some.">
			<Button href={resolve('/explore')} variant="primary">Browse credos</Button>
		</EmptyState>
	{:else}
		<p class="count">Following {credos.length} {credos.length === 1 ? 'credo' : 'credos'}</p>
		<div class="credo-grid">
			{#each credos as credo (credo.id)}
				<CredoCard {credo} />
			{/each}
		</div>
	{/if}
</div>

<style>
	.following {
		display: flex;
		flex-direction: column;
		gap: var(--space-6);
	}

	.loading {
		color: var(--color-text-muted);
		font-size: 0.9rem;
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
