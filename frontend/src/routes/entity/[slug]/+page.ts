import { getEntity } from '$lib/api';
import { error } from '@sveltejs/kit';

export async function load({ params }: { params: { slug: string } }) {
	try {
		const entity = await getEntity(params.slug);
		return { entity };
	} catch {
		throw error(404, 'Politician not found');
	}
}
