import { getEntities } from '$lib/api';

export const ssr = false;

export async function load() {
	const entities = await getEntities();
	return { entities };
}
