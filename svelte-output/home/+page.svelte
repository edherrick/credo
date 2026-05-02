<script lang="ts">
	import { resolve } from '$app/paths';
	import { ArrowRight } from 'lucide-svelte';

	const steps = [
		{
			n: '01',
			title: 'Identify a problem',
			body: 'Track a metric — median home price, vacancy rate, new permits — across your community over time.'
		},
		{
			n: '02',
			title: 'Develop your credo',
			body: 'Write your founding beliefs and policy positions. Fork an existing credo or start from scratch.'
		},
		{
			n: '03',
			title: 'Build agendas',
			body: 'Concrete proposals with measurable targets, supporting evidence, and constituent backing.'
		},
		{
			n: '04',
			title: 'Measure outcomes',
			body: 'Track whether the metric moves after policy is enacted. The record is permanent and public.'
		}
	];

	const exampleBeliefs = [
		'Housing is a human right — adequate shelter is a prerequisite for civic participation.',
		'Market-rate development alone cannot solve affordability without supply reform.',
		'Data about housing markets should be public, current, and free.'
	];

	const exampleAgendas = [
		{ dir: 'lower', label: '↓ Lower', color: '#fbbf24', bg: 'rgba(245,158,11,0.12)', title: 'Reduce median rent to $1,400/mo by 2028' },
		{ dir: 'raise', label: '↑ Raise', color: '#22c55e', bg: 'rgba(34,197,94,0.1)', title: 'Double annual permit approvals to 14,000 by 2026' }
	];

	const exampleMetrics = ['Median Rent ($/mo)', 'Vacancy Rate (%)', 'Building Permits', 'Rent-Burden Ratio'];
</script>

<svelte:head>
	<title>Credo — Community-verified policy</title>
</svelte:head>

<!-- Hero -->
<section class="hero">
	<div class="hero-inner">
		<div class="hero-eyebrow">Open Civic Infrastructure</div>
		<h1 class="hero-title">Policy belongs<br />to the public.</h1>
		<p class="hero-sub">
			Credo is the open-source alternative to corporate-funded think tanks — transparent,
			metrics-anchored, community-verified policy built by the people it affects.
		</p>
		<div class="hero-actions">
			<a href={resolve('/explore')} class="cta-primary">
				Explore credos <ArrowRight size={16} aria-hidden="true" />
			</a>
			<a href={resolve('/register')} class="cta-ghost">Create an account</a>
		</div>
	</div>
	<div class="hero-rule"></div>
</section>

