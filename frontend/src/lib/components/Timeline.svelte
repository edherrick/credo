<script lang="ts">
	// destructure all props at once, including callback
	const {
		values,
		selectedIndex,
		onChange
	}: {
		values: { date: string; value: number }[];
		selectedIndex: number;
		onChange?: (index: number) => void;
	} = $props();

	function handleInput(e: Event) {
		const target = e.target as HTMLInputElement;
		// call the parent callback if it exists
		if (onChange) {
			onChange(target.valueAsNumber);
		}
	}

	function formatDate(d: string) {
		return new Date(d + 'T00:00:00').toLocaleDateString('en-US', {
			year: 'numeric',
			month: 'short'
		});
	}
</script>

% TODO: This needs love but its a start for showing how a timeline component could work. It also
needs to be styled better and be more responsive.
<div class="timeline">
	<input
		type="range"
		min="0"
		max={values.length - 1}
		step="1"
		value={selectedIndex}
		oninput={handleInput}
	/>
	<div class="timeline-label">
		{values[selectedIndex] ? formatDate(values[selectedIndex].date) : ''}
	</div>
</div>

<style>
	.timeline {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 0.5rem;
	}
	input[type='range'] {
		width: 300px;
		height: 6px;
		border-radius: 3px;
		background: #e2e8f0;
		outline: none;
	}
	input[type='range']::-webkit-slider-thumb {
		width: 16px;
		height: 16px;
		border-radius: 50%;
		background: #1a2332;
		cursor: pointer;
	}
	.timeline-label {
		font-size: 0.75rem;
		color: #94a3b8;
	}
</style>
