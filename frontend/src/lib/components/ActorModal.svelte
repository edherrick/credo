<script lang="ts">
	import { X } from 'lucide-svelte';
	import type { Entity } from '$lib/types';

	let { entity, onclose }: { entity: Entity | null; onclose: () => void } = $props();

	let dialog = $state<HTMLDialogElement | null>(null);

	$effect(() => {
		if (!dialog) return;
		if (entity) {
			dialog.showModal();
		} else {
			dialog.close();
		}
	});

	function handleBackdrop(e: MouseEvent) {
		if (e.target === dialog) onclose();
	}

	function handleKeydown(e: KeyboardEvent) {
		if (e.key === 'Escape') onclose();
	}

	type ScoreTier = 'hero' | 'positive' | 'neutral' | 'negative' | 'villain';

	function scoreTier(score: number): ScoreTier {
		if (score >= 60) return 'hero';
		if (score >= 20) return 'positive';
		if (score >= -19) return 'neutral';
		if (score >= -59) return 'negative';
		return 'villain';
	}

	const tierLabel: Record<ScoreTier, string> = {
		hero: 'Hero',
		positive: 'Positive',
		neutral: 'Neutral',
		negative: 'Negative',
		villain: 'Villain'
	};

	function formatDate(d: string | null): string {
		if (!d) return '';
		return new Date(d).toLocaleDateString('en-US', {
			year: 'numeric',
			month: 'long',
			day: 'numeric'
		});
	}
</script>

<!-- svelte-ignore a11y_no_noninteractive_element_interactions -->
<dialog
	bind:this={dialog}
	class="actor-dialog"
	onclick={handleBackdrop}
	onkeydown={handleKeydown}
