<script lang="ts">
	import { untrack } from 'svelte';
	import { goto } from '$app/navigation';
	import { resolve } from '$app/paths';
	import { auth } from '$lib/stores/auth';
	import { updateCredo, deleteCredo } from '$lib/api';
	import { Button, Field } from '$lib/components/ui';

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
				<Button href={resolve(`/credo/${credo.username}`)} variant="ghost">Back to credo</Button>
			</div>
		{:else}
			<form onsubmit={handleSubmit}>
				<Field
					label="Handle"
					value={credo.username}
					disabled
					hint="The handle can't be changed after creation."
				/>
				<Field label="Title" bind:value={title} required />
				<Field label="Description" bind:value={description} multiline />

				{#if error}<p class="error">{error}</p>{/if}

				<div class="form-actions">
					<Button variant="danger" onclick={handleDelete} disabled={deleting || submitting}>
						{deleting ? 'Deleting…' : 'Delete'}
					</Button>
					<div class="form-actions-right">
						<Button href={resolve(`/credo/${credo.username}`)} variant="ghost">Cancel</Button>
						<Button type="submit" variant="primary" disabled={submitting || deleting || !title.trim()}>
							{submitting ? 'Saving…' : 'Save changes'}
						</Button>
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

	.error {
		color: var(--color-accent);
		font-size: 0.85rem;
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
</style>
