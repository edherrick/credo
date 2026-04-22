<script lang="ts">
	let { data } = $props();
	const credo = $derived(data.credo);
</script>

<svelte:head>
	<title>{credo.title} · Timeline · Credo</title>
</svelte:head>

<section class="placeholder">
	<div class="placeholder-inner">
		<span class="placeholder-icon">◎</span>
		<h2 class="placeholder-title">Timeline</h2>
		<p class="placeholder-desc">
			A chronological view of policy events and entity actions across this credo's agendas.<br />
			Coming in Phase 2.
		</p>
	</div>
</section>

<style>
	.placeholder {
		padding: var(--space-16) var(--space-6);
		display: flex;
		justify-content: center;
	}

	.placeholder-inner {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: var(--space-4);
		max-width: 420px;
		text-align: center;
	}

	.placeholder-icon {
		font-size: 2rem;
		color: var(--color-accent);
		opacity: 0.4;
	}

	.placeholder-title {
		font-family: var(--font-serif);
		font-size: 1.6rem;
		font-weight: 400;
		color: var(--color-text);
	}

	.placeholder-desc {
		font-size: 0.9rem;
		color: var(--color-text-muted);
		line-height: 1.7;
	}
</style>
