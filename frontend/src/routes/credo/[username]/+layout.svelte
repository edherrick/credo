<script lang="ts">
	import { page } from '$app/state';
	import { resolve } from '$app/paths';
	import { auth } from '$lib/stores/auth';
	import { Pencil } from 'lucide-svelte';

	let { data, children } = $props();

	const credo = $derived(data.credo);
	const username = $derived(credo.username);
	const isOwner = $derived(!!$auth && $auth.user.id === credo.owner_id);

	const path = $derived(page.url.pathname);
	const isOverview = $derived(path === `/credo/${username}` || path === `/credo/${username}/`);
	const isMap = $derived(path.endsWith('/map'));
	const isTimeline = $derived(path.endsWith('/timeline'));
	const isBoard = $derived(path.endsWith('/board'));
	const canEdit = $derived(isOwner && !path.endsWith('/edit'));
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
			{/if}
		</div>
	</section>

	<!-- Tab bar -->
	<nav class="credo-tabs">
		<div class="tabs-inner">
			<a href={resolve(`/credo/${username}`)} class:active={isOverview}>Overview</a>
			<a href={resolve(`/credo/${username}/map`)} class:active={isMap}>Map</a>
			<a href={resolve(`/credo/${username}/timeline`)} class:active={isTimeline}>Timeline</a>
			<a href={resolve(`/credo/${username}/board`)} class:active={isBoard}>Board</a>
		</div>
	</nav>

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
		color: rgba(255, 255, 255, 0.3);
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
		color: rgba(255, 255, 255, 0.7);
		padding: 0.2rem 0.55rem;
		border: 1px solid rgba(255, 255, 255, 0.15);
		border-radius: var(--radius-md);
		transition:
			color var(--transition-fast),
			border-color var(--transition-fast),
			background var(--transition-fast);
	}

	.credo-edit-link:hover {
		color: white;
		border-color: rgba(255, 255, 255, 0.3);
		background: rgba(255, 255, 255, 0.06);
	}

	/* ── Tab bar ─────────────────────────────────────────── */
	.credo-tabs {
		background: var(--color-navy);
		/* Neutral cool divider — the red is reserved for the active-tab underline. */
		border-bottom: 1px solid var(--color-border-strong);
		position: sticky;
		top: var(--nav-height);
		z-index: 50;
	}

	.tabs-inner {
		max-width: var(--max-width);
		margin: 0 auto;
		padding: 0 var(--space-6);
		display: flex;
		gap: var(--space-1);
	}

	.credo-tabs a {
		display: block;
		padding: var(--space-3) var(--space-4);
		font-size: 0.875rem;
		font-weight: 500;
		color: rgba(255, 255, 255, 0.5);
		border-bottom: 2px solid transparent;
		margin-bottom: -1px;
		transition:
			color var(--transition-fast),
			border-color var(--transition-fast);
	}

	.credo-tabs a:hover {
		color: rgba(255, 255, 255, 0.85);
	}

	.credo-tabs a.active {
		color: white;
		border-bottom-color: var(--color-accent);
	}
</style>
