<script lang="ts">
	import { onMount } from 'svelte';
	import { resolve } from '$app/paths';
	import { auth } from '$lib/stores/auth';
	import { getSavedBeliefs, getCredos, unsaveBelief } from '$lib/api';
	import { Button, EmptyState } from '$lib/components/ui';
	import AddToCredo from '$lib/components/AddToCredo.svelte';
	import { X } from 'lucide-svelte';
	import type { Belief, CredoSummary } from '$lib/types';

	let saved = $state<Belief[]>([]);
	let ownedCredos = $state<CredoSummary[]>([]);
	let loading = $state(true);

	const token = $derived($auth?.token ?? null);

	onMount(async () => {
		if (!token) return;
		try {
			const [savedRes, credosRes] = await Promise.all([getSavedBeliefs(token), getCredos()]);
			saved = savedRes;
			ownedCredos = credosRes.filter((c) => c.owner_id && c.owner_id === $auth?.user.id);
		} catch {
			saved = [];
		} finally {
			loading = false;
		}
	});

	async function remove(beliefId: string) {
		if (!token) return;
		try {
			await unsaveBelief(token, beliefId);
			saved = saved.filter((b) => b.id !== beliefId);
		} catch {
			// leave as-is
		}
	}
</script>

<svelte:head><title>Saved beliefs · Credo</title></svelte:head>

<div class="saved">
	{#if loading}
		<p class="loading">Loading…</p>
	{:else if saved.length === 0}
		<EmptyState
			message="No saved beliefs yet. Browse the library and save the ones you agree with."
		>
			<Button href={resolve('/beliefs')} variant="primary">Browse beliefs</Button>
		</EmptyState>
	{:else}
		<p class="count">{saved.length} saved {saved.length === 1 ? 'belief' : 'beliefs'}</p>
		<ul class="belief-list">
			{#each saved as belief (belief.id)}
				<li class="belief-card">
					<a class="belief-main" href={resolve(`/beliefs/${belief.id}`)}>
						<span class="tag">{belief.category}</span>
						<h3 class="belief-title">{belief.title}</h3>
						<p class="belief-statement">{belief.statement}</p>
					</a>
					<div class="belief-actions">
						<AddToCredo beliefId={belief.id} {ownedCredos} />
						<button class="remove" onclick={() => remove(belief.id)} aria-label="Remove from saved">
							<X size={14} aria-hidden="true" />
						</button>
					</div>
				</li>
			{/each}
		</ul>
		{#if ownedCredos.length === 0}
			<p class="hint">
				Create a credo to adopt these beliefs into it — <a href={resolve('/credo/new')}>new credo</a
				>.
			</p>
		{/if}
	{/if}
</div>

<style>
	.saved {
		display: flex;
		flex-direction: column;
		gap: var(--space-4);
		max-width: var(--max-width-text);
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

	.belief-list {
		list-style: none;
		display: flex;
		flex-direction: column;
		gap: var(--space-3);
	}

	.belief-card {
		display: flex;
		align-items: flex-start;
		justify-content: space-between;
		gap: var(--space-4);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-lg);
		padding: var(--space-5) var(--space-6);
		background: var(--color-bg);
	}

	.belief-main {
		display: flex;
		flex-direction: column;
		gap: var(--space-2);
		min-width: 0;
		color: inherit;
	}

	.belief-main:hover .belief-title {
		color: var(--color-accent);
	}

	.tag {
		font-family: var(--font-mono);
		font-size: 0.7rem;
		font-weight: 600;
		letter-spacing: 0.06em;
		text-transform: uppercase;
		color: var(--color-text-faint);
	}

	.belief-title {
		font-size: 0.975rem;
		font-weight: 600;
		color: var(--color-text);
		line-height: 1.4;
	}

	.belief-statement {
		font-size: 0.85rem;
		color: var(--color-text-muted);
		line-height: 1.6;
		display: -webkit-box;
		-webkit-box-orient: vertical;
		-webkit-line-clamp: 2;
		line-clamp: 2;
		overflow: hidden;
	}

	.belief-actions {
		display: flex;
		align-items: center;
		gap: var(--space-2);
		flex-shrink: 0;
	}

	.remove {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		width: 30px;
		height: 30px;
		color: var(--color-text-faint);
		background: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-md);
		cursor: pointer;
		transition:
			color var(--transition-fast),
			border-color var(--transition-fast);
	}

	.remove:hover {
		color: var(--color-accent);
		border-color: var(--color-accent);
	}

	.hint {
		font-size: 0.82rem;
		color: var(--color-text-muted);
	}

	.hint a {
		color: var(--color-accent);
		font-weight: 510;
	}
</style>
