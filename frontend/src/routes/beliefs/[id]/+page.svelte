<script lang="ts">
	import { resolve } from '$app/paths';
	import { ArrowLeft } from 'lucide-svelte';
	import { auth } from '$lib/stores/auth';
	import { getSavedBeliefs, getCredos } from '$lib/api';
	import SaveBeliefButton from '$lib/components/SaveBeliefButton.svelte';
	import AddToCredo from '$lib/components/AddToCredo.svelte';
	import { Badge } from '$lib/components/ui';
	import type { Belief, CredoSummary } from '$lib/types';

	let { data } = $props();
	const belief = $derived(data.belief as Belief);

	const authed = $derived(!!$auth);
	let saved = $state(false);
	let ownedCredos = $state<CredoSummary[]>([]);

	// Load saved-state + owned credos once auth is available. $effect (not onMount)
	// because this public page can render before the root layout restores auth.
	let loaded = false;
	$effect(() => {
		const token = $auth?.token ?? null;
		if (!token || loaded) return;
		loaded = true;
		Promise.all([getSavedBeliefs(token), getCredos()])
			.then(([savedList, credos]) => {
				saved = savedList.some((b) => b.id === belief.id);
				ownedCredos = credos.filter((c) => c.owner_id && c.owner_id === $auth?.user.id);
			})
			.catch(() => {});
	});
</script>

<svelte:head><title>{belief.title} · Credo</title></svelte:head>

<article class="belief">
	<a href={resolve('/beliefs')} class="back">
		<ArrowLeft size={14} aria-hidden="true" /> All beliefs
	</a>

	<p class="eyebrow">{belief.category}</p>
	<h1 class="title">{belief.title}</h1>

	{#if belief.source || belief.canonical}
		<div class="badges">
			{#if belief.canonical}<Badge tone="accent">canonical</Badge>{/if}
			{#if belief.source}<Badge>{belief.source}</Badge>{/if}
		</div>
	{/if}

	<p class="statement">{belief.statement}</p>

	{#if authed}
		<div class="actions">
			<SaveBeliefButton beliefId={belief.id} {saved} onchange={(s) => (saved = s)} />
			<AddToCredo beliefId={belief.id} {ownedCredos} />
		</div>
	{/if}
</article>

<style>
	.belief {
		max-width: var(--max-width-text);
		margin: 0 auto;
		padding: var(--space-12) var(--space-6) var(--space-16);
		display: flex;
		flex-direction: column;
		gap: var(--space-4);
	}

	.back {
		display: inline-flex;
		align-items: center;
		gap: 0.3rem;
		font-size: 0.85rem;
		font-weight: 500;
		color: var(--color-text-muted);
		transition: color var(--transition-fast);
		margin-bottom: var(--space-2);
	}

	.back:hover {
		color: var(--color-text);
	}

	.eyebrow {
		font-family: var(--font-mono);
		font-size: 0.72rem;
		font-weight: 600;
		letter-spacing: 0.1em;
		text-transform: uppercase;
		color: var(--color-text-faint);
	}

	.title {
		font-family: var(--font-serif);
		font-size: clamp(1.6rem, 4vw, 2.4rem);
		font-weight: 400;
		line-height: 1.2;
		color: var(--color-text);
	}

	.badges {
		display: flex;
		gap: var(--space-2);
	}

	.statement {
		font-size: 1.05rem;
		line-height: 1.75;
		color: var(--color-text);
	}

	.actions {
		display: flex;
		align-items: center;
		gap: var(--space-3);
		flex-wrap: wrap;
		margin-top: var(--space-4);
		padding-top: var(--space-5);
		border-top: 1px solid var(--color-border);
	}
</style>
