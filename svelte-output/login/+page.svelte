<script lang="ts">
	import { login, getMe } from '$lib/api';
	import { auth } from '$lib/stores/auth';
	import { goto } from '$app/navigation';
	import { resolve } from '$app/paths';

	let email = $state('');
	let password = $state('');
	let error = $state<string | null>(null);
	let submitting = $state(false);

	async function handleSubmit(e: SubmitEvent) {
		e.preventDefault();
		error = null;
		submitting = true;
		try {
			const token = await login(email, password);
			const user = await getMe(token.access_token);
			auth.login(token.access_token, user);
			goto(resolve('/me'));
		} catch (err) {
			error = err instanceof Error ? err.message : 'Login failed';
		} finally {
			submitting = false;
		}
	}
</script>

<svelte:head>
	<title>Log in · Credo</title>
</svelte:head>

<div class="login-page">
	<!-- Logo -->
	<div class="logo-lockup">
		<img src="/logo.svg" alt="Credo" class="logo-mark" />
		<span class="logo-name">Credo</span>
	</div>
	<p class="logo-sub">Open Civic Infrastructure</p>

	<!-- Card -->
	<div class="card">
		<h1 class="card-title">Welcome back</h1>
		<p class="card-sub">Log in to your policy workspace</p>

		<form onsubmit={handleSubmit} class="form">
			<div class="field">
				<label for="email">Email</label>
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
					placeholder="••••••••"
					required
				/>
				<a href={resolve('/forgot-password')} class="forgot">Forgot password?</a>
			</div>

			{#if error}
				<p class="error">{error}</p>
			{/if}

			<button type="submit" class="btn-primary" disabled={submitting}>
				{submitting ? 'Logging in…' : 'Log in'}
			</button>
		</form>

		<div class="divider"><span>or</span></div>

		<button type="button" class="btn-google">Continue with Google</button>

		<p class="register-link">
			No account? <a href={resolve('/register')}>Register →</a>
		</p>
	</div>

	<div class="footer-tenets">
		<span>Open source</span>
		<span>·</span>
		<span>No advertising</span>
		<span>·</span>
		<span>Community-governed</span>
	</div>
</div>

<style>
	.login-page {
		min-height: calc(100vh - var(--nav-height));
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		padding: var(--space-12) var(--space-6);
		position: relative;
	}

	/* Subtle radial glow */
	.login-page::before {
		content: '';
		position: fixed;
		top: 8%;
		left: 50%;
		transform: translateX(-50%);
		width: 800px;
		height: 500px;
		background: radial-gradient(
			ellipse,
			rgba(113, 112, 255, 0.06) 0%,
			rgba(240, 59, 32, 0.04) 55%,
			transparent 100%
		);
		pointer-events: none;
		z-index: 0;
	}

	/* Grid texture */
	.login-page::after {
		content: '';
		position: fixed;
		inset: 0;
		background-image:
			linear-gradient(rgba(255, 255, 255, 0.022) 1px, transparent 1px),
			linear-gradient(90deg, rgba(255, 255, 255, 0.022) 1px, transparent 1px);
		background-size: 52px 52px;
		pointer-events: none;
		z-index: 0;
	}

	.logo-lockup {
		position: relative;
		z-index: 1;
		display: flex;
		align-items: center;
		gap: var(--space-3);
		margin-bottom: var(--space-2);
	}

	.logo-mark {
		width: 56px;
		height: 56px;
		object-fit: contain;
		filter: brightness(0) invert(1);
	}

	.logo-name {
		font-size: 1.5rem;
		font-weight: 510;
		color: #f7f8f8;
		letter-spacing: -0.025em;
	}

	.logo-sub {
		position: relative;
		z-index: 1;
		font-size: 0.6875rem;
		font-weight: 600;
		letter-spacing: 0.14em;
		text-transform: uppercase;
		color: var(--color-text-muted);
		margin-bottom: var(--space-10);
	}

	.card {
		position: relative;
		z-index: 1;
		background: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-xl);
		padding: var(--space-10) var(--space-10);
		width: 100%;
		max-width: 440px;
		box-shadow: 0 32px 72px rgba(0, 0, 0, 0.6);
	}

	.card-title {
		font-family: var(--font-serif);
		font-size: 1.5rem;
		font-weight: 400;
		color: var(--color-text);
		text-align: center;
		margin-bottom: var(--space-2);
	}

	.card-sub {
		font-size: 0.8125rem;
		color: var(--color-text-muted);
		text-align: center;
		margin-bottom: var(--space-8);
	}

	.form {
		display: flex;
		flex-direction: column;
		gap: var(--space-5);
	}

	.field {
		display: flex;
		flex-direction: column;
		gap: var(--space-2);
		position: relative;
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
		transition: border-color var(--transition-fast);
		outline: none;
	}

	.field input::placeholder {
		color: var(--color-text-faint);
	}

	.field input:focus {
		border-color: var(--color-accent);
	}

	.forgot {
		align-self: flex-end;
		font-size: 0.75rem;
		color: var(--color-text-muted);
		transition: color var(--transition-fast);
	}

	.forgot:hover {
		color: var(--color-text);
	}

	.error {
		font-size: 0.8125rem;
		color: var(--color-error-text);
		background: var(--color-error-bg);
		border: 1px solid var(--color-error-border);
		border-radius: var(--radius-md);
		padding: var(--space-3) var(--space-4);
	}

	.btn-primary {
		width: 100%;
		background: var(--color-accent);
		color: white;
		border: none;
		border-radius: var(--radius-md);
		padding: 0.75rem var(--space-6);
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

	.divider {
		display: flex;
		align-items: center;
		gap: var(--space-3);
		margin: var(--space-6) 0;
	}

	.divider::before,
	.divider::after {
		content: '';
		flex: 1;
		height: 1px;
		background: var(--color-border);
	}

	.divider span {
		font-size: 0.6875rem;
		color: var(--color-text-faint);
	}

	.btn-google {
		width: 100%;
		background: transparent;
		border: 1px solid var(--color-border);
		border-radius: var(--radius-md);
		padding: 0.75rem;
		font-size: 0.8125rem;
		color: var(--color-text-muted);
		font-family: inherit;
		cursor: pointer;
		transition:
			border-color var(--transition-fast),
			color var(--transition-fast);
	}

	.btn-google:hover {
		border-color: var(--color-border-strong);
		color: var(--color-text);
	}

	.register-link {
		text-align: center;
		margin-top: var(--space-6);
		font-size: 0.8125rem;
		color: var(--color-text-muted);
	}

	.register-link a {
		color: var(--color-accent);
		font-weight: 500;
	}

	.register-link a:hover {
		text-decoration: underline;
	}

	.footer-tenets {
		position: relative;
		z-index: 1;
		margin-top: var(--space-8);
		display: flex;
		gap: var(--space-4);
		font-size: 0.6875rem;
		color: var(--color-text-faint);
	}
</style>
