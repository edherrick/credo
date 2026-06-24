import { getEntities } from '$lib/api';

export const ssr = false;

export async function load({ fetch }: { fetch: typeof globalThis.fetch }) {
	const entities = await getEntities(fetch);
	return { entities };
}
