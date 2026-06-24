import { defineConfig } from 'vitest/config';
import { sveltekit } from '@sveltejs/kit/vite';

export default defineConfig({
	plugins: [sveltekit()],
	server: {
		proxy: {
			'/api': 'http://localhost:8000'
		}
	},
	// `vite preview` (used by test.sh and Playwright's webServer on :4173) does not
	// inherit `server.proxy`, so mirror it here or /api calls 404 against the prod build.
	preview: {
		proxy: {
			'/api': 'http://localhost:8000'
		}
	},
	test: {
		expect: { requireAssertions: true },
		projects: [
			{
				extends: './vite.config.ts',
				test: {
					name: 'server',
					environment: 'node',
					include: ['src/**/*.{test,spec}.{js,ts}'],
					exclude: ['src/**/*.svelte.{test,spec}.{js,ts}']
				}
			}
		]
	}
});
