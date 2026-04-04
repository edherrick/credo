import { writable } from 'svelte/store';
import type { User } from '../types';

interface AuthState {
	token: string;
	user: User;
}

function createAuthStore() {
	const { subscribe, set } = writable<AuthState | null>(null);

	return {
		subscribe,
		login(token: string, user: User) {
			set({ token, user });
			localStorage.setItem('auth_token', token);
		},
		logout() {
			set(null);
			localStorage.removeItem('auth_token');
		},
		loadFromStorage() {
			const token = localStorage.getItem('auth_token');
			if (token) {
				// Token exists but we don't have user data yet — caller must fetch /me
				return token;
			}
			return null;
		}
	};
}

export const auth = createAuthStore();
