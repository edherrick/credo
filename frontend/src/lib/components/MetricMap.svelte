<script lang="ts">
	import { getMetricGeoJSON, getMetricValues } from '../api';

	interface Props {
		metricId: string;
		geographyId: string;
	}

	let { metricId, geographyId }: Props = $props();

	let map: import('leaflet').Map | undefined;
	let error = $state<string | null>(null);
	let currentValue = $state<number | null>(null);
	let currentDate = $state<string | null>(null);
	let allValues = $state<{ date: string; value: number }[]>([]);
	let selectedDate = $state<string | null>(null);

	// Warm sequential scale: pale yellow → deep red
	const COLORS = ['#ffffb2', '#fecc5c', '#fd8d3c', '#f03b20', '#bd0026'];
	const MIN_VALUE = 250_000;
	const MAX_VALUE = 400_000;

	function valueToColor(value: number): string {
		const ratio = Math.min(1, Math.max(0, (value - MIN_VALUE) / (MAX_VALUE - MIN_VALUE)));
		const index = Math.min(COLORS.length - 1, Math.floor(ratio * COLORS.length));
		return COLORS[index];
	}

	function formatUSD(value: number): string {
		return new Intl.NumberFormat('en-US', {
			style: 'currency',
			currency: 'USD',
			maximumFractionDigits: 0
		}).format(value);
	}

	function formatDate(d: string): string {
		return new Date(d + 'T00:00:00').toLocaleDateString('en-US', {
			year: 'numeric',
			month: 'short'
		});
	}

	let geoJsonLayer: import('leaflet').GeoJSON | undefined;

	async function loadLayer(L: typeof import('leaflet'), date?: string) {
		try {
			const geojson = await getMetricGeoJSON(geographyId, metricId, date);
			const feature = geojson.features?.[0];
			if (!feature) return;

			currentValue = feature.properties.value;
			currentDate = feature.properties.date;

			if (geoJsonLayer) {
				geoJsonLayer.remove();
			}

			geoJsonLayer = L.geoJSON(geojson, {
				style: () => ({
					fillColor: valueToColor(feature.properties.value),
					fillOpacity: 0.72,
					weight: 1.5,
					color: '#c0392b',
					opacity: 0.8
				}),
				onEachFeature(feat, layer) {
					const p = feat.properties;
					layer.bindPopup(`
						<div class="credo-popup">
							<div class="credo-popup-label">${p.geography_name}</div>
							<div class="credo-popup-value">${formatUSD(p.value)}</div>
							<div class="credo-popup-meta">${p.metric_id.replace(/_/g, ' ')} · ${formatDate(p.date)}</div>
						</div>
					`);
				}
			}).addTo(map!);

			// Fit bounds on first load
			if (!date) {
				map!.fitBounds(geoJsonLayer.getBounds(), { padding: [40, 40] });
			}
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to load map data';
		}
	}

	function mapAttachment(node: HTMLDivElement) {
		(async () => {
			const L = (await import('leaflet')).default;

			if (!document.querySelector('#leaflet-css')) {
				const link = document.createElement('link');
				link.id = 'leaflet-css';
				link.rel = 'stylesheet';
				link.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css';
				document.head.appendChild(link);
			}

			if (!document.querySelector('#credo-map-css')) {
				const style = document.createElement('style');
				style.id = 'credo-map-css';
				style.textContent = `
					.credo-popup { font-family: 'DM Sans', system-ui, sans-serif; min-width: 160px; }
					.credo-popup-label { font-size: 0.7rem; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; color: #94a3b8; margin-bottom: 0.25rem; }
					.credo-popup-value { font-size: 1.3rem; font-weight: 600; color: #1a2332; line-height: 1.2; }
					.credo-popup-meta { font-size: 0.75rem; color: #94a3b8; margin-top: 0.25rem; }
					.leaflet-popup-content-wrapper { border-radius: 10px !important; box-shadow: 0 8px 24px rgba(0,0,0,0.12) !important; border: 1px solid #e8e8e4; padding: 0 !important; }
					.leaflet-popup-content { margin: 1rem 1.25rem !important; }
					.leaflet-popup-tip { background: white !important; }
				`;
				document.head.appendChild(style);
			}

			map = L.map(node, { zoomControl: true, attributionControl: true });

			// CartoDB Positron — clean, minimal basemap
			L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
				attribution:
					'© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors © <a href="https://carto.com/attributions">CARTO</a>',
				subdomains: 'abcd',
				maxZoom: 19
			}).addTo(map);

			// Load time series for the slider
			try {
				const series = await getMetricValues(geographyId, metricId);
				allValues = series.values;
				if (allValues.length > 0) {
					selectedDate = allValues[allValues.length - 1].date;
				}
			} catch {
				// non-fatal — map still works without the slider
			}

			await loadLayer(L);
		})();

		return () => {
			map?.remove();
		};
	}

	async function handleDateChange(date: string) {
		selectedDate = date;
		const L = (await import('leaflet')).default;
		await loadLayer(L, date);
	}
