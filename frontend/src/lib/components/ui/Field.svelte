<script lang="ts">
	interface Props {
		label: string;
		value: string;
		type?: string;
		placeholder?: string;
		hint?: string;
		error?: string;
		required?: boolean;
		disabled?: boolean;
		multiline?: boolean;
		rows?: number;
	}

	let {
		label,
		value = $bindable(''),
		type = 'text',
		placeholder,
		hint,
		error,
		required = false,
		disabled = false,
		multiline = false,
		rows = 4
	}: Props = $props();
</script>

<label class="field">
	<span class="label">
		{label}{#if !required}<span class="optional"> (optional)</span>{/if}
	</span>

	{#if multiline}
		<textarea bind:value {placeholder} {rows} {disabled}></textarea>
	{:else}
		<input {type} bind:value {placeholder} {required} {disabled} />
	{/if}

	{#if error}
		<span class="error">{error}</span>
	{:else if hint}
		<span class="hint">{hint}</span>
	{/if}
</label>

<style>
	.field {
		display: flex;
		flex-direction: column;
		gap: var(--space-2);
	}

	.label {
		font-size: 0.85rem;
		font-weight: 510;
		color: var(--color-text);
	}

	.optional {
		font-weight: 400;
		color: var(--color-text-faint);
	}

	input,
	textarea {
		width: 100%;
		padding: 0.6rem 0.75rem;
		font: inherit;
		font-size: 0.9rem;
		color: var(--color-text);
		background: var(--color-bg);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-md);
		transition:
			border-color var(--transition-fast),
			box-shadow var(--transition-fast);
	}

	textarea {
		resize: vertical;
	}

	input:focus,
	textarea:focus {
		outline: none;
		border-color: var(--color-accent);
		box-shadow: var(--shadow-accent);
	}

	input:disabled,
	textarea:disabled {
		color: var(--color-text-faint);
		background: var(--color-surface);
		cursor: not-allowed;
	}

	.hint {
		font-size: 0.78rem;
		color: var(--color-text-muted);
	}

	.error {
		font-size: 0.78rem;
		color: var(--color-accent);
	}
</style>
