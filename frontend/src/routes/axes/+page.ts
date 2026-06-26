export const ssr = false;

import { getAxes } from '$lib/api';

export async function load({ fetch }: { fetch: typeof globalThis.fetch }) {
	try {
		return { axes: await getAxes(fetch) };
	} catch {
		return { axes: [] };
	}
}
