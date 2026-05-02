<script lang="ts">
	import { onMount } from 'svelte';
	import { auth } from '$lib/stores/auth';
	import { getMe } from '$lib/api';
	import { goto } from '$app/navigation';
	import type { User } from '$lib/types';
	import { resolve } from '$app/paths';

	let user = $state<User | null>(null);
	let loading = $state(true);
	let activeTab = $state<'beliefs' | 'metrics' | 'entities' | 'account'>('beliefs');

	onMount(async () => {
		let token: string | null = null;
		const unsubscribe = auth.subscribe((state) => {
			token = state?.token ?? null;
			user = state?.user ?? null;
		});
		unsubscribe();

		if (!token) token = auth.loadFromStorage();
		if (!token) { goto(resolve('/login')); return; }

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

	const initials = $derived(
		user?.username?.[0]?.toUpperCase() ?? user?.display_name?.[0]?.toUpperCase() ?? '?'
	);
</script>

<svelte:head>
	<title>My Credo · Credo</title>
</svelte:head>

{#if loading}
	<div class="loading">Loading…</div>
{:else if user}

<!-- Personal credo header -->
<div class="me-header">
	<div class="header-inner">
		<div class="header-left">
			<div class="header-identity">
				<div class="avatar-lg">{initials}</div>
				<div>
					<div class="header-eyebrow">My Credo</div>
					<h1 class="header-name">
						{user.display_name ?? user.username}
						<span class="header-handle">@{user.username}</span>
					</h1>
				</div>
			</div>
			<p class="header-desc">
				A civic record of my policy beliefs, the metrics I track, and the entities I hold accountable.
			</p>
		</div>
		<div class="header-actions">
			<button class="btn-primary" type="button">Edit credo</button>
			<button class="btn-outline" type="button">Share</button>
		</div>
	</div>
	<div class="header-rule"></div>
</div>

<!-- Tab bar -->
<nav class="me-tabs">
	<div class="tabs-inner">
		{#each [['beliefs','My Beliefs'],['metrics','Subscribed Metrics'],['entities','Watched Entities'],['account','Account']] as [id, label]}
			<button
				class="tab-btn"
				class:active={activeTab === id}
				onclick={() => (activeTab = id as typeof activeTab)}
			>{label}</button>
		{/each}
	</div>
</nav>

<!-- Content -->
<div class="me-content">
	<div class="content-inner">

		{#if activeTab === 'beliefs'}
		<div class="two-col">
			<div class="col-main">
				<!-- Beliefs -->
				<div class="section-head">
					<div>
						<h2 class="section-title">My Founding Beliefs</h2>
						<p class="section-sub">The principles that guide my policy positions</p>
					</div>
					<button class="btn-sm-accent" type="button">+ Add belief</button>
				</div>
				<p class="empty-state">No beliefs yet — add your founding principles to get started.</p>

				<!-- My credos -->
				<div class="section-head" style="margin-top: 3rem;">
					<h2 class="section-title">My Credos</h2>
					<a href={resolve('/credo/new')} class="btn-sm-outline">+ New credo</a>
				</div>
				<div class="credo-grid">
					<a href={resolve(`/credo/${user.username}`)} class="credo-card new-credo">
						<div class="new-credo-inner">
							<div class="new-credo-icon">+</div>
							<p>New credo</p>
						</div>
					</a>
				</div>
			</div>

			<div class="col-side">
				<!-- Quick stats -->
				<div class="sidebar-card">
					<h3 class="sidebar-label">Account</h3>
					<div class="account-rows">
						<div class="account-row">
							<span class="account-key">Username</span>
							<span class="account-val">@{user.username}</span>
						</div>
						<div class="account-row">
							<span class="account-key">Email</span>
							<span class="account-val">{user.email}</span>
						</div>
						<div class="account-row">
							<span class="account-key">Member since</span>
							<span class="account-val">{new Date(user.created_at).toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}</span>
						</div>
						<div class="account-row">
							<span class="account-key">Plan</span>
							<span class="account-val">Free · Open Source</span>
						</div>
					</div>
					<button class="btn-logout" onclick={handleLogout} type="button">Log out</button>
				</div>
			</div>
		</div>

		{:else if activeTab === 'metrics'}
		<div class="section-head">
			<div>
				<h2 class="section-title">Subscribed Metrics</h2>
				<p class="section-sub">Metrics you're tracking across your credos</p>
			</div>
			<button class="btn-sm-accent" type="button">+ Add metric</button>
		</div>
		<p class="empty-state">No metrics subscribed yet.</p>

		{:else if activeTab === 'entities'}
		<div class="section-head">
			<div>
				<h2 class="section-title">Watched Entities</h2>
				<p class="section-sub">Politicians, organizations, and corporations you're tracking</p>
			</div>
			<button class="btn-sm-accent" type="button">+ Watch entity</button>
		</div>
		<p class="empty-state">No entities watched yet.</p>

		{:else if activeTab === 'account'}
		<div class="account-page">
			<h2 class="section-title">Account Settings</h2>
			<div class="account-card">
				<div class="account-rows">
					<div class="account-row">
						<span class="account-key">Username</span>
						<span class="account-val">@{user.username}</span>
					</div>
					<div class="account-row">
						<span class="account-key">Email</span>
						<span class="account-val">{user.email}</span>
					</div>
					<div class="account-row">
						<span class="account-key">Member since</span>
						<span class="account-val">{new Date(user.created_at).toLocaleDateString()}</span>
					</div>
					<div class="account-row">
						<span class="account-key">Plan</span>
						<span class="account-val">Free · Open Source</span>
					</div>
				</div>
			</div>
			<button class="btn-logout" onclick={handleLogout} type="button">Log out</button>
		</div>
		{/if}

	</div>
</div>

{/if}

<style>
	.loading {
		display: flex;
		align-items: center;
		justify-content: center;
		min-height: 50vh;
		color: var(--color-text-muted);
		font-size: 0.875rem;
	}

	/* ── Header ────────────────────────────────────── */
	.me-header {
		background: var(--color-navy);
		color: white;
		padding: var(--space-10) var(--space-6) var(--space-9);
		position: relative;
		overflow: hidden;
	}

	.me-header::before {
		content: '';
		position: absolute;
		inset: 0;
		background-image:
			linear-gradient(rgba(255, 255, 255, 0.022) 1px, transparent 1px),
			linear-gradient(90deg, rgba(255, 255, 255, 0.022) 1px, transparent 1px);
		background-size: 52px 52px;
		pointer-events: none;
	}

	.header-inner {
		position: relative;
		z-index: 1;
		max-width: var(--max-width);
		margin: 0 auto;
		display: flex;
		justify-content: space-between;
		align-items: flex-end;
		gap: var(--space-6);
		flex-wrap: wrap;
	}

	.header-identity {
		display: flex;
		align-items: center;
		gap: var(--space-4);
		margin-bottom: var(--space-4);
	}

	.avatar-lg {
		width: 52px;
		height: 52px;
		border-radius: 50%;
		background: var(--color-accent);
		color: white;
		font-size: 1.25rem;
		font-weight: 600;
		display: flex;
		align-items: center;
		justify-content: center;
		flex-shrink: 0;
	}

	.header-eyebrow {
		font-size: 0.625rem;
		font-weight: 700;
		letter-spacing: 0.1em;
		text-transform: uppercase;
		color: var(--color-accent);
		margin-bottom: var(--space-2);
	}

	.header-name {
		font-family: var(--font-serif);
		font-size: 1.875rem;
		font-weight: 400;
		color: white;
		line-height: 1.2;
	}

	.header-handle {
		color: rgba(255, 255, 255, 0.4);
		font-size: 1.375rem;
	}

	.header-desc {
		font-size: 0.875rem;
		color: rgba(255, 255, 255, 0.55);
		max-width: 520px;
		line-height: 1.7;
	}

	.header-actions {
		display: flex;
		gap: var(--space-3);
		flex-shrink: 0;
	}

	.btn-primary {
		background: var(--color-accent);
		color: white;
		border: none;
		border-radius: var(--radius-md);
		padding: var(--space-2) var(--space-5);
		font-size: 0.8125rem;
		font-weight: 600;
		font-family: inherit;
		cursor: pointer;
		transition: background var(--transition-fast);
	}

	.btn-primary:hover {
		background: var(--color-accent-dark);
	}

	.btn-outline {
		border: 1px solid rgba(255, 255, 255, 0.15);
		color: rgba(255, 255, 255, 0.6);
		background: transparent;
		border-radius: var(--radius-md);
		padding: var(--space-2) var(--space-4);
		font-size: 0.8125rem;
		font-weight: 500;
		font-family: inherit;
		cursor: pointer;
		transition: border-color var(--transition-fast), color var(--transition-fast);
	}

	.btn-outline:hover {
		border-color: rgba(255, 255, 255, 0.3);
		color: white;
	}

	.header-rule {
		position: absolute;
		bottom: 0;
		left: 0;
		right: 0;
		height: 3px;
		background: linear-gradient(
			90deg,
			var(--color-accent) 0%,
			var(--choropleth-2) 45%,
			transparent 100%
		);
	}

	/* ── Tabs ───────────────────────────────────────── */
	.me-tabs {
		background: #0a1828;
		border-bottom: 1px solid rgba(255, 255, 255, 0.07);
		position: sticky;
		top: var(--nav-height);
		z-index: 40;
	}

	.tabs-inner {
		max-width: var(--max-width);
		margin: 0 auto;
		padding: 0 var(--space-6);
		display: flex;
		gap: var(--space-1);
	}

	.tab-btn {
		padding: var(--space-3) var(--space-4);
		font-size: 0.875rem;
		font-weight: 500;
		color: rgba(255, 255, 255, 0.4);
		background: transparent;
		border: none;
		border-bottom: 2px solid transparent;
		margin-bottom: -1px;
		cursor: pointer;
		font-family: inherit;
		transition: color var(--transition-fast), border-color var(--transition-fast);
		white-space: nowrap;
	}

	.tab-btn:hover {
		color: rgba(255, 255, 255, 0.75);
	}

	.tab-btn.active {
		color: white;
		border-bottom-color: var(--color-accent);
	}

	/* ── Content ────────────────────────────────────── */
	.me-content {
		padding: var(--space-12) var(--space-6) var(--space-20);
	}

	.content-inner {
		max-width: var(--max-width);
		margin: 0 auto;
	}

	.two-col {
		display: grid;
		grid-template-columns: 1fr 280px;
		gap: var(--space-10);
	}

	@media (max-width: 800px) {
		.two-col { grid-template-columns: 1fr; }
	}

	.section-head {
		display: flex;
		justify-content: space-between;
		align-items: center;
		gap: var(--space-4);
		margin-bottom: var(--space-8);
	}

	.section-title {
		font-family: var(--font-serif);
		font-size: 1.375rem;
		font-weight: 400;
		color: var(--color-text);
		margin-bottom: 0.2rem;
	}

	.section-sub {
		font-size: 0.8125rem;
		color: var(--color-text-muted);
	}

	.empty-state {
		font-size: 0.875rem;
		color: var(--color-text-muted);
		padding: var(--space-10) 0;
		border: 1px dashed var(--color-border);
		border-radius: var(--radius-lg);
		text-align: center;
	}

	.btn-sm-accent {
		background: var(--color-accent);
		color: white;
		border: none;
		border-radius: var(--radius-md);
		padding: var(--space-2) var(--space-4);
		font-size: 0.75rem;
		font-weight: 600;
		font-family: inherit;
		cursor: pointer;
		white-space: nowrap;
		flex-shrink: 0;
		transition: background var(--transition-fast);
	}

	.btn-sm-accent:hover {
		background: var(--color-accent-dark);
	}

	.btn-sm-outline {
		border: 1px solid var(--color-border);
		color: var(--color-text-muted);
		background: transparent;
		border-radius: var(--radius-md);
		padding: var(--space-2) var(--space-4);
		font-size: 0.75rem;
		font-weight: 600;
		font-family: inherit;
		cursor: pointer;
		white-space: nowrap;
		flex-shrink: 0;
		transition: border-color var(--transition-fast), color var(--transition-fast);
	}

	.btn-sm-outline:hover {
		border-color: var(--color-border-strong);
		color: var(--color-text);
	}

	/* Credo grid */
	.credo-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
		gap: var(--space-4);
	}

	.credo-card {
		background: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-lg);
		padding: var(--space-5);
		font-size: 0.875rem;
		color: var(--color-text);
		transition: border-color var(--transition-fast), transform var(--transition-fast);
	}

	.credo-card:hover {
		border-color: var(--color-accent);
		transform: translateY(-1px);
	}

	.new-credo {
		background: transparent;
		border-style: dashed;
		display: flex;
		align-items: center;
		justify-content: center;
		min-height: 120px;
	}

	.new-credo-inner {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: var(--space-3);
		color: var(--color-text-muted);
		font-size: 0.8125rem;
	}

	.new-credo-icon {
		width: 36px;
		height: 36px;
		border-radius: 50%;
		border: 2px dashed var(--color-border);
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 1.25rem;
		color: var(--color-text-faint);
	}

	/* Sidebar */
	.sidebar-card {
		background: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-lg);
		padding: var(--space-5);
	}

	.sidebar-label {
		font-size: 0.625rem;
		font-weight: 700;
		letter-spacing: 0.1em;
		text-transform: uppercase;
		color: var(--color-text-faint);
		margin-bottom: var(--space-4);
	}

	.account-rows {
		display: flex;
		flex-direction: column;
	}

	.account-row {
		display: grid;
		grid-template-columns: 100px 1fr;
		gap: var(--space-2);
		padding: var(--space-2) 0;
		border-bottom: 1px solid var(--color-border);
	}

	.account-key {
		font-size: 0.75rem;
		font-weight: 600;
		color: var(--color-text-muted);
	}

	.account-val {
		font-size: 0.75rem;
		color: var(--color-text);
		word-break: break-all;
	}

	.btn-logout {
		margin-top: var(--space-4);
		width: 100%;
		background: transparent;
		border: 1px solid var(--color-border);
		border-radius: var(--radius-md);
		padding: var(--space-2);
		font-size: 0.8125rem;
		color: var(--color-text-muted);
		font-family: inherit;
		cursor: pointer;
		text-align: center;
		transition: border-color var(--transition-fast), color var(--transition-fast);
	}

	.btn-logout:hover {
		border-color: var(--color-border-strong);
		color: var(--color-text);
	}

	.account-page {
		max-width: 500px;
	}

	.account-card {
		background: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-lg);
		padding: var(--space-5);
		margin: var(--space-6) 0 var(--space-6);
	}
</style>
