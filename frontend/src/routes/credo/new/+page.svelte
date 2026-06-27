<script lang="ts">
	import { goto } from '$app/navigation';
	import { resolve } from '$app/paths';
	import { auth } from '$lib/stores/auth';
	import { createCredo } from '$lib/api';
	import { Button, Field, PageHeader } from '$lib/components/ui';

	const authState = $derived($auth);

	let username = $state('');
	let title = $state('');
	let description = $state('');
	let error = $state<string | null>(null);
	let submitting = $state(false);

	// Live preview of the handle the server will store (it lowercases + trims).
	const slug = $derived(username.trim().toLowerCase());

	async function handleSubmit(e: SubmitEvent) {
		e.preventDefault();
		if (!authState) return;
		error = null;
		submitting = true;
		try {
			const credo = await createCredo(authState.token, {
				username: slug,
				title: title.trim(),
				description: description.trim() || null
			});
			await goto(resolve(`/credo/${credo.username}`));
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to create credo';
		} finally {
			submitting = false;
		}
	}
</script>

<svelte:head>
	<title>New credo · Credo</title>
</svelte:head>

<PageHeader
	title="New credo"
	sub="A credo is your worldview — beliefs, agendas, and the entities you hold accountable"
/>

<section class="section">
	<div class="form-wrap">
		{#if !authState}
			<div class="gate">
				<p>You need an account to create a credo.</p>
				<div class="gate-actions">
					<Button href={resolve('/login')} variant="primary">Log in</Button>
					<Button href={resolve('/register')} variant="ghost">Register</Button>
				</div>
			</div>
		{:else}
			<form onsubmit={handleSubmit}>
				<Field
					label="Handle"
					bind:value={username}
					placeholder="chicago-housing"
					required
					hint={`Lowercase letters, numbers, hyphens — lives at /credo/${slug || '…'}`}
				/>
				<Field
					label="Title"
					bind:value={title}
					placeholder="Chicago Metro Housing Affordability"
					required
				/>
				<Field
					label="Description"
					bind:value={description}
					multiline
					placeholder="What this credo is about and what it's trying to change."
				/>

				{#if error}<p class="error">{error}</p>{/if}

				<div class="form-actions">
					<Button href={resolve('/explore')} variant="ghost">Cancel</Button>
					<Button type="submit" variant="primary" disabled={submitting || !slug || !title.trim()}>
						{submitting ? 'Creating…' : 'Create credo'}
					</Button>
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
		justify-content: flex-end;
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

	.gate-actions {
		display: flex;
		gap: var(--space-3);
	}
</style>
