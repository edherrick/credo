<script lang="ts">
	import { resolve } from '$app/paths';
	import { ScrollText, Layers, Compass, BarChart3, Users } from 'lucide-svelte';
	import { PageHeader } from '$lib/components/ui';

	let { data } = $props();
	const counts = $derived(data.counts);

	const sections = $derived([
		{
			key: 'beliefs',
			label: 'Beliefs',
			href: resolve('/beliefs'),
			icon: ScrollText,
			count: counts.beliefs,
			desc: 'Founding axioms credos adopt and interpret'
		},
		{
			key: 'issues',
			label: 'Issues',
			href: resolve('/issues'),
			icon: Layers,
			count: counts.issues,
			desc: 'Abstract policy areas an agenda instantiates'
		},
		{
			key: 'axes',
			label: 'Axes',
			href: resolve('/axes'),
			icon: Compass,
			count: counts.axes,
			desc: 'Scoring dimensions credos weight and align against'
		},
		{
			key: 'metrics',
			label: 'Metrics',
			href: resolve('/metrics'),
			icon: BarChart3,
			count: counts.metrics,
			desc: 'Measurable indicators, mapped over time'
		},
		{
			key: 'entities',
			label: 'Entities',
			href: resolve('/entities'),
			icon: Users,
			count: counts.entities,
			desc: 'Politicians, organizations and corporations tracked'
		}
	]);
</script>

<svelte:head><title>Library · Credo</title></svelte:head>

<PageHeader
	eyebrow="The Commons"
	title="Library"
	sub="The shared building blocks every credo assembles from"
/>

<section class="hub">
	<div class="hub-inner">
		<div class="hub-grid">
			{#each sections as s (s.key)}
				{@const Icon = s.icon}
				<!-- eslint-disable-next-line svelte/no-navigation-without-resolve -- s.href is already resolve()'d in the sections array -->
				<a href={s.href} class="hub-card">
					<div class="hub-card-top">
						<span class="hub-icon"><Icon size={18} aria-hidden="true" /></span>
						<span class="hub-count">{s.count}</span>
					</div>
					<h2 class="hub-label">{s.label}</h2>
					<p class="hub-desc">{s.desc}</p>
				</a>
			{/each}
		</div>
	</div>
</section>

<style>
	.hub {
		padding: var(--space-10) var(--space-6);
	}

	.hub-inner {
		max-width: var(--max-width);
		margin: 0 auto;
	}

	.hub-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
		gap: var(--space-4);
	}

	.hub-card {
		display: flex;
		flex-direction: column;
		gap: var(--space-2);
		padding: var(--space-6);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-lg);
		background: var(--color-surface);
		color: inherit;
		transition:
			border-color var(--transition-base),
			box-shadow var(--transition-base),
			transform var(--transition-base);
	}

	.hub-card:hover {
		border-color: var(--color-accent);
		box-shadow: var(--shadow-accent);
		transform: translateY(-2px);
	}

	.hub-card-top {
		display: flex;
		align-items: center;
		justify-content: space-between;
	}

	.hub-icon {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		width: 34px;
		height: 34px;
		border-radius: var(--radius-md);
		background: var(--color-bg);
		color: var(--color-accent);
	}

	.hub-count {
		font-family: var(--font-mono);
		font-size: 1.25rem;
		font-weight: 600;
		color: var(--color-text);
	}

	.hub-label {
		font-family: var(--font-serif);
		font-size: 1.2rem;
		font-weight: 400;
		color: var(--color-text);
	}

	.hub-desc {
		font-size: 0.83rem;
		color: var(--color-text-muted);
		line-height: 1.55;
	}
</style>
