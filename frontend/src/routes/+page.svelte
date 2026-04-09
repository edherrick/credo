<script lang="ts">
	import { onMount } from 'svelte';
	import { getGeographies, getMetrics, getAgendas } from '$lib/api';
	import type { Geography, Metric, Agenda } from '$lib/types';
	import { resolve } from '$app/paths';
	import { ArrowRight, TrendingUp, TrendingDown } from 'lucide-svelte';

	let geographies = $state<Geography[]>([]);
	let metrics = $state<Metric[]>([]);
	let agendas = $state<Agenda[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);

	onMount(async () => {
		try {
			[geographies, metrics, agendas] = await Promise.all([
				getGeographies(),
				getMetrics(),
				getAgendas()
			]);
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to load data';
		} finally {
			loading = false;
		}
	});

	function metricLabel(geo: Geography): string {
		// TODO: Why can this be empty all metrics should have a display name??
		return `${geo.name} · ${metrics[0]?.display_name ?? ''}`;
	}

	// directionLabel replaced by directionIcon — rendered in template

	function formatCurrency(val: number | null): string {
		if (val === null || val === undefined) return '—';
		return new Intl.NumberFormat('en-US', {
			style: 'currency',
			currency: 'USD',
			maximumFractionDigits: 0
		}).format(val);
	}
</script>

<svelte:head>
	<title>Credo — Community-verified policy</title>
</svelte:head>

<!-- Hero -->
<section class="hero">
	<div class="hero-inner">
		<div class="hero-eyebrow">Open civic infrastructure</div>
		<h1 class="hero-title">
			Community-verified policy,<br />backed by evidence.
		</h1>
		<p class="hero-sub">
			Credo connects measurable outcomes to community beliefs — and community beliefs to real
			legislation. Transparent, metrics-anchored, and open source.
		</p>
		<div class="hero-actions">
			<a href={resolve('/map?fips=17031&metric=median_home_price')} class="cta-primary">
				Explore the map
				<ArrowRight size={16} aria-hidden="true" />
			</a>
			<a href={resolve('/register')} class="cta-ghost">Create an account</a>
		</div>
	</div>
	<div class="hero-rule"></div>
</section>

