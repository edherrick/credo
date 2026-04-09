import { writable } from 'svelte/store';
import { browser } from '$app/environment';

export type Theme = 'dark' | 'light';

function createThemeStore() {
	const stored = browser ? (localStorage.getItem('credo-theme') as Theme | null) : null;
	const initial: Theme = stored ?? 'dark';

	const { subscribe, update } = writable<Theme>(initial);

	function apply(theme: Theme) {
		if (browser) {
			document.documentElement.setAttribute('data-theme', theme);
			localStorage.setItem('credo-theme', theme);
		}
	}

	apply(initial);

	return {
		subscribe,
		toggle() {
			update((current) => {
				const next: Theme = current === 'dark' ? 'light' : 'dark';
				apply(next);
				return next;
			});
		}
	};
}

export const theme = createThemeStore();
