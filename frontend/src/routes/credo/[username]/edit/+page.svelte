<script lang="ts">
	import { untrack } from 'svelte';
	import { goto } from '$app/navigation';
	import { resolve } from '$app/paths';
	import { auth } from '$lib/stores/auth';
	import { updateCredo, deleteCredo } from '$lib/api';

	let { data } = $props();
	const credo = $derived(data.credo);
	const authState = $derived($auth);
	const isOwner = $derived(!!authState && authState.user.id === credo.owner_id);

	// Seed the form once from the loaded credo; untrack documents that we intentionally
	// capture the initial value rather than reactively follow `data`.
	let title = $state(untrack(() => data.credo.title));
	let description = $state(untrack(() => data.credo.description ?? ''));
	let error = $state<string | null>(null);
	let submitting = $state(false);
	let deleting = $state(false);

	async function handleSubmit(e: SubmitEvent) {
		e.preventDefault();
		if (!isOwner || !authState) return;
		error = null;
		submitting = true;
		try {
			await updateCredo(authState.token, credo.username, {
				title: title.trim(),
				description: description.trim() || null
			});
			await goto(resolve(`/credo/${credo.username}`), { invalidateAll: true });
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to save changes';
			submitting = false;
		}
	}

	async function handleDelete() {
		if (!isOwner || !authState) return;
		if (!confirm(`Delete "${credo.title}"? This cannot be undone.`)) return;
		error = null;
		deleting = true;
		try {
			await deleteCredo(authState.token, credo.username);
			await goto(resolve('/explore'), { invalidateAll: true });
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to delete credo';
			deleting = false;
		}
	}
</script>

<svelte:head>
	<title>Edit {credo.title} · Credo</title>
</svelte:head>

<section class="section">
	<div class="form-wrap">
		{#if !isOwner}
			<div class="gate">
				<p>You don't have permission to edit this credo.</p>
				<a href={resolve(`/credo/${credo.username}`)} class="btn-ghost">Back to credo</a>
			</div>
		{:else}
			<form onsubmit={handleSubmit}>
				<label class="field">
					<span class="field-label">Handle</span>
					<input type="text" value={credo.username} disabled />
					<span class="field-hint">The handle can't be changed after creation.</span>
				</label>

				<label class="field">
					<span class="field-label">Title</span>
					<input type="text" bind:value={title} required />
				</label>

				<label class="field">
					<span class="field-label">Description <span class="optional">(optional)</span></span>
					<textarea bind:value={description} rows="4"></textarea>
				</label>

				{#if error}
					<p class="error">{error}</p>
				{/if}

				<div class="form-actions">
					<button
						type="button"
						class="btn-danger"
						onclick={handleDelete}
						disabled={deleting || submitting}
					>
						{deleting ? 'Deleting…' : 'Delete'}
					</button>
					<div class="form-actions-right">
						<a href={resolve(`/credo/${credo.username}`)} class="btn-ghost">Cancel</a>
						<button type="submit" class="btn-primary" disabled={submitting || deleting || !title.trim()}>
							{submitting ? 'Saving…' : 'Save changes'}
						</button>
					</div>
				</div>
			</form>
		{/if}
	</div>
</section>

<style>
	.section {
		padding: var(--space-12) var(--space-6);
	}

	.form-wrap {
		max-width: 560px;
		margin: 0 auto;
	}

	form {
		display: flex;
		flex-direction: column;
		gap: var(--space-6);
	}

	.field {
		display: flex;
		flex-direction: column;
		gap: var(--space-2);
	}

	.field-label {
		font-size: 0.85rem;
		font-weight: 510;
		color: var(--color-text);
	}

	.optional {
		font-weight: 400;
		color: var(--color-text-faint);
	}

	input,
	textarea {
		width: 100%;
		padding: 0.6rem 0.75rem;
		font: inherit;
		font-size: 0.9rem;
		color: var(--color-text);
		background: var(--color-bg);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-md);
		transition: border-color var(--transition-fast), box-shadow var(--transition-fast);
	}

	textarea {
		resize: vertical;
	}

	input:focus,
	textarea:focus {
		outline: none;
		border-color: var(--color-accent);
		box-shadow: var(--shadow-accent);
	}

	input:disabled {
		color: var(--color-text-faint);
		background: var(--color-surface);
		cursor: not-allowed;
	}

	.field-hint {
		font-size: 0.78rem;
		color: var(--color-text-muted);
	}

	.error {
		color: var(--color-accent);
		font-size: 0.85rem;
		margin: calc(-1 * var(--space-3)) 0 0;
	}

	.form-actions {
		display: flex;
		justify-content: space-between;
		align-items: center;
		gap: var(--space-3);
	}

	.form-actions-right {
		display: flex;
		gap: var(--space-3);
		align-items: center;
	}

	.gate {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: var(--space-4);
		padding: var(--space-12) var(--space-6);
		text-align: center;
		color: var(--color-text-muted);
	}

	.btn-primary {
		background: var(--color-accent);
		color: white;
		font-size: 0.85rem;
		font-weight: 510;
		padding: 0.55rem var(--space-5);
		border-radius: var(--radius-md);
		border: none;
		cursor: pointer;
		transition: background var(--transition-fast);
	}

	.btn-primary:hover {
		background: var(--color-accent-dark);
	}

	.btn-primary:disabled {
		opacity: 0.55;
		cursor: not-allowed;
	}

	.btn-ghost {
		color: var(--color-text-muted);
		font-size: 0.85rem;
		font-weight: 510;
		padding: 0.55rem var(--space-4);
		border-radius: var(--radius-md);
		border: 1px solid var(--color-border);
		background: var(--color-bg);
		transition: border-color var(--transition-fast), color var(--transition-fast);
	}

	.btn-ghost:hover {
		color: var(--color-text);
		border-color: var(--color-border-strong);
	}

	.btn-danger {
		color: var(--color-accent);
		font-size: 0.85rem;
		font-weight: 510;
		padding: 0.55rem var(--space-4);
		border-radius: var(--radius-md);
		border: 1px solid var(--color-border);
		background: var(--color-bg);
		cursor: pointer;
		transition: border-color var(--transition-fast), background var(--transition-fast);
	}

	.btn-danger:hover {
		border-color: var(--color-accent);
		background: var(--color-warn-bg);
	}

	.btn-danger:disabled {
		opacity: 0.55;
		cursor: not-allowed;
	}
</style>
