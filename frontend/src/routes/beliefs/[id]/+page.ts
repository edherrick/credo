export const ssr = false;

import { error } from '@sveltejs/kit';
import { getBelief } from '$lib/api';

export async function load({
	params,
	fetch
}: {
	params: { id: string };
	fetch: typeof globalThis.fetch;
}) {
	try {
		return { belief: await getBelief(params.id, fetch) };
	} catch {
		throw error(404, 'Belief not found');
	}
}
