<script lang="ts">
	import { page } from '$app/state';
	import { resolve } from '$app/paths';
	import MetricMap from '$lib/components/MetricMap.svelte';

	const fips = $derived(page.url.searchParams.get('fips') ?? '17031');
	const metricId = $derived(page.url.searchParams.get('metric') ?? 'median_home_price');
</script>

<svelte:head>
	<title>Cook County — Median Home Price · Credo</title>
</svelte:head>

<div class="map-page">
	<div class="map-header">
		<div>
			<h1 class="map-title">Cook County, IL</h1>
			<p class="map-sub">Median Home Price · FIPS {fips}</p>
		</div>
		<a href={resolve('/')} class="back-link">← Back to home</a>
	</div>
	<div class="map-body">
		<MetricMap geographyId={fips} {metricId} />
	</div>
</div>

<style>
	.map-page {
		display: flex;
		flex-direction: column;
		height: calc(100vh - 56px); /* subtract nav height */
	}

	.map-header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 1rem 1.5rem;
		background: white;
		border-bottom: 1px solid #e8e8e4;
		flex-shrink: 0;
	}

	.map-title {
		font-family: 'DM Serif Display', serif;
		font-size: 1.25rem;
		font-weight: 400;
		color: #1a2332;
	}

	.map-sub {
		font-size: 0.8rem;
		color: #94a3b8;
		margin-top: 0.1rem;
	}

	.back-link {
		font-size: 0.85rem;
		font-weight: 500;
		color: #64748b;
		transition: color 0.15s;
	}

	.back-link:hover {
		color: #1a2332;
	}

	.map-body {
		flex: 1;
		padding: 1rem 1.5rem;
		background: #f7f7f5;
		overflow: hidden;
	}

	.map-body :global(.map-wrap) {
		height: 100%;
		border-radius: 10px;
	}

	.map-body :global(.map) {
		height: 100%;
	}
</style>
