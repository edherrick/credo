<script lang="ts">
	import { resolve } from '$app/paths';
	import { SvelteSet } from 'svelte/reactivity';
	import BlockList from '$lib/components/BlockList.svelte';
	import SaveBeliefButton from '$lib/components/SaveBeliefButton.svelte';
	import { Search } from 'lucide-svelte';
	import { auth } from '$lib/stores/auth';
	import { getSavedBeliefs } from '$lib/api';
	import type { Belief } from '$lib/types';

	let { data } = $props();
	const beliefs = $derived(data.beliefs as Belief[]);

	const categories = $derived([...new Set(beliefs.map((b) => b.category))].sort());

	let activeCategory = $state('all');
	let query = $state('');

	const authed = $derived(!!$auth);
	const token = $derived($auth?.token ?? null);
	const savedIds = new SvelteSet<string>();

	// Hydrate saved state once the token is available. An $effect (not onMount) is
	// required because this public page can render before the root layout has
	// restored auth from storage.
	let savedLoaded = false;
	$effect(() => {
		const t = token;
		if (!t || savedLoaded) return;
		savedLoaded = true;
		getSavedBeliefs(t)
			.then((saved) => {
				for (const b of saved) savedIds.add(b.id);
			})
			.catch(() => {});
	});

	function setSaved(id: string, saved: boolean) {
		if (saved) savedIds.add(id);
		else savedIds.delete(id);
	}

	const filtered = $derived(
		beliefs.filter((b) => {
			const catOk = activeCategory === 'all' || b.category === activeCategory;
			const q = query.trim().toLowerCase();
			const qOk = !q || b.title.toLowerCase().includes(q) || b.statement.toLowerCase().includes(q);
			return catOk && qOk;
		})
	);

	const items = $derived(
		filtered.map((b) => ({
			id: b.id,
			title: b.title,
			desc: b.statement,
			tags: [b.category, b.source, b.canonical ? 'canonical' : null],
			href: resolve(`/beliefs/${b.id}`)
		}))
	);
</script>

<svelte:head><title>Beliefs · Credo</title></svelte:head>

{#snippet saveBtn(item: { id: string | number })}
	{@const id = String(item.id)}
	<SaveBeliefButton beliefId={id} saved={savedIds.has(id)} onchange={(s) => setSaved(id, s)} />
{/snippet}

<BlockList
	title="Beliefs"
	sub="Founding axioms credos can adopt and interpret"
	{items}
	empty="No beliefs match your filter."
	action={authed ? saveBtn : undefined}
>
	{#snippet toolbar()}
		<div class="filters">
			<div class="chips">
				<button
					class="chip"
					class:active={activeCategory === 'all'}
					onclick={() => (activeCategory = 'all')}
				>
					All
				</button>
				{#each categories as cat (cat)}
					<button
						class="chip"
						class:active={activeCategory === cat}
						onclick={() => (activeCategory = cat)}
					>
						{cat}
					</button>
				{/each}
			</div>
			<div class="search">
				<Search size={15} aria-hidden="true" />
				<input
					type="search"
					placeholder="Search beliefs"
					bind:value={query}
					aria-label="Search beliefs"
				/>
			</div>
		</div>
		<p class="count">Showing {filtered.length} of {beliefs.length}</p>
	{/snippet}
</BlockList>

<style>
	.filters {
		display: flex;
		align-items: center;
		justify-content: space-between;
		flex-wrap: wrap;
		gap: var(--space-3);
	}

	.chips {
		display: flex;
		flex-wrap: wrap;
		gap: var(--space-2);
	}

	.chip {
		font-family: var(--font-mono);
		font-size: 0.7rem;
		font-weight: 600;
		letter-spacing: 0.06em;
		text-transform: uppercase;
		color: var(--color-text-muted);
		background: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-full);
		padding: 0.3rem 0.7rem;
		cursor: pointer;
		transition:
			color var(--transition-fast),
			border-color var(--transition-fast),
			background var(--transition-fast);
	}

	.chip:hover {
		color: var(--color-text);
		border-color: var(--color-border-strong);
	}

	.chip.active {
		color: white;
		background: var(--color-accent);
		border-color: var(--color-accent);
	}

	.search {
		display: flex;
		align-items: center;
		gap: var(--space-2);
		padding: 0.35rem var(--space-3);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-md);
		background: var(--color-bg);
		color: var(--color-text-faint);
	}

	.search:focus-within {
		border-color: var(--color-accent);
		color: var(--color-text-muted);
	}

	.search input {
		border: none;
		background: none;
		outline: none;
		color: var(--color-text);
		font-family: inherit;
		font-size: 0.85rem;
		width: 11rem;
		max-width: 40vw;
	}

	.search input::placeholder {
		color: var(--color-text-faint);
	}

	.count {
		margin-top: var(--space-3);
		font-family: var(--font-mono);
		font-size: 0.72rem;
		letter-spacing: 0.06em;
		text-transform: uppercase;
		color: var(--color-text-faint);
	}
</style>
