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

	const tenets = [
		'Policy should be grounded in measurable outcomes, not institutional funding.',
		'Every community deserves the same quality of evidence that corporate-funded think tanks access.',
		'Accountability requires memory — who said what, who acted, what changed.',
		'Transparency of reasoning matters as much as transparency of data.'
	];
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
			<a href={resolve('/credo/example')} class="cta-primary">
				See an example credo
				<ArrowRight size={16} aria-hidden="true" />
			</a>
			<a href={resolve('/register')} class="cta-ghost">Create an account</a>
		</div>
	</div>
	<div class="hero-rule"></div>
</section>

<!-- How it works -->
<section class="section">
	<div class="section-inner">
		<div class="section-header">
			<h2 class="section-title">How it works</h2>
			<p class="section-sub">From problem to policy in four steps</p>
		</div>
		<div class="steps">
			{#each steps as step}
				<div class="step">
					<div class="step-number">{step.n}</div>
					<div class="step-content">
						<h3 class="step-title">{step.title}</h3>
						<p class="step-body">{step.body}</p>
					</div>
				</div>
			{/each}
		</div>
	</div>
</section>

<!-- Beliefs -->
<section class="section section-alt">
	<div class="section-inner">
		<div class="section-header">
			<h2 class="section-title">What we believe</h2>
			<p class="section-sub">The principles behind the platform</p>
		</div>
		<div class="tenets">
			{#each tenets as tenet}
				<div class="tenet">
					<span class="tenet-mark" aria-hidden="true">&ldquo;</span>
					<p class="tenet-text">{tenet}</p>
				</div>
			{/each}
		</div>
	</div>
</section>

<!-- CTA strip -->
<section class="cta-strip">
	<div class="cta-strip-inner">
		<div>
			<h2 class="cta-strip-title">See it in action</h2>
			<p class="cta-strip-sub">
				Explore a live credo tracking housing affordability across the Chicago metro.
			</p>
		</div>
		<a href={resolve('/credo/example')} class="cta-strip-btn">
			View example credo
			<ArrowRight size={15} aria-hidden="true" />
		</a>
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
		color: var(--text-on-navy);
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
		color: var(--text-on-navy);
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
		margin-bottom: var(--space-10);
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

	/* ── How it works ────────────────────────────────────── */
	.steps {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
		gap: var(--space-8);
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
		opacity: 0.6;
		line-height: 1;
		flex-shrink: 0;
		width: 2.5rem;
	}

	.step-title {
		font-size: 0.95rem;
		font-weight: 600;
		color: var(--color-text);
		margin-bottom: var(--space-2);
	}

	.step-body {
		font-size: 0.875rem;
		color: var(--color-text-muted);
		line-height: 1.6;
	}

	/* ── Beliefs ─────────────────────────────────────────── */
	.tenets {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
		gap: var(--space-4);
	}

	.tenet {
		background: var(--color-bg);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-lg);
		padding: var(--space-6);
		display: flex;
		gap: var(--space-3);
	}

	.tenet-mark {
		font-family: var(--font-serif);
		font-size: 2rem;
		line-height: 1;
		color: var(--color-accent);
		opacity: 0.4;
		flex-shrink: 0;
	}

	.tenet-text {
		font-size: 0.925rem;
		color: var(--color-text);
		line-height: 1.65;
	}

	/* ── CTA strip ───────────────────────────────────────── */
	.cta-strip {
		background: var(--color-navy);
		padding: var(--space-12) var(--space-6);
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
		font-size: 1.4rem;
		font-weight: 400;
		color: white;
		margin-bottom: var(--space-2);
	}

	.cta-strip-sub {
		font-size: 0.9rem;
		color: var(--text-on-navy);
		max-width: 420px;
	}

	.cta-strip-btn {
		display: inline-flex;
		align-items: center;
		gap: var(--space-2);
		background: var(--color-accent);
		color: white;
		font-weight: 500;
		font-size: 0.9rem;
		padding: 0.7rem var(--space-6);
		border-radius: var(--radius-md);
		white-space: nowrap;
		flex-shrink: 0;
		transition:
			background var(--transition-fast),
			transform var(--transition-fast);
	}

	.cta-strip-btn:hover {
		background: var(--color-accent-dark);
		transform: translateY(-1px);
	}

	.cta-strip-btn :global(svg) {
		transition: transform var(--transition-fast);
	}

	.cta-strip-btn:hover :global(svg) {
		transform: translateX(3px);
	}
</style>
