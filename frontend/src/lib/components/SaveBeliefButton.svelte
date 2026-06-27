<script lang="ts">
	// Controlled Save/Saved toggle for a belief. The parent owns `saved` and updates
	// it via `onchange` (optimistic). Renders nothing when logged out.
	import { Plus, Check } from 'lucide-svelte';
	import { auth } from '$lib/stores/auth';
	import { saveBelief, unsaveBelief } from '$lib/api';

	interface Props {
		beliefId: string;
		saved: boolean;
		onchange?: (saved: boolean) => void;
	}

	let { beliefId, saved, onchange }: Props = $props();

	let busy = $state(false);
	const token = $derived($auth?.token ?? null);

	async function toggle(e: MouseEvent) {
		e.stopPropagation();
		if (!token || busy) return;
		busy = true;
		const next = !saved;
		onchange?.(next); // optimistic
		try {
			if (next) await saveBelief(token, beliefId);
			else await unsaveBelief(token, beliefId);
		} catch {
			onchange?.(!next); // revert
		} finally {
			busy = false;
		}
	}
</script>

{#if token}
	<button class="save-btn" class:saved onclick={toggle} disabled={busy} aria-pressed={saved}>
		{#if saved}
			<Check size={13} aria-hidden="true" /> Saved
		{:else}
			<Plus size={13} aria-hidden="true" /> Save
		{/if}
	</button>
{/if}

<style>
	.save-btn {
		display: inline-flex;
		align-items: center;
		gap: 0.3rem;
		font-family: var(--font-mono);
		font-size: 0.7rem;
		font-weight: 600;
		letter-spacing: 0.04em;
		text-transform: uppercase;
		color: var(--color-text-muted);
		background: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-md);
		padding: 0.3rem 0.6rem;
		cursor: pointer;
		transition:
			color var(--transition-fast),
			border-color var(--transition-fast),
			background var(--transition-fast);
	}

	.save-btn:hover:not(:disabled) {
		color: var(--color-text);
		border-color: var(--color-border-strong);
	}

	.save-btn.saved {
		color: var(--color-accent);
		border-color: var(--color-accent);
		background: color-mix(in srgb, var(--color-accent) 12%, transparent);
	}

	.save-btn:disabled {
		opacity: 0.6;
		cursor: default;
	}
</style>
