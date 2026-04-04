<script lang="ts">
	import { login, getMe } from '$lib/api';
	import { auth } from '$lib/stores/auth';
	import { goto } from '$app/navigation';
	import { resolve } from '$app/paths';

	let email = $state('');
	let password = $state('');
	let error = $state<string | null>(null);
	let submitting = $state(false);

	async function handleSubmit(e: SubmitEvent) {
		e.preventDefault();
		error = null;
		submitting = true;
		try {
			const token = await login(email, password);
			const user = await getMe(token.access_token);
			auth.login(token.access_token, user);
			goto(resolve('/me'));
		} catch (e) {
			error = e instanceof Error ? e.message : 'Login failed';
		} finally {
			submitting = false;
		}
	}
</script>

<main>
	<h1>Log in</h1>
	<form onsubmit={handleSubmit}>
		<label>
			Email
			<input type="email" bind:value={email} required />
		</label>
		<label>
			Password
			<input type="password" bind:value={password} required />
		</label>
		{#if error}
			<p class="error">{error}</p>
		{/if}
		<button type="submit" disabled={submitting}>
			{submitting ? 'Logging in…' : 'Log in'}
		</button>
	</form>
	<p>No account? <a href={resolve('/register')}>Register</a></p>
</main>

<style>
	main {
		max-width: 400px;
		margin: 4rem auto;
		padding: 0 1rem;
		font-family: sans-serif;
	}
	form {
		display: flex;
		flex-direction: column;
		gap: 1rem;
	}
	label {
		display: flex;
		flex-direction: column;
		gap: 0.25rem;
		font-size: 0.9rem;
	}
	input {
		padding: 0.5rem;
		border: 1px solid #ccc;
		border-radius: 4px;
		font-size: 1rem;
	}
	button {
		padding: 0.6rem;
		background: #2171b5;
		color: white;
		border: none;
		border-radius: 4px;
		font-size: 1rem;
		cursor: pointer;
	}
	button:disabled {
		opacity: 0.6;
	}
	.error {
		color: #c00;
		font-size: 0.9rem;
	}
</style>
