export const ssr = false;

import { getCredos } from '$lib/api';

export async function load({ fetch }: { fetch: typeof globalThis.fetch }) {
	try {
		return { credos: await getCredos(fetch) };
	} catch {
		return { credos: [] };
	}
}
