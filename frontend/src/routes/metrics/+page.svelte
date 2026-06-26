<script lang="ts">
	import { resolve } from '$app/paths';
	import BlockList from '$lib/components/BlockList.svelte';
	import type { Metric } from '$lib/types';

	let { data } = $props();
	const items = $derived(
		(data.metrics as Metric[]).map((m) => ({
			id: m.id,
			title: m.display_name,
			desc: m.description,
			tags: [m.unit, m.data_source],
			href: resolve(`/metrics/${m.id}`)
		}))
	);
</script>

<svelte:head><title>Metrics · Credo</title></svelte:head>

<BlockList
	title="Metrics"
	sub="Measurable indicators — open one to see it mapped"
	{items}
	empty="No metrics in the library yet."
/>