</script>

<div class="map-wrap">
	{#if error}
		<div class="map-error">{error}</div>
	{/if}

	<div {@attach mapAttachment} class="map"></div>

	<!-- Metric value badge (top-left overlay) -->
	{#if currentValue !== null}
		<div class="metric-badge">
			<div class="metric-badge-label">Median Home Price</div>
			<div class="metric-badge-value">{formatUSD(currentValue)}</div>
			{#if currentDate}
				<div class="metric-badge-date">{formatDate(currentDate)}</div>
			{/if}
		</div>
	{/if}

	<!-- Color legend (bottom-right) -->
	<div class="legend">
		<div class="legend-title">Price range</div>
		<div class="legend-scale">
			{#each COLORS as color, i (i)}
				<div
					class="legend-swatch"
					style="background:{color}"
					title={formatUSD(MIN_VALUE + (i / (COLORS.length - 1)) * (MAX_VALUE - MIN_VALUE))}
				></div>
			{/each}
		</div>
		<div class="legend-labels">
			<span>{formatUSD(MIN_VALUE)}</span>
			<span>{formatUSD(MAX_VALUE)}</span>
		</div>
	</div>

	<!-- Time slider (bottom-center) -->
	{#if allValues.length > 1}
		<div class="time-slider">
			<label class="time-label">
				Year
				<select
					value={selectedDate ?? ''}
					onchange={(e) => handleDateChange((e.target as HTMLSelectElement).value)}
				>
					{#each allValues as v (v.date)}
						<option value={v.date}>{formatDate(v.date)}</option>
					{/each}
				</select>
			</label>
		</div>
	{/if}
</div>

<style>
	.map-wrap {
		position: relative;
		width: 100%;
		height: 100%;
		min-height: 500px;
		border-radius: 10px;
		overflow: hidden;
		background: #f0efeb;
	}

	.map {
		width: 100%;
		height: 100%;
		min-height: 500px;
	}

	.map-error {
		position: absolute;
		top: 1rem;
		left: 50%;
		transform: translateX(-50%);
		background: #fef2f2;
		border: 1px solid #fecaca;
		color: #991b1b;
		font-size: 0.8rem;
		padding: 0.5rem 1rem;
		border-radius: 6px;
		z-index: 500;
		white-space: nowrap;
	}

	/* ── Metric badge ──────────────────────────────── */
	.metric-badge {
		position: absolute;
		top: 1rem;
		left: 1rem;
		z-index: 400;
		background: white;
		border: 1px solid #e8e8e4;
		border-radius: 10px;
		padding: 0.75rem 1rem;
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
		min-width: 150px;
	}

	.metric-badge-label {
		font-size: 0.65rem;
		font-weight: 600;
		letter-spacing: 0.1em;
		text-transform: uppercase;
		color: #94a3b8;
		margin-bottom: 0.2rem;
	}

	.metric-badge-value {
		font-size: 1.35rem;
		font-weight: 600;
		color: #1a2332;
		line-height: 1.2;
	}

	.metric-badge-date {
		font-size: 0.7rem;
		color: #94a3b8;
		margin-top: 0.15rem;
	}

	/* ── Legend ────────────────────────────────────── */
	.legend {
		position: absolute;
		bottom: 2rem;
		right: 1rem;
		z-index: 400;
		background: white;
		border: 1px solid #e8e8e4;
		border-radius: 8px;
		padding: 0.6rem 0.75rem;
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
		min-width: 140px;
	}

	.legend-title {
		font-size: 0.65rem;
		font-weight: 600;
		letter-spacing: 0.08em;
		text-transform: uppercase;
		color: #94a3b8;
		margin-bottom: 0.4rem;
	}

	.legend-scale {
		display: flex;
		height: 10px;
		border-radius: 4px;
		overflow: hidden;
	}

	.legend-swatch {
		flex: 1;
	}

	.legend-labels {
		display: flex;
		justify-content: space-between;
		margin-top: 0.3rem;
		font-size: 0.65rem;
		color: #94a3b8;
	}

	/* ── Time slider ───────────────────────────────── */
	.time-slider {
		position: absolute;
		bottom: 2rem;
		left: 50%;
		transform: translateX(-50%);
		z-index: 400;
		background: white;
		border: 1px solid #e8e8e4;
		border-radius: 8px;
		padding: 0.5rem 0.75rem;
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
	}

	.time-label {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		font-size: 0.7rem;
		font-weight: 600;
		letter-spacing: 0.08em;
		text-transform: uppercase;
		color: #94a3b8;
	}

	.time-label select {
		font-family: inherit;
		font-size: 0.8rem;
		font-weight: 600;
		color: #1a2332;
		border: none;
		background: transparent;
		cursor: pointer;
		outline: none;
	}
</style>
