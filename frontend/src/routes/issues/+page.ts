export const ssr = false;

import { getIssues } from '$lib/api';

export async function load({ fetch }: { fetch: typeof globalThis.fetch }) {
	try {
		return { issues: await getIssues(fetch) };
	} catch {
		return { issues: [] };
	}
}
