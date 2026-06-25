<script lang="ts">
	import type { Snippet } from 'svelte';

	// neutral = mono category label; the score tones map to the accountability scale.
	type Tone = 'neutral' | 'accent' | 'hero' | 'positive' | 'neutral-score' | 'negative' | 'villain';

	interface Props {
		tone?: Tone;
		/** show a leading status dot (for score tones) */
		dot?: boolean;
		children: Snippet;
	}

	let { tone = 'neutral', dot = false, children }: Props = $props();
</script>

<span
	class="badge"
	class:accent={tone === 'accent'}
	class:hero={tone === 'hero'}
	class:positive={tone === 'positive'}
	class:neutral-score={tone === 'neutral-score'}
	class:negative={tone === 'negative'}
	class:villain={tone === 'villain'}
>
	{#if dot}<span class="dot" aria-hidden="true"></span>{/if}
	{@render children()}
</span>

<style>
	/* Mono small-caps — the cartographic / ledger label voice */
	.badge {
		display: inline-flex;
		align-items: center;
		gap: 0.35rem;
		font-family: var(--font-mono);
		font-size: 0.68rem;
		font-weight: 600;
		letter-spacing: 0.06em;
		text-transform: uppercase;
		color: var(--color-text-muted);
		padding: 0.15rem 0.5rem;
		border-radius: var(--radius-sm);
		border: 1px solid var(--color-border);
		white-space: nowrap;
	}

	.dot {
		width: 6px;
		height: 6px;
		border-radius: var(--radius-full);
		background: currentColor;
		flex-shrink: 0;
	}

	.accent {
		color: var(--color-accent);
		border-color: var(--color-border-strong);
	}
	.hero {
		color: var(--score-hero);
	}
	.positive {
		color: var(--score-positive);
	}
	.neutral-score {
		color: var(--score-neutral);
	}
	.negative {
		color: var(--score-negative);
	}
	.villain {
		color: var(--score-villain);
	}
</style>
