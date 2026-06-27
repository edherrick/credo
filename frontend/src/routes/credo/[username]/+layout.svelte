<script lang="ts">
	import { page } from '$app/state';
	import { resolve } from '$app/paths';
	import { auth } from '$lib/stores/auth';
	import { getFollowing, followCredo, unfollowCredo } from '$lib/api';
	import { Tabs } from '$lib/components/ui';
	import { Pencil, Plus, Check } from 'lucide-svelte';

	let { data, children } = $props();

	const credo = $derived(data.credo);
	const username = $derived(credo.username);
	const isOwner = $derived(!!$auth && $auth.user.id === credo.owner_id);

	// ── Follow state ─────────────────────────────────────────────
	const token = $derived($auth?.token ?? null);
	const showFollow = $derived(!!token && !isOwner);
	let following = $state<boolean | null>(null); // null = unknown / loading
	let followBusy = $state(false);

	$effect(() => {
		const u = username;
		const t = token;
		if (!t || isOwner) {
			following = null;
			return;
		}
		let cancelled = false;
		getFollowing(t)
			.then((list) => {
				if (!cancelled) following = list.some((c) => c.username === u);
			})
			.catch(() => {
				if (!cancelled) following = null;
			});
		return () => {
			cancelled = true;
		};
	});

	async function toggleFollow() {
		if (!token || following === null) return;
		const next = !following;
		followBusy = true;
		try {
			if (next) await followCredo(token, username);
			else await unfollowCredo(token, username);
			following = next;
		} catch {
			// leave state unchanged on failure
		} finally {
			followBusy = false;
		}
	}

	const path = $derived(page.url.pathname);
	const isOverview = $derived(path === `/credo/${username}` || path === `/credo/${username}/`);
	const isMap = $derived(path.endsWith('/map'));
	const isTimeline = $derived(path.endsWith('/timeline'));
	const isBoard = $derived(path.endsWith('/board'));
	const canEdit = $derived(isOwner && !path.endsWith('/edit'));

	const tabs = $derived([
		{ label: 'Overview', href: resolve(`/credo/${username}`), active: isOverview },
		{ label: 'Map', href: resolve(`/credo/${username}/map`), active: isMap },
		{ label: 'Timeline', href: resolve(`/credo/${username}/timeline`), active: isTimeline },
		{ label: 'Board', href: resolve(`/credo/${username}/board`), active: isBoard }
	]);
</script>

<!-- Data tabs (!isOverview) fill the viewport; Overview scrolls. The bar + tabs are
     identical on every tab so the tabs never shift position. -->
<div class="credo-shell" class:fill={!isOverview}>
	<!-- Consistent credo bar (every tab) -->
	<section class="credo-bar">
		<div class="credo-bar-inner">
			<span class="credo-bar-handle">@{credo.username}</span>
			<span class="credo-bar-sep" aria-hidden="true">·</span>
			<span class="credo-bar-title">{credo.title}</span>
			{#if canEdit}
				<a href={resolve(`/credo/${username}/edit`)} class="credo-edit-link">
					<Pencil size={13} aria-hidden="true" /> Edit
				</a>
			{:else if showFollow}
				<button
					class="credo-follow-btn"
					class:following={following === true}
					onclick={toggleFollow}
					disabled={following === null || followBusy}
					aria-pressed={following === true}
				>
					{#if following}
						<Check size={13} aria-hidden="true" /> Following
					{:else}
						<Plus size={13} aria-hidden="true" /> Follow
					{/if}
				</button>
			{/if}
		</div>
	</section>

	<!-- Tab bar -->
	<Tabs {tabs} aria-label="Credo sections" />

	<div class="credo-content">
		{@render children()}
	</div>
</div>

<style>
	/* ── Shell ───────────────────────────────────────────── */
	.credo-shell {
		display: flex;
		flex-direction: column;
		min-height: calc(100vh - var(--nav-height));
	}

	/* Data tabs: pin to the viewport so children fill it (no page scroll, no magic number). */
	.credo-shell.fill {
		height: calc(100vh - var(--nav-height));
	}

	.credo-content {
		flex: 1;
		min-height: 0;
	}

	/* ── Consistent credo bar (identical on every tab) ───── */
	.credo-bar {
		background: var(--color-navy);
		color: white;
	}

	.credo-bar-inner {
		max-width: var(--max-width);
		margin: 0 auto;
		padding: var(--space-3) var(--space-6);
		display: flex;
		align-items: center;
		gap: var(--space-2);
	}

	.credo-bar-handle {
		flex-shrink: 0;
		font-size: 0.72rem;
		font-weight: 600;
		letter-spacing: 0.08em;
		text-transform: uppercase;
		color: var(--color-accent);
	}

	.credo-bar-sep {
		color: var(--overlay-4);
	}

	.credo-bar-title {
		font-family: var(--font-serif);
		font-size: 1rem;
		font-weight: 400;
		color: white;
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
	}

	.credo-edit-link {
		margin-left: auto;
		flex-shrink: 0;
		display: inline-flex;
		align-items: center;
		gap: 0.3rem;
		font-size: 0.75rem;
		font-weight: 510;
		color: var(--text-on-navy);
		padding: 0.2rem 0.55rem;
		border: 1px solid var(--overlay-3);
		border-radius: var(--radius-md);
		transition:
			color var(--transition-fast),
			border-color var(--transition-fast),
			background var(--transition-fast);
	}

	.credo-edit-link:hover {
		color: white;
		border-color: var(--overlay-4);
		background: var(--overlay-2);
	}

	.credo-follow-btn {
		margin-left: auto;
		flex-shrink: 0;
		display: inline-flex;
		align-items: center;
		gap: 0.3rem;
		font-family: inherit;
		font-size: 0.75rem;
		font-weight: 510;
		color: white;
		background: var(--color-accent);
		padding: 0.25rem 0.65rem;
		border: 1px solid var(--color-accent);
		border-radius: var(--radius-md);
		cursor: pointer;
		transition:
			color var(--transition-fast),
			border-color var(--transition-fast),
			background var(--transition-fast);
	}

	.credo-follow-btn:hover:not(:disabled) {
		background: var(--color-accent-dark);
		border-color: var(--color-accent-dark);
	}

	/* Following = quiet outline state (the action is now "unfollow") */
	.credo-follow-btn.following {
		color: var(--text-on-navy);
		background: transparent;
		border-color: var(--overlay-3);
	}

	.credo-follow-btn.following:hover:not(:disabled) {
		color: white;
		border-color: var(--overlay-4);
		background: var(--overlay-2);
	}

	.credo-follow-btn:disabled {
		opacity: 0.6;
		cursor: default;
	}
</style>
