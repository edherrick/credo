<script lang="ts">
	import { register, login, getMe } from '$lib/api';
	import { auth } from '$lib/stores/auth';
	import { goto } from '$app/navigation';
	import { resolve } from '$app/paths';
	import { Button, Field } from '$lib/components/ui';

	let email = $state('');
	let password = $state('');
	let username = $state('');
	let error = $state<string | null>(null);
	let submitting = $state(false);

	async function handleSubmit(e: SubmitEvent) {
		e.preventDefault();
		error = null;
		submitting = true;
		try {
			await register(email, password, username);
			const token = await login(email, password);
			const user = await getMe(token.access_token);
			auth.login(token.access_token, user);
			goto(resolve('/me'));
		} catch (e) {
			error = e instanceof Error ? e.message : 'Registration failed';
		} finally {
			submitting = false;
		}
	}
</script>

<svelte:head><title>Register · Credo</title></svelte:head>

<main class="auth">
	<div class="auth-card">
		<h1 class="auth-title">Create your account</h1>
		<form onsubmit={handleSubmit}>
			<Field label="Username" bind:value={username} required placeholder="your-handle" />
			<Field label="Email" type="email" bind:value={email} required />
			<Field
				label="Password"
				type="password"
				bind:value={password}
				required
				hint="At least 8 characters."
			/>
			{#if error}<p class="auth-error">{error}</p>{/if}
			<Button type="submit" variant="primary" disabled={submitting}>
				{submitting ? 'Creating account…' : 'Register'}
			</Button>
		</form>
		<p class="auth-alt">Already have an account? <a href={resolve('/login')}>Log in</a></p>
	</div>
</main>

<style>
	.auth {
		max-width: 400px;
		margin: var(--space-16) auto;
		padding: 0 var(--space-6);
	}

	.auth-card {
		background: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-lg);
		padding: var(--space-8);
	}

	.auth-title {
		font-family: var(--font-serif);
		font-size: 1.5rem;
		font-weight: 400;
		line-height: 1.2;
		color: var(--color-text);
		margin-bottom: var(--space-6);
	}

	form {
		display: flex;
		flex-direction: column;
		gap: var(--space-5);
	}

	.auth-error {
		color: var(--color-accent);
		font-size: 0.85rem;
	}

	.auth-alt {
		margin-top: var(--space-6);
		font-size: 0.85rem;
		color: var(--color-text-muted);
	}

	.auth-alt a {
		color: var(--color-accent);
		font-weight: 510;
	}
</style>
