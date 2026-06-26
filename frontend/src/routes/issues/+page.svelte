<script lang="ts">
	import BlockList from '$lib/components/BlockList.svelte';
	import type { Issue } from '$lib/types';

	let { data } = $props();
	const items = $derived(
		(data.issues as Issue[]).map((i) => ({
			id: i.id,
			title: i.title,
			desc: i.description,
			tags: [i.category, i.canonical ? 'canonical' : null]
		}))
	);
</script>

<svelte:head><title>Issues · Credo</title></svelte:head>

<BlockList
	title="Issues"
	sub="Abstract policy areas an agenda instantiates"
	{items}
	empty="No issues in the library yet."
/>
