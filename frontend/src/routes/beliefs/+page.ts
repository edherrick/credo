export const ssr = false;

import { getBeliefs } from '$lib/api';

export async function load({ fetch }: { fetch: typeof globalThis.fetch }) {
	try {
		return { beliefs: await getBeliefs(fetch) };
	} catch {
		return { beliefs: [] };
	}
}