<!-- How it works -->
<section class="section">
	<div class="section-inner">
		<h2 class="section-title">How it works</h2>
		<p class="section-sub">From problem to policy in four steps</p>
		<div class="steps">
			{#each steps as step}
				<div class="step">
					<span class="step-number">{step.n}</span>
					<div class="step-content">
						<h3 class="step-title">{step.title}</h3>
						<p class="step-body">{step.body}</p>
					</div>
				</div>
			{/each}
		</div>
	</div>
</section>

<!-- Live example credo -->
<section class="section section-alt">
	<div class="section-inner">
		<div class="example-header">
			<div>
				<div class="example-eyebrow">Example credo</div>
				<h2 class="section-title">Chicago Metro Housing Affordability</h2>
				<p class="example-meta">
					by <a href={resolve('/credo/ed')} class="example-author">@ed</a>
					· 3 agendas · 4 metrics · 12 entities
				</p>
			</div>
			<a href={resolve('/credo/ed')} class="btn-outline">
				View full credo <ArrowRight size={14} aria-hidden="true" />
			</a>
		</div>

		<div class="example-grid">
			<!-- Founding beliefs -->
			<div class="example-col">
				<h3 class="col-label">Founding Beliefs</h3>
				{#each exampleBeliefs as belief, i}
					<div class="belief-row" class:border-b={i < exampleBeliefs.length - 1}>
						<span class="belief-num">{String(i + 1).padStart(2, '0')}</span>
						<p class="belief-text">{belief}</p>
					</div>
				{/each}
			</div>

			<!-- Agendas + metrics -->
			<div class="example-col">
				<h3 class="col-label">Active Agendas</h3>
				{#each exampleAgendas as agenda}
					<div class="agenda-row" style="--agenda-bg:{agenda.bg};--agenda-color:{agenda.color};">
						<span class="agenda-dir">{agenda.label}</span>
						<p class="agenda-title">{agenda.title}</p>
					</div>
				{/each}

				<h3 class="col-label" style="margin-top: 1.5rem;">Tracked Metrics</h3>
				<div class="metrics-chips">
					{#each exampleMetrics as m}
						<span class="metric-chip">{m}</span>
					{/each}
				</div>
			</div>
		</div>
	</div>
</section>

<!-- CTA strip -->
<section class="cta-strip">
	<div class="cta-strip-inner">
		<div>
			<h2 class="cta-strip-title">Ready to write your credo?</h2>
			<p class="cta-strip-sub">
				Join the community building transparent, evidence-backed policy. Free forever.
			</p>
		</div>
		<div class="cta-strip-actions">
			<a href={resolve('/register')} class="cta-primary">
				Create an account
			</a>
			<a href={resolve('/explore')} class="cta-outline-light">
				Explore credos <ArrowRight size={14} aria-hidden="true" />
			</a>
		</div>
	</div>
</section>

<style>
	/* ── Hero ───────────────────────────────────────────── */
	.hero {
		background: var(--color-navy);
		color: white;
		padding: var(--space-20) var(--space-6) var(--space-16);
		position: relative;
		overflow: hidden;
	}

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

	.hero::after {
		content: '';
		position: absolute;
		bottom: -60px;
		left: -40px;
		width: 380px;
		height: 380px;
		background: radial-gradient(circle, rgba(240, 59, 32, 0.09) 0%, transparent 70%);
		pointer-events: none;
	}

	.hero-inner {
		position: relative;
		z-index: 1;
		max-width: 700px;
		margin: 0 auto;
	}

	.hero-eyebrow {
		font-size: 0.6875rem;
		font-weight: 700;
		letter-spacing: 0.16em;
		text-transform: uppercase;
		color: var(--color-accent);
		margin-bottom: var(--space-6);
	}

	.hero-title {
		font-family: var(--font-serif);
		font-size: clamp(2.5rem, 6vw, 4rem);
		font-weight: 400;
		line-height: 1.08;
		color: white;
		letter-spacing: -0.015em;
		margin-bottom: var(--space-6);
	}

	.hero-sub {
		font-size: 1rem;
		color: rgba(255, 255, 255, 0.6);
		max-width: 540px;
		line-height: 1.8;
		margin-bottom: var(--space-12);
	}

	.hero-actions {
		display: flex;
		align-items: center;
		gap: var(--space-5);
		flex-wrap: wrap;
	}

	.cta-primary {
		display: inline-flex;
		align-items: center;
		gap: var(--space-2);
		background: var(--color-accent);
		color: white;
		font-weight: 600;
		font-size: 0.875rem;
		padding: 0.75rem var(--space-6);
		border-radius: var(--radius-md);
		transition: background var(--transition-fast), transform var(--transition-fast);
	}

	.cta-primary:hover {
		background: var(--color-accent-dark);
		transform: translateY(-1px);
	}

	.cta-ghost {
		color: rgba(255, 255, 255, 0.6);
		font-size: 0.875rem;
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
			var(--choropleth-2) 45%,
			transparent 100%
		);
	}

	/* ── Sections ─────────────────────────────────────── */
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

	.section-title {
		font-family: var(--font-serif);
		font-size: 1.75rem;
		font-weight: 400;
		color: var(--color-text);
		margin-bottom: 0.35rem;
	}

	.section-sub {
		font-size: 0.875rem;
		color: var(--color-text-muted);
		margin-bottom: var(--space-10);
	}

	/* ── How it works ─────────────────────────────────── */
	.steps {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
		gap: var(--space-10);
	}

	.step {
		display: flex;
		gap: var(--space-4);
	}

	.step-number {
		font-family: var(--font-serif);
		font-size: 1.75rem;
		font-weight: 400;
		color: var(--color-accent);
		opacity: 0.5;
		line-height: 1;
		flex-shrink: 0;
		width: 2.5rem;
		padding-top: 0.15rem;
	}

	.step-title {
		font-size: 0.9375rem;
		font-weight: 600;
		color: var(--color-text);
		margin-bottom: var(--space-2);
		line-height: 1.35;
	}

	.step-body {
		font-size: 0.875rem;
		color: var(--color-text-muted);
		line-height: 1.65;
	}

	/* ── Example credo ────────────────────────────────── */
	.example-header {
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
		gap: var(--space-6);
		margin-bottom: var(--space-10);
		flex-wrap: wrap;
	}

	.example-eyebrow {
		font-size: 0.6875rem;
		font-weight: 700;
		letter-spacing: 0.14em;
		text-transform: uppercase;
		color: var(--color-accent);
		margin-bottom: var(--space-3);
	}

	.example-meta {
		font-size: 0.8125rem;
		color: var(--color-text-muted);
		margin-top: var(--space-2);
	}

	.example-author {
		color: var(--color-accent);
	}

	.example-author:hover {
		text-decoration: underline;
	}

	.btn-outline {
		display: inline-flex;
		align-items: center;
		gap: var(--space-2);
		border: 1px solid var(--color-border);
		color: var(--color-text-muted);
		font-size: 0.8125rem;
		font-weight: 500;
		padding: 0.5625rem var(--space-5);
		border-radius: var(--radius-md);
		white-space: nowrap;
		flex-shrink: 0;
		transition: border-color var(--transition-fast), color var(--transition-fast);
	}

	.btn-outline:hover {
		border-color: var(--color-border-strong);
		color: var(--color-text);
	}

	.example-grid {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: var(--space-10);
	}

	@media (max-width: 700px) {
		.example-grid { grid-template-columns: 1fr; }
	}

	.col-label {
		font-size: 0.6875rem;
		font-weight: 700;
		letter-spacing: 0.1em;
		text-transform: uppercase;
		color: var(--color-text-faint);
		margin-bottom: var(--space-5);
	}

	.belief-row {
		display: flex;
		gap: var(--space-4);
		padding-bottom: var(--space-5);
		margin-bottom: var(--space-5);
	}

	.belief-row.border-b {
		border-bottom: 1px solid var(--color-border);
	}

	.belief-num {
		font-family: var(--font-mono);
		font-size: 0.8125rem;
		font-weight: 700;
		color: var(--color-accent);
		opacity: 0.6;
		flex-shrink: 0;
		padding-top: 0.1rem;
	}

	.belief-text {
		font-size: 0.8125rem;
		color: var(--color-text);
		line-height: 1.65;
	}

	.agenda-row {
		background: var(--color-bg);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-md);
		padding: 0.75rem var(--space-4);
		margin-bottom: var(--space-3);
		display: flex;
		gap: var(--space-3);
		align-items: center;
	}

	.agenda-dir {
		background: var(--agenda-bg);
		color: var(--agenda-color);
		font-size: 0.625rem;
		font-weight: 700;
		padding: 0.15rem 0.5rem;
		border-radius: var(--radius-sm);
		flex-shrink: 0;
	}

	.agenda-title {
		font-size: 0.8125rem;
		color: var(--color-text);
		line-height: 1.4;
	}

	.metrics-chips {
		display: flex;
		flex-wrap: wrap;
		gap: var(--space-2);
	}

	.metric-chip {
		font-size: 0.75rem;
		padding: 0.3125rem 0.75rem;
		border-radius: var(--radius-md);
		background: var(--color-bg);
		border: 1px solid var(--color-border);
		color: var(--color-text);
	}

	/* ── CTA strip ────────────────────────────────────── */
	.cta-strip {
		background: var(--color-navy);
		padding: var(--space-16) var(--space-6);
	}

	.cta-strip-inner {
		max-width: var(--max-width);
		margin: 0 auto;
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: var(--space-8);
		flex-wrap: wrap;
	}

	.cta-strip-title {
		font-family: var(--font-serif);
		font-size: 1.625rem;
		font-weight: 400;
		color: white;
		margin-bottom: var(--space-2);
	}

	.cta-strip-sub {
		font-size: 0.875rem;
		color: rgba(255, 255, 255, 0.55);
		max-width: 420px;
		line-height: 1.65;
	}

	.cta-strip-actions {
		display: flex;
		gap: var(--space-4);
		align-items: center;
		flex-shrink: 0;
		flex-wrap: wrap;
	}

	.cta-outline-light {
		display: inline-flex;
		align-items: center;
		gap: var(--space-2);
		border: 1px solid rgba(255, 255, 255, 0.15);
		color: rgba(255, 255, 255, 0.6);
		font-size: 0.875rem;
		font-weight: 500;
		padding: 0.75rem var(--space-5);
		border-radius: var(--radius-md);
		transition: border-color var(--transition-fast), color var(--transition-fast);
	}

	.cta-outline-light:hover {
		border-color: rgba(255, 255, 255, 0.3);
		color: white;
	}
</style>
