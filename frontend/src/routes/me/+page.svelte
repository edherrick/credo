<script lang="ts">
	import { resolve } from '$app/paths';
	import { auth } from '$lib/stores/auth';
	import { Card } from '$lib/components/ui';
	import { ArrowRight } from 'lucide-svelte';
</script>

<svelte:head><title>Profile · Credo</title></svelte:head>

{#if $auth}
	<div class="profile">
		<Card>
			<dl class="details">
				<dt>Username</dt>
				<dd>{$auth.user.username ?? '—'}</dd>
				<dt>Email</dt>
				<dd>{$auth.user.email}</dd>
				<dt>Member since</dt>
				<dd>{new Date($auth.user.created_at).toLocaleDateString()}</dd>
			</dl>
		</Card>

		<a href={resolve('/me/credos')} class="next-card">
			<span>
				<span class="next-label">Your credos</span>
				<span class="next-sub">The credos you've created and maintain</span>
			</span>
			<ArrowRight size={16} aria-hidden="true" />
		</a>
	</div>
{/if}

<style>
	.profile {
		display: flex;
		flex-direction: column;
		gap: var(--space-4);
		max-width: var(--max-width-text);
	}

	.details {
		display: grid;
		grid-template-columns: 140px 1fr;
		gap: var(--space-3) var(--space-4);
	}

	dt {
		font-family: var(--font-mono);
		font-size: 0.72rem;
		font-weight: 600;
		letter-spacing: 0.06em;
		text-transform: uppercase;
		color: var(--color-text-faint);
		align-self: center;
	}

	dd {
		color: var(--color-text);
		font-size: 0.9rem;
	}

	.next-card {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: var(--space-4);
		padding: var(--space-5) var(--space-6);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-lg);
		background: var(--color-surface);
		color: var(--color-text-muted);
		transition:
			border-color var(--transition-fast),
			color var(--transition-fast);
	}

	.next-card:hover {
		border-color: var(--color-accent);
		color: var(--color-text);
	}

	.next-label {
		display: block;
		font-family: var(--font-serif);
		font-size: 1.05rem;
		color: var(--color-text);
	}

	.next-sub {
		display: block;
		font-size: 0.82rem;
		color: var(--color-text-muted);
		margin-top: 0.15rem;
	}
</style>
