export const ssr = false;

import { getCredos } from '$lib/api';

export async function load({ fetch }: { fetch: typeof globalThis.fetch }) {
	try {
		const credos = await getCredos(fetch);
		return { credos };
	} catch {
		return { credos: [] };
	}
}
