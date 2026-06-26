<script lang="ts">
	import BlockList from '$lib/components/BlockList.svelte';
	import type { Belief } from '$lib/types';

	let { data } = $props();
	const items = $derived(
		(data.beliefs as Belief[]).map((b) => ({
			id: b.id,
			title: b.title,
			desc: b.statement,
			tags: [b.category, b.source, b.canonical ? 'canonical' : null]
		}))
	);
</script>

<svelte:head><title>Beliefs · Credo</title></svelte:head>

<BlockList
	title="Beliefs"
	sub="Founding axioms credos can adopt and interpret"
	{items}
	empty="No beliefs in the library yet."
/>