>
	{#if entity}
		{@const tier = scoreTier(entity.impact_score)}
		<div class="modal-inner">
			<div class="modal-header modal-header--{tier}">
				<div class="modal-header-meta">
					<span class="modal-type">{entity.type}</span>
					<span class="modal-score score--{tier}">
						<span class="score-dot" aria-hidden="true"></span>
						{tierLabel[tier]}
					</span>
				</div>
				<h2 class="modal-name">{entity.name}</h2>
				{#if entity.description}
					<p class="modal-desc">{entity.description}</p>
				{/if}
				<button class="close-btn" onclick={onclose} aria-label="Close">
					<X size={16} />
				</button>
			</div>

			{#if entity.events.length > 0}
				<div class="modal-body">
					<h3 class="events-heading">Documented events</h3>
					<ol class="event-timeline">
						{#each entity.events as ev (ev.id)}
							<li class="timeline-item">
								<div class="timeline-marker" aria-hidden="true"></div>
								<div class="timeline-content">
									<div class="timeline-meta">
										{#if ev.event_date}
											<span class="timeline-date">{formatDate(ev.event_date)}</span>
										{/if}
										{#if ev.event_impact_score !== null}
											<span
												class="timeline-score"
												class:positive={ev.event_impact_score > 0}
												class:negative={ev.event_impact_score < 0}
											>
												{ev.event_impact_score > 0 ? '+' : ''}{ev.event_impact_score}
											</span>
										{/if}
										{#if ev.metric_id}
											<span class="timeline-metric">{ev.metric_id.replace(/_/g, ' ')}</span>
										{/if}
									</div>
									<p class="timeline-title">{ev.title}</p>
									{#if ev.description}
										<p class="timeline-desc">{ev.description}</p>
									{/if}
									{#if ev.source_url}
										<a
											class="timeline-source"
											href={ev.source_url}
											target="_blank"
											rel="noopener noreferrer"
										>Source ↗</a>
									{/if}
								</div>
							</li>
						{/each}
					</ol>
				</div>
			{:else}
				<div class="modal-body modal-empty">
					<p>No documented events yet.</p>
				</div>
			{/if}
		</div>
	{/if}
</dialog>

<style>
	.actor-dialog {
		border: none;
		border-radius: var(--radius-xl, 12px);
		padding: 0;
		max-width: min(640px, 95vw);
		width: 100%;
		max-height: 85vh;
		overflow: hidden;
		display: flex;
		flex-direction: column;
		box-shadow: 0 24px 64px rgba(0, 0, 0, 0.35);
		/* Center within the viewport */
		position: fixed;
		top: 50%;
		left: 50%;
		translate: -50% -50%;
		margin: 0;
		background: var(--color-bg);
	}

	.actor-dialog::backdrop {
		background: rgba(0, 0, 0, 0.55);
		backdrop-filter: blur(2px);
	}

	.modal-inner {
		display: flex;
		flex-direction: column;
		overflow: hidden;
		max-height: 85vh;
	}

	/* ── Header ──────────────────────────────────────────── */
	.modal-header {
		position: relative;
		padding: 2rem 2rem 1.5rem;
		border-bottom: 1px solid var(--color-border);
		border-left: 4px solid transparent;
		flex-shrink: 0;
	}

	.modal-header--hero    { border-left-color: #22c55e; }
	.modal-header--positive { border-left-color: #14b8a6; }
	.modal-header--neutral  { border-left-color: var(--color-border); }
	.modal-header--negative { border-left-color: #f97316; }
	.modal-header--villain  { border-left-color: var(--color-accent); }

	.modal-header-meta {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		margin-bottom: 0.75rem;
	}

	.modal-type {
		font-size: 0.7rem;
		font-weight: 600;
		letter-spacing: 0.1em;
		text-transform: uppercase;
		color: var(--color-text-faint);
	}

	.modal-score {
		display: flex;
		align-items: center;
		gap: 0.35rem;
		font-size: 0.72rem;
		font-weight: 600;
		letter-spacing: 0.06em;
		text-transform: uppercase;
	}

	.score-dot {
		width: 7px;
		height: 7px;
		border-radius: 50%;
		flex-shrink: 0;
	}

	.score--hero     { color: #22c55e; }
	.score--hero .score-dot { background: #22c55e; }
	.score--positive { color: #14b8a6; }
	.score--positive .score-dot { background: #14b8a6; }
	.score--neutral  { color: var(--color-text-muted); }
	.score--neutral .score-dot { background: var(--color-text-muted); }
	.score--negative { color: #f97316; }
	.score--negative .score-dot { background: #f97316; }
	.score--villain  { color: var(--color-accent); }
	.score--villain .score-dot { background: var(--color-accent); }

	.modal-name {
		font-family: var(--font-serif);
		font-size: 1.5rem;
		font-weight: 400;
		color: var(--color-text);
		line-height: 1.25;
		margin-bottom: 0.6rem;
		padding-right: 2.5rem; /* space for close btn */
	}

	.modal-desc {
		font-size: 0.9rem;
		color: var(--color-text-muted);
		line-height: 1.65;
	}

	.close-btn {
		position: absolute;
		top: 1.25rem;
		right: 1.25rem;
		display: flex;
		align-items: center;
		justify-content: center;
		width: 30px;
		height: 30px;
		border-radius: var(--radius-md);
		border: 1px solid var(--color-border);
		background: var(--color-bg);
		color: var(--color-text-muted);
		cursor: pointer;
		transition:
			color var(--transition-fast),
			border-color var(--transition-fast);
	}

	.close-btn:hover {
		color: var(--color-text);
		border-color: var(--color-text-muted);
	}

	/* ── Body / timeline ─────────────────────────────────── */
	.modal-body {
		overflow-y: auto;
		padding: 1.5rem 2rem 2rem;
		flex: 1;
	}

	.modal-empty {
		color: var(--color-text-muted);
		font-size: 0.9rem;
	}

	.events-heading {
		font-size: 0.7rem;
		font-weight: 700;
		letter-spacing: 0.12em;
		text-transform: uppercase;
		color: var(--color-text-faint);
		margin-bottom: 1.25rem;
	}

	.event-timeline {
		list-style: none;
		display: flex;
		flex-direction: column;
		gap: 0;
		position: relative;
	}

	.event-timeline::before {
		content: '';
		position: absolute;
		left: 6px;
		top: 8px;
		bottom: 8px;
		width: 1px;
		background: var(--color-border);
	}

	.timeline-item {
		display: flex;
		gap: 1rem;
		padding-bottom: 1.5rem;
	}

	.timeline-item:last-child {
		padding-bottom: 0;
	}

	.timeline-marker {
		width: 13px;
		height: 13px;
		border-radius: 50%;
		border: 2px solid var(--color-accent);
		background: var(--color-bg);
		flex-shrink: 0;
		margin-top: 0.2rem;
		position: relative;
		z-index: 1;
	}

	.timeline-content {
		display: flex;
		flex-direction: column;
		gap: 0.3rem;
	}

	.timeline-meta {
		display: flex;
		align-items: center;
		gap: 0.6rem;
		flex-wrap: wrap;
	}

	.timeline-date {
		font-size: 0.75rem;
		color: var(--color-text-faint);
		font-family: var(--font-mono);
	}

	.timeline-score {
		font-size: 0.72rem;
		font-weight: 700;
		font-family: var(--font-mono);
	}

	.timeline-score.positive { color: #22c55e; }
	.timeline-score.negative { color: var(--color-accent); }

	.timeline-metric {
		font-size: 0.68rem;
		padding: 0.1rem 0.4rem;
		border-radius: var(--radius-sm);
		background: var(--color-border);
		color: var(--color-text-muted);
		text-transform: capitalize;
	}

	.timeline-title {
		font-size: 0.9rem;
		font-weight: 600;
		color: var(--color-text);
		line-height: 1.4;
	}

	.timeline-desc {
		font-size: 0.83rem;
		color: var(--color-text-muted);
		line-height: 1.6;
	}

	.timeline-source {
		font-size: 0.72rem;
		color: var(--color-text-faint);
		text-decoration: none;
		font-family: var(--font-mono);
	}

	.timeline-source:hover {
		color: var(--color-text-muted);
		text-decoration: underline;
	}
</style>
