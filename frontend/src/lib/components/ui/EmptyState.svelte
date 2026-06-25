<script lang="ts">
	import type { Snippet } from 'svelte';

	interface Props {
		message: string;
		children?: Snippet;
	}

	let { message, children }: Props = $props();
</script>

<div class="empty">
	<p class="msg">{message}</p>
	{#if children}<div class="actions">{@render children()}</div>{/if}
</div>

<style>
	.empty {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: var(--space-4);
		padding: var(--space-16) var(--space-6);
		text-align: center;
	}

	.msg {
		color: var(--color-text-muted);
		font-size: 0.9rem;
	}

	.actions {
		display: flex;
		gap: var(--space-3);
	}
</style>
