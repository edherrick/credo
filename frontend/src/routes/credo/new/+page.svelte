<script lang="ts">
	import { goto } from '$app/navigation';
	import { resolve } from '$app/paths';
	import { auth } from '$lib/stores/auth';
	import { createCredo } from '$lib/api';

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

<section class="page-header">
	<div class="page-header-inner">
		<h1 class="page-title">New credo</h1>
		<p class="page-sub">A credo is your worldview — beliefs, agendas, and the entities you hold accountable</p>
	</div>
</section>

<section class="section">
	<div class="form-wrap">
		{#if !authState}
			<div class="gate">
				<p>You need an account to create a credo.</p>
				<div class="gate-actions">
					<a href={resolve('/login')} class="btn-primary">Log in</a>
					<a href={resolve('/register')} class="btn-ghost">Register</a>
				</div>
			</div>
		{:else}
			<form onsubmit={handleSubmit}>
				<label class="field">
					<span class="field-label">Handle</span>
					<input
						type="text"
						bind:value={username}
						placeholder="chicago-housing"
						autocomplete="off"
						required
					/>
					<span class="field-hint">
						Lowercase letters, numbers, hyphens. Your credo will live at
						<code>/credo/{slug || '…'}</code>
					</span>
				</label>

				<label class="field">
					<span class="field-label">Title</span>
					<input type="text" bind:value={title} placeholder="Chicago Metro Housing Affordability" required />
				</label>

				<label class="field">
					<span class="field-label">Description <span class="optional">(optional)</span></span>
					<textarea
						bind:value={description}
						rows="4"
						placeholder="What this credo is about and what it's trying to change."
					></textarea>
				</label>

				{#if error}
					<p class="error">{error}</p>
				{/if}

				<div class="form-actions">
					<a href={resolve('/explore')} class="btn-ghost">Cancel</a>
					<button type="submit" class="btn-primary" disabled={submitting || !slug || !title.trim()}>
						{submitting ? 'Creating…' : 'Create credo'}
					</button>
				</div>
			</form>
		{/if}
	</div>
</section>

<style>
	.page-header {
		background: var(--color-navy);
		color: white;
		padding: var(--space-12) var(--space-6) var(--space-10);
		border-bottom: 3px solid var(--color-accent);
	}

	.page-header-inner {
		max-width: var(--max-width);
		margin: 0 auto;
	}

	.page-title {
		font-family: var(--font-serif);
		font-size: clamp(1.75rem, 4vw, 2.5rem);
		font-weight: 400;
		margin-bottom: var(--space-2);
	}

	.page-sub {
		font-size: 0.9rem;
		color: rgba(255, 255, 255, 0.55);
	}

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

	.field-hint {
		font-size: 0.78rem;
		color: var(--color-text-muted);
	}

	.field-hint code {
		font-family: var(--font-mono);
		font-size: 0.74rem;
		color: var(--color-accent);
	}

	.error {
		color: var(--color-accent);
		font-size: 0.85rem;
		margin: calc(-1 * var(--space-3)) 0 0;
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
</style>
