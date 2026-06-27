<script lang="ts">
	import { resolve } from '$app/paths';
	import { goto } from '$app/navigation';
	import { auth } from '$lib/stores/auth';
	import { theme } from '$lib/stores/theme';
	import { Button } from '$lib/components/ui';
	import { Sun, Moon } from 'lucide-svelte';

	function handleLogout() {
		auth.logout();
		goto(resolve('/'));
	}
</script>

<svelte:head><title>Settings · Credo</title></svelte:head>

<div class="settings">
	<section class="row">
		<div class="row-text">
			<h2 class="row-title">Appearance</h2>
			<p class="row-sub">Switch between light and dark.</p>
		</div>
		<Button variant="subtle" size="sm" onclick={() => theme.toggle()}>
			{#if $theme === 'dark'}
				<Sun size={15} aria-hidden="true" /> Light mode
			{:else}
				<Moon size={15} aria-hidden="true" /> Dark mode
			{/if}
		</Button>
	</section>

	<section class="row">
		<div class="row-text">
			<h2 class="row-title">Session</h2>
			<p class="row-sub">Signed in as {$auth?.user.email}.</p>
		</div>
		<Button variant="danger" size="sm" onclick={handleLogout}>Log out</Button>
	</section>
</div>

<style>
	.settings {
		display: flex;
		flex-direction: column;
		gap: var(--space-3);
		max-width: var(--max-width-text);
	}

	.row {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: var(--space-4);
		padding: var(--space-5) var(--space-6);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-lg);
		background: var(--color-surface);
	}

	.row-title {
		font-family: var(--font-serif);
		font-size: 1.05rem;
		font-weight: 400;
		color: var(--color-text);
	}

	.row-sub {
		font-size: 0.82rem;
		color: var(--color-text-muted);
		margin-top: 0.15rem;
	}
</style>
