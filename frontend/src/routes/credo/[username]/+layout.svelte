<script lang="ts">
	import { page } from '$app/state';
	import { resolve } from '$app/paths';

	let { data, children } = $props();

	const credo = $derived(data.credo);
	const username = $derived(credo.username);

	const path = $derived(page.url.pathname);
	const isOverview = $derived(path === `/credo/${username}` || path === `/credo/${username}/`);
	const isMap = $derived(path.endsWith('/map'));
	const isTimeline = $derived(path.endsWith('/timeline'));
	const isBoard = $derived(path.endsWith('/board'));
</script>

<!-- Credo header -->
<section class="credo-header">
	<div class="credo-header-inner">
		<div class="credo-attribution">@{credo.username}</div>
		<h1 class="credo-title">{credo.title}</h1>
		{#if credo.description}
			<p class="credo-desc">{credo.description}</p>
		{/if}
	</div>
	<div class="credo-rule"></div>
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

{@render children()}

<style>
	/* ── Credo header ────────────────────────────────────── */
	.credo-header {
		background: var(--color-navy);
		color: white;
		padding: var(--space-14) var(--space-6) var(--space-12);
		position: relative;
		overflow: hidden;
	}

	.credo-header::before {
		content: '';
		position: absolute;
		inset: 0;
		background-image:
			linear-gradient(rgba(255, 255, 255, 0.022) 1px, transparent 1px),
			linear-gradient(90deg, rgba(255, 255, 255, 0.022) 1px, transparent 1px);
		background-size: 52px 52px;
		pointer-events: none;
	}

	.credo-header-inner {
		position: relative;
		z-index: 1;
		max-width: var(--max-width-text);
		margin: 0 auto;
	}

	.credo-attribution {
		font-size: 0.75rem;
		font-weight: 600;
		letter-spacing: 0.1em;
		text-transform: uppercase;
		color: var(--color-accent);
		margin-bottom: var(--space-3);
	}

	.credo-title {
		font-family: var(--font-serif);
		font-size: clamp(1.75rem, 4vw, 2.5rem);
		font-weight: 400;
		line-height: 1.2;
		margin-bottom: var(--space-4);
	}

	.credo-desc {
		font-size: 0.975rem;
		color: rgba(255, 255, 255, 0.6);
		max-width: 560px;
		line-height: 1.7;
	}

	.credo-rule {
		position: absolute;
		bottom: 0;
		left: 0;
		right: 0;
		height: 3px;
		background: linear-gradient(
			90deg,
			var(--color-accent) 0%,
			var(--choropleth-2) 50%,
			transparent 100%
		);
	}

	/* ── Tab bar ─────────────────────────────────────────── */
	.credo-tabs {
		background: var(--color-navy);
		border-bottom: 1px solid rgba(255, 255, 255, 0.08);
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
