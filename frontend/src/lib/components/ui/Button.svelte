<script lang="ts">
	import type { Snippet } from 'svelte';

	type Variant = 'primary' | 'ghost' | 'subtle' | 'danger';
	type Size = 'sm' | 'md';

	interface Props {
		variant?: Variant;
		size?: Size;
		type?: 'button' | 'submit' | 'reset';
		href?: string;
		disabled?: boolean;
		title?: string;
		'aria-label'?: string;
		onclick?: (event: MouseEvent) => void;
		children: Snippet;
	}

	let {
		variant = 'ghost',
		size = 'md',
		type = 'button',
		href,
		disabled = false,
		title,
		'aria-label': ariaLabel,
		onclick,
		children
	}: Props = $props();
</script>

{#if href}
	<a
		{href}
		{title}
		aria-label={ariaLabel}
		class="btn"
		class:primary={variant === 'primary'}
		class:ghost={variant === 'ghost'}
		class:subtle={variant === 'subtle'}
		class:danger={variant === 'danger'}
		class:sm={size === 'sm'}
		class:disabled
	>
		{@render children()}
	</a>
{:else}
	<button
		{type}
		{disabled}
		{title}
		aria-label={ariaLabel}
		{onclick}
		class="btn"
		class:primary={variant === 'primary'}
		class:ghost={variant === 'ghost'}
		class:subtle={variant === 'subtle'}
		class:danger={variant === 'danger'}
		class:sm={size === 'sm'}
	>
		{@render children()}
	</button>
{/if}

<style>
	.btn {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		gap: var(--space-2);
		font-family: var(--font-sans);
		font-size: 0.85rem;
		font-weight: 510;
		padding: 0.5rem var(--space-4);
		border-radius: var(--radius-md);
		border: 1px solid transparent;
		cursor: pointer;
		white-space: nowrap;
		transition:
			background var(--transition-fast),
			border-color var(--transition-fast),
			color var(--transition-fast);
	}

	.sm {
		font-size: 0.78rem;
		padding: 0.3rem var(--space-3);
	}

	.btn:disabled,
	.btn.disabled {
		opacity: 0.55;
		cursor: not-allowed;
		pointer-events: none;
	}

	.btn:focus-visible {
		outline: none;
		box-shadow: var(--shadow-accent);
	}

	/* primary — the one place a solid accent appears (a live CTA) */
	.primary {
		background: var(--color-accent);
		color: white;
	}
	.primary:hover {
		background: var(--color-accent-dark);
	}

	/* ghost — default; quiet surface with a cool border */
	.ghost {
		background: var(--color-bg);
		color: var(--color-text);
		border-color: var(--color-border);
	}
	.ghost:hover {
		border-color: var(--color-border-strong);
	}

	/* subtle — text-only, for low-emphasis actions */
	.subtle {
		background: transparent;
		color: var(--color-text-muted);
	}
	.subtle:hover {
		color: var(--color-text);
		background: var(--color-surface);
	}

	/* danger — accent only on intent, not by default */
	.danger {
		background: var(--color-bg);
		color: var(--color-accent);
		border-color: var(--color-border);
	}
	.danger:hover {
		border-color: var(--color-accent);
		background: var(--color-warn-bg);
	}
</style>
