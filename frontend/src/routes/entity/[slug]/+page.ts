import { getEntity } from '$lib/api';
import { error } from '@sveltejs/kit';

export async function load({ params, fetch }: { params: { slug: string }; fetch: typeof globalThis.fetch }) {
	try {
		const entity = await getEntity(params.slug, fetch);
		return { entity };
	} catch {
		throw error(404, 'Politician not found');
	}
}
