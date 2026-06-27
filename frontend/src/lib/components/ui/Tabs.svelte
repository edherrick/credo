<script lang="ts">
	// Tab bar for the always-navy chrome (account sub-nav, credo lens). Renders a
	// sticky row of links with the active tab underlined in the accent. The caller
	// owns active detection and passes pre-resolve()'d hrefs.
	interface Tab {
		label: string;
		href: string;
		active?: boolean;
	}

	type Variant = 'sans' | 'mono';

	interface Props {
		tabs: Tab[];
		/** sans = section nav (credo lens); mono = uppercase labels (account). */
		variant?: Variant;
		'aria-label'?: string;
	}

	let { tabs, variant = 'sans', 'aria-label': ariaLabel }: Props = $props();
</script>

<nav class="tabs" aria-label={ariaLabel}>
	<div class="tabs-inner">
		{#each tabs as tab (tab.href)}
			<!-- eslint-disable-next-line svelte/no-navigation-without-resolve -- hrefs are pre-resolve()'d by the caller -->
			<a href={tab.href} class="tab" class:mono={variant === 'mono'} class:active={tab.active}>
				{tab.label}
			</a>
		{/each}
	</div>
</nav>

<style>
	.tabs {
		background: var(--color-navy);
		border-bottom: 1px solid var(--overlay-2);
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

	.tab {
		display: block;
		padding: var(--space-3) var(--space-4);
		font-size: 0.875rem;
		font-weight: 500;
		color: var(--text-on-navy);
		border-bottom: 2px solid transparent;
		margin-bottom: -1px;
		transition:
			color var(--transition-fast),
			border-color var(--transition-fast);
	}

	.tab.mono {
		font-family: var(--font-mono);
		font-size: 0.72rem;
		font-weight: 600;
		letter-spacing: 0.08em;
		text-transform: uppercase;
	}

	.tab:hover {
		color: white;
	}

	.tab.active {
		color: white;
		border-bottom-color: var(--color-accent);
	}
</style>
