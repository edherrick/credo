<script lang="ts">
	import { register, login, getMe } from '$lib/api';
	import { auth } from '$lib/stores/auth';
	import { goto } from '$app/navigation';
	import { resolve } from '$app/paths';

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

<main>
	<h1>Register</h1>
	<form onsubmit={handleSubmit}>
		<label>
			Username
			<input type="text" bind:value={username} required />
		</label>
		<label>
			Email
			<input type="email" bind:value={email} required />
		</label>
		<label>
			Password
			<input type="password" bind:value={password} required minlength={8} />
		</label>
		{#if error}
			<p class="error">{error}</p>
		{/if}
		<button type="submit" disabled={submitting}>
			{submitting ? 'Creating account…' : 'Register'}
		</button>
	</form>
	<p>Already have an account? <a href={resolve('/login')}>Log in</a></p>
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
