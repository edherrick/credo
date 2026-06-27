<script lang="ts">
	// Picker to adopt a belief into one of the user's owned credos (owner-scoped
	// write). Self-contained: reads the token from the auth store, shows a status
	// line after each attempt. Renders nothing if the user owns no credos.
	import { auth } from '$lib/stores/auth';
	import { addBeliefToCredo } from '$lib/api';
	import type { CredoSummary } from '$lib/types';

	interface Props {
		beliefId: string;
		ownedCredos: CredoSummary[];
	}

	let { beliefId, ownedCredos }: Props = $props();

	const token = $derived($auth?.token ?? null);
	let status = $state('');

	async function promote(e: Event) {
		const el = e.currentTarget as HTMLSelectElement;
		const username = el.value;
		el.value = '';
		if (!token || !username) return;
		try {
			await addBeliefToCredo(token, username, beliefId);
			status = `Added to @${username}`;
		} catch (err) {
			status = err instanceof Error ? err.message : 'Could not add';
		}
	}
</script>

{#if ownedCredos.length > 0}
	<div class="add-to-credo">
		<select aria-label="Add to a credo" onchange={promote}>
			<option value="">Add to credo…</option>
			{#each ownedCredos as c (c.id)}
				<option value={c.username}>@{c.username}</option>
			{/each}
		</select>
		{#if status}<span class="status">{status}</span>{/if}
	</div>
{/if}

<style>
	.add-to-credo {
		display: flex;
		align-items: center;
		gap: var(--space-2);
	}

	select {
		font-family: var(--font-sans);
		font-size: 0.8rem;
		color: var(--color-text);
		background: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-md);
		padding: 0.3rem var(--space-2);
		cursor: pointer;
	}

	select:hover {
		border-color: var(--color-border-strong);
	}

	.status {
		font-family: var(--font-mono);
		font-size: 0.72rem;
		color: var(--color-accent);
		white-space: nowrap;
	}
</style>
