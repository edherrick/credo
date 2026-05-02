<script lang="ts">
	import { register, login, getMe } from '$lib/api';
	import { auth } from '$lib/stores/auth';
	import { goto } from '$app/navigation';
	import { resolve } from '$app/paths';

	let email = $state('');
	let password = $state('');
	let username = $state('');
	let displayName = $state('');
	let error = $state<string | null>(null);
	let submitting = $state(false);

	async function handleSubmit(e: SubmitEvent) {
		e.preventDefault();
		error = null;
		submitting = true;
		try {
			await register(email, password, username);
			const token = await login(email, password);
			const user = await getMe(token.access_token);
			auth.login(token.access_token, user);
			goto(resolve('/me'));
		} catch (err) {
			error = err instanceof Error ? err.message : 'Registration failed';
		} finally {
			submitting = false;
		}
	}
</script>

<svelte:head>
	<title>Register · Credo</title>
</svelte:head>

<div class="register-page">
	<!-- Grid texture -->
	<div class="grid-texture" aria-hidden="true"></div>

	<div class="page-inner">
		<!-- Progress -->
		<div class="progress-bar">
			<div class="steps-indicator">
				{#each [1, 2, 3] as n}
					<div class="step-dot" class:active={n === 1} class:done={n < 1}>
						{n}
					</div>
					{#if n < 3}
						<div class="step-connector"></div>
					{/if}
				{/each}
			</div>
			<span class="step-label">Step 1 of 3</span>
		</div>

		<div class="step-labels">
			{#each ['Account', 'Your credo', 'Done'] as s, i}
				<span class:current={i === 0} class:future={i > 0}>{s}{i < 2 ? ' →' : ''} </span>
			{/each}
		</div>

		<h1 class="page-title">Create your account</h1>
		<p class="page-sub">Join the community building transparent, evidence-backed policy.</p>

		<form onsubmit={handleSubmit} class="form">
			<div class="field-row">
				<div class="field">
					<label for="username">Username</label>
					<input
						id="username"
						type="text"
						bind:value={username}
						placeholder="@yourname"
						required
					/>
					<span class="field-hint">Your public handle on Credo.</span>
				</div>
				<div class="field">
					<label for="display-name">Display name</label>
					<input
						id="display-name"
						type="text"
						bind:value={displayName}
						placeholder="Jane Doe"
					/>
				</div>
			</div>

			<div class="field">
				<label for="email">Email address</label>
				<input
					id="email"
					type="email"
					bind:value={email}
					placeholder="you@example.com"
					required
				/>
			</div>

			<div class="field">
				<label for="password">Password</label>
				<input
					id="password"
					type="password"
					bind:value={password}
					placeholder="At least 8 characters"
					required
					minlength={8}
				/>
			</div>

			{#if error}
				<p class="error">{error}</p>
			{/if}

			<div class="form-footer">
				<p class="login-link">
					Have an account? <a href={resolve('/login')}>Log in</a>
				</p>
				<button type="submit" class="btn-primary" disabled={submitting}>
					{submitting ? 'Creating account…' : 'Continue →'}
				</button>
			</div>
		</form>

		<!-- Trust note -->
		<div class="trust-note">
			<img src="/logo.svg" alt="" class="trust-logo" aria-hidden="true" />
			<p>
				<strong>Free forever.</strong> Open source, no advertising, no corporate sponsors.
				Your data is yours.
			</p>
		</div>
	</div>
</div>

<style>
	.register-page {
		min-height: calc(100vh - var(--nav-height));
		display: flex;
		align-items: center;
		justify-content: center;
		padding: var(--space-12) var(--space-6);
		position: relative;
	}

	.grid-texture {
		position: fixed;
		inset: 0;
		background-image:
			linear-gradient(rgba(255, 255, 255, 0.022) 1px, transparent 1px),
			linear-gradient(90deg, rgba(255, 255, 255, 0.022) 1px, transparent 1px);
		background-size: 52px 52px;
		pointer-events: none;
		z-index: 0;
	}

	.page-inner {
		position: relative;
		z-index: 1;
		width: 100%;
		max-width: 600px;
	}

	/* Progress */
	.progress-bar {
		display: flex;
		align-items: center;
		justify-content: space-between;
		margin-bottom: var(--space-3);
	}

	.steps-indicator {
		display: flex;
		align-items: center;
		gap: var(--space-2);
	}

	.step-dot {
		width: 28px;
		height: 28px;
		border-radius: 50%;
		background: var(--color-border);
		color: var(--color-text-faint);
		font-size: 0.75rem;
		font-weight: 600;
		display: flex;
		align-items: center;
		justify-content: center;
		transition: background var(--transition-fast), color var(--transition-fast);
	}

	.step-dot.active {
		background: var(--color-accent);
		color: white;
	}

	.step-dot.done {
		background: var(--color-accent);
		color: white;
	}

	.step-connector {
		width: 40px;
		height: 2px;
		background: var(--color-border);
		border-radius: 1px;
	}

	.step-label {
		font-size: 0.75rem;
		color: var(--color-text-faint);
	}

	.step-labels {
		display: flex;
		gap: var(--space-1);
		margin-bottom: var(--space-10);
		font-size: 0.6875rem;
	}

	.step-labels span {
		color: var(--color-text-faint);
	}

	.step-labels .current {
		color: var(--color-text);
		font-weight: 600;
	}

	.page-title {
		font-family: var(--font-serif);
		font-size: 2.125rem;
		font-weight: 400;
		color: var(--color-text);
		margin-bottom: var(--space-2);
		letter-spacing: -0.01em;
	}

	.page-sub {
		font-size: 0.875rem;
		color: var(--color-text-muted);
		line-height: 1.6;
		margin-bottom: var(--space-9);
	}

	.form {
		display: flex;
		flex-direction: column;
		gap: var(--space-5);
	}

	.field-row {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: var(--space-4);
	}

	.field {
		display: flex;
		flex-direction: column;
		gap: var(--space-2);
	}

	.field label {
		font-size: 0.8125rem;
		font-weight: 500;
		color: var(--color-text);
	}

	.field input {
		background: rgba(255, 255, 255, 0.04);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-md);
		padding: 0.625rem 0.875rem;
		font-size: 0.875rem;
		color: var(--color-text);
		font-family: inherit;
		outline: none;
		transition: border-color var(--transition-fast);
	}

	.field input::placeholder {
		color: var(--color-text-faint);
	}

	.field input:focus {
		border-color: var(--color-accent);
	}

	.field-hint {
		font-size: 0.6875rem;
		color: var(--color-text-muted);
		line-height: 1.5;
	}

	.error {
		font-size: 0.8125rem;
		color: var(--color-error-text);
		background: var(--color-error-bg);
		border: 1px solid var(--color-error-border);
		border-radius: var(--radius-md);
		padding: var(--space-3) var(--space-4);
	}

	.form-footer {
		display: flex;
		align-items: center;
		justify-content: space-between;
		margin-top: var(--space-2);
	}

	.login-link {
		font-size: 0.8125rem;
		color: var(--color-text-muted);
	}

	.login-link a {
		color: var(--color-accent);
		font-weight: 500;
	}

	.login-link a:hover {
		text-decoration: underline;
	}

	.btn-primary {
		background: var(--color-accent);
		color: white;
		border: none;
		border-radius: var(--radius-md);
		padding: 0.75rem var(--space-8);
		font-size: 0.875rem;
		font-weight: 600;
		font-family: inherit;
		cursor: pointer;
		transition: background var(--transition-fast), transform var(--transition-fast);
	}

	.btn-primary:hover:not(:disabled) {
		background: var(--color-accent-dark);
		transform: translateY(-1px);
	}

	.btn-primary:disabled {
		opacity: 0.6;
		cursor: not-allowed;
	}

	/* Trust note */
	.trust-note {
		margin-top: var(--space-9);
		padding: var(--space-4) var(--space-5);
		background: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-lg);
		display: flex;
		gap: var(--space-4);
		align-items: center;
	}

	.trust-logo {
		width: 22px;
		height: 22px;
		flex-shrink: 0;
		filter: brightness(0) saturate(100%) invert(42%) sepia(80%) saturate(1500%) hue-rotate(220deg) brightness(110%);
	}

	.trust-note p {
		font-size: 0.75rem;
		color: var(--color-text-muted);
		line-height: 1.55;
	}

	.trust-note strong {
		color: var(--color-text);
	}
</style>
