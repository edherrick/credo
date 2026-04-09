<script lang="ts">
	import { onMount } from 'svelte';
	import { auth } from '$lib/stores/auth';
	import { getMe } from '$lib/api';
	import { goto } from '$app/navigation';
	import type { User } from '$lib/types';
	import { resolve } from '$app/paths';
	import { ArrowLeft } from 'lucide-svelte';

	let user = $state<User | null>(null);
	let loading = $state(true);

	onMount(async () => {
		// Try store first, then localStorage token
		let token: string | null = null;
		const unsubscribe = auth.subscribe((state) => {
			token = state?.token ?? null;
			user = state?.user ?? null;
		});
		unsubscribe();

		if (!token) {
			token = auth.loadFromStorage();
		}
		if (!token) {
			goto(resolve('/login'));
			return;
		}
		try {
			const fetched = await getMe(token);
			auth.login(token, fetched);
			user = fetched;
		} catch {
			auth.logout();
			goto(resolve('/login'));
		} finally {
			loading = false;
		}
	});

	function handleLogout() {
		auth.logout();
		goto(resolve('/'));
	}
</script>

<main>
	{#if loading}
		<p>Loading…</p>
	{:else if user}
		<h1>My Profile</h1>
		<dl>
			<dt>Username</dt>
			<dd>{user.username ?? '—'}</dd>
			<dt>Email</dt>
			<dd>{user.email}</dd>
			<dt>Member since</dt>
			<dd>{new Date(user.created_at).toLocaleDateString()}</dd>
		</dl>
		<button onclick={handleLogout}>Log out</button>
		<a href={resolve('/')} class="back-link"><ArrowLeft size={14} aria-hidden="true" /> Home</a>
	{/if}
</main>

<style>
	main {
		max-width: 500px;
		margin: var(--space-16) auto;
		padding: 0 var(--space-6);
	}

	h1 {
		font-family: var(--font-serif);
		font-size: 1.6rem;
		font-weight: 400;
		color: var(--color-text);
		margin-bottom: var(--space-8);
	}

	dl {
		display: grid;
		grid-template-columns: 120px 1fr;
		gap: var(--space-2) var(--space-4);
		margin-bottom: var(--space-8);
	}

	dt {
		font-weight: 600;
		color: var(--color-text-muted);
		font-size: 0.875rem;
	}

	dd {
		color: var(--color-text);
		font-size: 0.875rem;
	}

	button {
		padding: var(--space-2) var(--space-5);
		background: var(--color-accent);
		color: white;
		border: none;
		border-radius: var(--radius-md);
		cursor: pointer;
		font-family: inherit;
		font-size: 0.875rem;
		font-weight: 500;
		transition: background var(--transition-fast);
	}

	button:hover {
		background: var(--color-accent-dark);
	}

	.back-link {
		display: inline-flex;
		align-items: center;
		gap: 0.3rem;
		margin-top: var(--space-4);
		font-size: 0.85rem;
		font-weight: 500;
		color: var(--color-text-muted);
		transition: color var(--transition-fast);
	}

	.back-link:hover {
		color: var(--color-text);
	}
</style>
