<script lang="ts">
	import BlockList from '$lib/components/BlockList.svelte';
	import type { Axis } from '$lib/types';

	let { data } = $props();
	const items = $derived(
		(data.axes as Axis[]).map((a) => ({
			id: a.id,
			title: a.label,
			desc: a.description,
			tags: [a.family, a.canonical ? 'canonical' : null]
		}))
	);
</script>

<svelte:head><title>Axes · Credo</title></svelte:head>

<BlockList
	title="Axes"
	sub="Scoring dimensions credos weight and align against"
	{items}
	empty="No axes in the library yet."
/>