{#if loading}
	<div class="loading-state">
		<div class="spinner"></div>
		<span>Loading data…</span>
	</div>
{:else if error}
	<div class="error-banner">{error}</div>
{:else}
	<!-- Geographies -->
	{#if geographies.length > 0}
		<section class="section">
			<div class="section-inner">
				<div class="section-header">
					<h2 class="section-title">Geographies</h2>
					<p class="section-sub">Active regions with housing price data</p>
				</div>
				<div class="card-grid">
					{#each geographies as geo (geo.id)}
						<a href={resolve(`/map?fips=${geo.id}&metric=median_home_price`)} class="geo-card">
							<div class="geo-card-top">
								<span class="geo-type">{geo.geo_type}</span>
								<span class="geo-fips">FIPS {geo.id}</span>
							</div>
							<h3 class="geo-name">{geo.name}</h3>
							<div class="geo-metric">{metricLabel(geo)}</div>
							<div class="geo-arrow">View map <ArrowRight size={13} aria-hidden="true" /></div>
						</a>
					{/each}
				</div>
			</div>
		</section>
	{/if}

	<!-- Agendas -->
	{#if agendas.length > 0}
		<section class="section section-alt">
			<div class="section-inner">
				<div class="section-header">
					<h2 class="section-title">Active Agendas</h2>
					<p class="section-sub">Community policy goals with measurable targets</p>
				</div>
				<div class="agenda-list">
					{#each agendas as agenda (agenda.id)}
						<div class="agenda-card">
							<div class="agenda-badge" class:lower={agenda.direction === 'lower'}>
								{#if agenda.direction === 'lower'}
									<TrendingDown size={12} aria-hidden="true" /> Lower
								{:else}
									<TrendingUp size={12} aria-hidden="true" /> Raise
								{/if}
							</div>
							<h3 class="agenda-title">{agenda.title}</h3>
							<div class="agenda-meta">
								{#if agenda.target_value}
									<span class="agenda-target">
										Target: <strong>{formatCurrency(agenda.target_value)}</strong>
									</span>
								{/if}
								{#if agenda.target_date}
									<span class="agenda-date">by {agenda.target_date}</span>
								{/if}
							</div>
						</div>
					{/each}
				</div>
			</div>
		</section>
	{/if}
{/if}

<style>
	/* ── Hero ───────────────────────────────────────────── */
	.hero {
		background: var(--color-navy);
		color: white;
		padding: var(--space-20) var(--space-6) var(--space-16);
		position: relative;
		overflow: hidden;
	}

	/* Subtle data-grid motif — evokes charts and civic infrastructure */
	.hero::before {
		content: '';
		position: absolute;
		inset: 0;
		background-image:
			linear-gradient(rgba(255, 255, 255, 0.028) 1px, transparent 1px),
			linear-gradient(90deg, rgba(255, 255, 255, 0.028) 1px, transparent 1px);
		background-size: 52px 52px;
		pointer-events: none;
	}

	/* Warm glow from accent at bottom-left — echoes the choropleth palette */
	.hero::after {
		content: '';
		position: absolute;
		bottom: -60px;
		left: -40px;
		width: 320px;
		height: 320px;
		background: radial-gradient(circle, rgba(240, 59, 32, 0.12) 0%, transparent 70%);
		pointer-events: none;
	}

	.hero-inner {
		position: relative;
		z-index: 1;
		max-width: var(--max-width-text);
		margin: 0 auto;
	}

	.hero-eyebrow {
		font-size: 0.75rem;
		font-weight: 600;
		letter-spacing: 0.12em;
		text-transform: uppercase;
		color: var(--color-accent);
		margin-bottom: var(--space-5);
	}

	.hero-title {
		font-family: var(--font-serif);
		font-size: clamp(2rem, 5vw, 3rem);
		font-weight: 400;
		line-height: 1.15;
		margin-bottom: var(--space-5);
		letter-spacing: -0.01em;
	}

	.hero-sub {
		font-size: 1.05rem;
		color: rgba(255, 255, 255, 0.65);
		max-width: 540px;
		line-height: 1.7;
		margin-bottom: var(--space-10);
	}

	.hero-actions {
		display: flex;
		align-items: center;
		gap: var(--space-4);
		flex-wrap: wrap;
	}

	.cta-primary {
		display: inline-flex;
		align-items: center;
		gap: var(--space-2);
		background: var(--color-accent);
		color: white;
		font-weight: 500;
		font-size: 0.9rem;
		padding: 0.65rem var(--space-5);
		border-radius: var(--radius-md);
		transition:
			background var(--transition-fast),
			transform var(--transition-fast);
	}

	.cta-primary:hover {
		background: var(--color-accent-dark);
		transform: translateY(-1px);
	}

	.cta-primary :global(svg) {
		transition: transform var(--transition-fast);
	}
	.cta-primary:hover :global(svg) {
		transform: translateX(3px);
	}

	.cta-ghost {
		color: rgba(255, 255, 255, 0.6);
		font-size: 0.9rem;
		font-weight: 500;
		transition: color var(--transition-fast);
	}
	.cta-ghost:hover {
		color: white;
	}

	.hero-rule {
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

	/* ── Loading / Error ─────────────────────────────────── */
	.loading-state {
		display: flex;
		align-items: center;
		justify-content: center;
		gap: var(--space-3);
		padding: var(--space-16);
		color: var(--color-text-muted);
		font-size: 0.9rem;
	}

	.spinner {
		width: 18px;
		height: 18px;
		border: 2px solid var(--color-border);
		border-top-color: var(--color-accent);
		border-radius: 50%;
		animation: spin 0.7s linear infinite;
	}

	@keyframes spin {
		to {
			transform: rotate(360deg);
		}
	}

	.error-banner {
		margin: var(--space-8) auto;
		max-width: 600px;
		padding: var(--space-4) var(--space-5);
		background: var(--color-error-bg);
		border: 1px solid var(--color-error-border);
		border-radius: var(--radius-lg);
		color: var(--color-error-text);
		font-size: 0.9rem;
	}

	/* ── Sections ────────────────────────────────────────── */
	.section {
		padding: var(--space-16) var(--space-6);
	}

	.section-alt {
		background: var(--color-surface);
		border-top: 1px solid var(--color-border);
		border-bottom: 1px solid var(--color-border);
	}

	.section-inner {
		max-width: var(--max-width);
		margin: 0 auto;
	}

	.section-header {
		margin-bottom: var(--space-8);
	}

	.section-title {
		font-family: var(--font-serif);
		font-size: 1.6rem;
		font-weight: 400;
		color: var(--color-text);
		margin-bottom: 0.35rem;
	}

	.section-sub {
		font-size: 0.9rem;
		color: var(--color-text-muted);
	}

	/* ── Geo cards ───────────────────────────────────────── */
	.card-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
		gap: var(--space-4);
	}

	.geo-card {
		display: flex;
		flex-direction: column;
		gap: var(--space-2);
		background: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-lg);
		padding: var(--space-5) var(--space-6);
		transition:
			border-color var(--transition-base),
			box-shadow var(--transition-base),
			transform var(--transition-base);
		cursor: pointer;
	}

	.geo-card:hover {
		border-color: var(--color-accent);
		box-shadow: var(--shadow-accent);
		transform: translateY(-2px);
	}

	.geo-card-top {
		display: flex;
		align-items: center;
		justify-content: space-between;
	}

	.geo-type {
		font-size: 0.7rem;
		font-weight: 600;
		letter-spacing: 0.1em;
		text-transform: uppercase;
		color: var(--color-text-faint);
	}

	.geo-fips {
		font-size: 0.7rem;
		font-family: var(--font-mono);
		color: var(--color-border-strong);
	}

	.geo-name {
		font-size: 1.05rem;
		font-weight: 600;
		color: var(--color-text);
		line-height: 1.3;
	}

	.geo-metric {
		font-size: 0.8rem;
		color: var(--color-text-muted);
	}

	.geo-arrow {
		margin-top: auto;
		padding-top: var(--space-3);
		font-size: 0.8rem;
		font-weight: 500;
		color: var(--color-accent);
		opacity: 0;
		display: flex;
		align-items: center;
		gap: 0.25rem;
		transition: opacity var(--transition-fast);
	}

	.geo-card:hover .geo-arrow {
		opacity: 1;
	}

	/* ── Agenda cards ────────────────────────────────────── */
	.agenda-list {
		display: flex;
		flex-direction: column;
		gap: var(--space-3);
	}

	.agenda-card {
		background: var(--color-bg);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-lg);
		padding: var(--space-5) var(--space-6);
		display: flex;
		flex-direction: column;
		gap: var(--space-2);
	}

	.agenda-badge {
		display: inline-flex;
		align-items: center;
		gap: 0.3rem;
		font-size: 0.7rem;
		font-weight: 600;
		letter-spacing: 0.08em;
		text-transform: uppercase;
		padding: 0.2rem 0.6rem;
		border-radius: var(--radius-sm);
		background: var(--color-border);
		color: var(--color-text-muted);
		width: fit-content;
	}

	.agenda-badge.lower {
		background: var(--color-warn-bg);
		color: var(--color-warn-text);
	}

	.agenda-title {
		font-size: 1rem;
		font-weight: 600;
		color: var(--color-text);
		line-height: 1.4;
	}

	.agenda-meta {
		display: flex;
		align-items: center;
		gap: var(--space-4);
		font-size: 0.85rem;
		color: var(--color-text-muted);
	}

	.agenda-target strong {
		color: var(--color-text);
	}
</style>
