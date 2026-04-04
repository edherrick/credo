<script lang="ts">
	import '../app.css';
	import favicon from '$lib/assets/favicon.svg';
	import { onMount } from 'svelte';
	import { auth } from '$lib/stores/auth';
	import { getMe } from '$lib/api';
	import { page } from '$app/state';
	import { resolve } from '$app/paths';

	let { children } = $props();

	const authState = $derived($auth);
	const currentPath = $derived(page.url.pathname);

	onMount(async () => {
		const token = auth.loadFromStorage();
		if (token && !$auth) {
			try {
				const user = await getMe(token);
				auth.login(token, user);
			} catch {
				auth.logout();
			}
		}
	});
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
	<link rel="preconnect" href="https://fonts.googleapis.com" />
	<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin="anonymous" />
	<link
		href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600&family=DM+Serif+Display&display=swap"
		rel="stylesheet"
	/>
</svelte:head>

<div class="app">
	<header class="nav">
		<div class="nav-inner">
			<a href={resolve('/')} class="brand">
				<span class="brand-mark">C</span>
				<span class="brand-name">Credo</span>
			</a>

			<nav class="nav-links">
				<a href={resolve('/')} class:active={currentPath === '/'}>Home</a>
				<a
					href={resolve('/map?fips=17031&metric=median_home_price')}
					class:active={currentPath === '/map'}>Map</a
				>
			</nav>

			<div class="nav-auth">
				{#if authState}
					<a href={resolve('/me')} class="nav-user">
						<span class="avatar">{authState.user.username?.[0]?.toUpperCase() ?? '?'}</span>
						<span>{authState.user.username}</span>
					</a>
				{:else}
					<a href={resolve('/login')} class="btn-ghost">Log in</a>
					<a href={resolve('/register')} class="btn-primary">Register</a>
				{/if}
			</div>
		</div>
	</header>

	<main class="content">
		{@render children()}
	</main>
</div>

<style>
	.app {
		min-height: 100vh;
		display: flex;
		flex-direction: column;
	}

	/* ── Nav ─────────────────────────────────────── */
	.nav {
		position: sticky;
		top: 0;
		z-index: 100;
		background: var(--color-navy);
		border-bottom: 1px solid rgba(255, 255, 255, 0.06);
		height: var(--nav-height);
	}

	.nav-inner {
		max-width: var(--max-width);
		margin: 0 auto;
		padding: 0 var(--space-6);
		height: 100%;
		display: flex;
		align-items: center;
		gap: var(--space-8);
	}

	.brand {
		display: flex;
		align-items: center;
		gap: var(--space-2);
		flex-shrink: 0;
	}

	.brand-mark {
		width: 28px;
		height: 28px;
		background: var(--color-accent);
		color: white;
		border-radius: var(--radius-md);
		display: flex;
		align-items: center;
		justify-content: center;
		font-family: var(--font-serif);
		font-size: 1rem;
		line-height: 1;
	}

	.brand-name {
		font-family: var(--font-serif);
		font-size: 1.1rem;
		color: white;
		letter-spacing: 0.01em;
	}

	.nav-links {
		display: flex;
		align-items: center;
		gap: var(--space-1);
		flex: 1;
	}

	.nav-links a {
		color: rgba(255, 255, 255, 0.55);
		font-size: 0.875rem;
		font-weight: 500;
		padding: var(--space-2) var(--space-3);
		border-radius: var(--radius-md);
		transition:
			color var(--transition-fast),
			background var(--transition-fast);
	}

	.nav-links a:hover {
		color: white;
		background: rgba(255, 255, 255, 0.07);
	}

	.nav-links a.active {
		color: white;
		background: rgba(255, 255, 255, 0.1);
	}

	.nav-auth {
		display: flex;
		align-items: center;
		gap: var(--space-2);
		flex-shrink: 0;
	}

	.btn-ghost {
		color: rgba(255, 255, 255, 0.7);
		font-size: 0.875rem;
		font-weight: 500;
		padding: var(--space-2) var(--space-3);
		border-radius: var(--radius-md);
		transition: color var(--transition-fast);
	}

	.btn-ghost:hover {
		color: white;
	}

	.btn-primary {
		background: var(--color-accent);
		color: white;
		font-size: 0.875rem;
		font-weight: 500;
		padding: var(--space-2) var(--space-4);
		border-radius: var(--radius-md);
		transition: background var(--transition-fast);
	}

	.btn-primary:hover {
		background: var(--color-accent-dark);
	}

	.nav-user {
		display: flex;
		align-items: center;
		gap: var(--space-2);
		color: rgba(255, 255, 255, 0.8);
		font-size: 0.875rem;
		font-weight: 500;
		padding: var(--space-1) var(--space-2);
		border-radius: var(--radius-md);
		transition: color var(--transition-fast);
	}

	.nav-user:hover {
		color: white;
	}

	.avatar {
		width: 26px;
		height: 26px;
		background: var(--color-accent);
		color: white;
		border-radius: 50%;
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 0.75rem;
		font-weight: 600;
	}

	.content {
		flex: 1;
	}
</style>
