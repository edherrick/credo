<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/state';
	import { resolve } from '$app/paths';
	import { goto } from '$app/navigation';
	import { auth } from '$lib/stores/auth';
	import { getMe } from '$lib/api';
	import { Tabs, PageHeader } from '$lib/components/ui';

	let { children } = $props();

	let ready = $state(false);

	const path = $derived(page.url.pathname);
	const meHref = resolve('/me');

	function isActive(href: string) {
		// Profile is the index — match exactly so it doesn't light up on child routes.
		return href === meHref ? path === meHref : path.startsWith(href);
	}

	const tabs = $derived(
		[
			{ label: 'Profile', href: meHref },
			{ label: 'Credos', href: resolve('/me/credos') },
			{ label: 'Following', href: resolve('/me/following') },
			{ label: 'Beliefs', href: resolve('/me/beliefs') },
			{ label: 'Settings', href: resolve('/me/settings') }
		].map((t) => ({ ...t, active: isActive(t.href) }))
	);

	// Single auth guard for the whole account area: ensure the store is populated
	// (hydrating from a stored token if needed), otherwise bounce to /login.
	onMount(async () => {
		const token = auth.loadFromStorage();
		if (!token) {
			goto(resolve('/login'));
			return;
		}
		if (!$auth) {
			try {
				const user = await getMe(token);
				auth.login(token, user);
			} catch {
				auth.logout();
				goto(resolve('/login'));
				return;
			}
		}
		ready = true;
	});
</script>

{#if ready && $auth}
	<PageHeader eyebrow="Your account" title={`@${$auth.user.username ?? 'you'}`} />

	<Tabs {tabs} variant="mono" aria-label="Account sections" />

	<main class="account-body">
		{@render children()}
	</main>
{:else}
	<div class="loading">Loading…</div>
{/if}

<style>
	.account-body {
		max-width: var(--max-width);
		margin: 0 auto;
		padding: var(--space-10) var(--space-6);
	}

	.loading {
		max-width: var(--max-width);
		margin: 0 auto;
		padding: var(--space-16) var(--space-6);
		color: var(--color-text-muted);
		font-size: 0.9rem;
	}
</style>
