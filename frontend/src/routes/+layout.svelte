<script lang="ts">
	import '../app.css';
	import favicon from '$lib/assets/favicon.svg';
	import { onMount } from 'svelte';
	import { auth } from '$lib/stores/auth';
	import { theme } from '$lib/stores/theme';
	import { getMe } from '$lib/api';
	import { page } from '$app/state';
	import { resolve } from '$app/paths';
	import { Sun, Moon } from 'lucide-svelte';

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
		href="https://fonts.googleapis.com/css2?family=Inter:ital,opsz,wght@0,14..32,100..900;1,14..32,100..900&family=DM+Serif+Display&display=swap"
		rel="stylesheet"
	/>
</svelte:head>

<div class="app">
	<header class="nav">
		<div class="nav-inner">
			<a href={resolve('/')} class="brand">
				<span class="brand-mark" aria-hidden="true">
					<svg width="22" height="22" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
						<!-- Hexagonal civic seal — community structure & legitimacy -->
						<path
							d="M12 2.5 L20.2 7.25 L20.2 16.75 L12 21.5 L3.8 16.75 L3.8 7.25 Z"
							stroke="rgba(247,248,248,0.38)"
							stroke-width="1.25"
							stroke-linejoin="round"
							fill="none"
						/>
						<!-- Rising trend — measurable change, evidence-backed progress -->
						<line x1="7.8" y1="16.2" x2="16.2" y2="8.2" stroke="#7170ff" stroke-width="1.3" stroke-linecap="round"/>
						<circle cx="7.8" cy="16.2" r="1.6" fill="#7170ff"/>
						<circle cx="12" cy="12.2" r="1.6" fill="#7170ff"/>
						<circle cx="16.2" cy="8.2" r="1.6" fill="#7170ff"/>
					</svg>
				</span>
				<span class="brand-name">Credo</span>
			</a>

			<nav class="nav-links">
				<a href={resolve('/explore')} class:active={currentPath.startsWith('/explore')}>Explore</a>
				<a href={resolve('/library')} class:active={currentPath.startsWith('/library')}>Library</a>
			</nav>

			<button
				class="theme-toggle"
				onclick={() => theme.toggle()}
				aria-label="Toggle theme"
				title={$theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
			>
				{#if $theme === 'dark'}
					<Sun size={16} />
				{:else}
					<Moon size={16} />
				{/if}
			</button>

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
		background: #0f1011;
		border-bottom: 1px solid rgba(255, 255, 255, 0.05);
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
		width: 22px;
		height: 22px;
		display: flex;
		align-items: center;
		justify-content: center;
		flex-shrink: 0;
	}

	.brand-name {
		font-size: 0.9375rem;
		font-weight: 510;
		color: #f7f8f8;
		letter-spacing: -0.02em;
	}

	.nav-links {
		display: flex;
		align-items: center;
		gap: 2px;
		flex: 1;
	}

	.nav-links a {
		color: #8a8f98;
		font-size: 0.8125rem;
		font-weight: 510;
		padding: 5px var(--space-3);
		border-radius: var(--radius-md);
		transition:
			color var(--transition-fast),
			background var(--transition-fast);
	}

	.nav-links a:hover {
		color: #f7f8f8;
		background: rgba(255, 255, 255, 0.05);
	}

	.nav-links a.active {
		color: #f7f8f8;
		background: rgba(255, 255, 255, 0.08);
	}

	.nav-auth {
		display: flex;
		align-items: center;
		gap: var(--space-2);
		flex-shrink: 0;
	}

	.btn-ghost {
		color: #8a8f98;
		font-size: 0.8125rem;
		font-weight: 510;
		padding: 5px var(--space-3);
		border-radius: var(--radius-md);
		background: rgba(255, 255, 255, 0.02);
		border: 1px solid rgba(255, 255, 255, 0.08);
		transition:
			color var(--transition-fast),
			background var(--transition-fast),
			border-color var(--transition-fast);
	}

	.btn-ghost:hover {
		color: #f7f8f8;
		background: rgba(255, 255, 255, 0.05);
		border-color: rgba(255, 255, 255, 0.12);
	}

	.btn-primary {
		background: var(--color-accent);
		color: white;
		font-size: 0.8125rem;
		font-weight: 510;
		padding: 5px var(--space-4);
		border-radius: var(--radius-md);
		border: none;
		transition: background var(--transition-fast);
	}

	.btn-primary:hover {
		background: var(--color-accent-dark);
	}

	.nav-user {
		display: flex;
		align-items: center;
		gap: var(--space-2);
		color: #8a8f98;
		font-size: 0.8125rem;
		font-weight: 510;
		padding: 4px var(--space-2);
		border-radius: var(--radius-md);
		transition: color var(--transition-fast);
	}

	.nav-user:hover {
		color: #f7f8f8;
	}

	.avatar {
		width: 24px;
		height: 24px;
		background: var(--color-accent);
		color: white;
		border-radius: 50%;
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 0.6875rem;
		font-weight: 590;
	}

	.theme-toggle {
		display: flex;
		align-items: center;
		justify-content: center;
		width: 28px;
		height: 28px;
		background: rgba(255, 255, 255, 0.02);
		border: 1px solid rgba(255, 255, 255, 0.08);
		border-radius: 50%;
		color: #62666d;
		transition:
			color var(--transition-fast),
			border-color var(--transition-fast),
			background var(--transition-fast);
		flex-shrink: 0;
	}

	.theme-toggle:hover {
		color: #f7f8f8;
		border-color: rgba(255, 255, 255, 0.15);
		background: rgba(255, 255, 255, 0.05);
	}

	.content {
		flex: 1;
	}
</style>
