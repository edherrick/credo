export const ssr = false;

import { getCredos } from '$lib/api';

export async function load() {
	try {
		const credos = await getCredos();
		return { credos };
	} catch {
		return { credos: [] };
	}
}
