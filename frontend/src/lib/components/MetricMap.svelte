<script lang="ts">
	import { getMetricGeoJSON, getStateMetricGeoJSON } from '../api';
	import { theme } from '$lib/stores/theme';
	import { choroplethScale, accentColor } from '$lib/theme';
	import { ScanSearch } from 'lucide-svelte';

	interface Props {
		metricId: string;
		/** Single county FIPS — used when stateFips is not set */
		geographyId?: string;
		/** Show all counties for this state FIPS (e.g. '17' for Illinois) */
		stateFips?: string;
		/** Shared timeline values — drives which date is displayed */
		values: { period_start: string; value: number }[];
		/** Index into values[] for the currently selected date */
		selectedIndex: number;
		/** When the map is collapsed and then re-expanded, invalidateSize is needed */
		collapsed?: boolean;
	}

	let {
		metricId,
		geographyId,
		stateFips,
		values,
		selectedIndex,
		collapsed = false
	}: Props = $props();

	let map: import('leaflet').Map | undefined;
	let leaflet = $state<typeof import('leaflet') | null>(null);
	let mapReady = $state(false);
	// Track the last date loaded to prevent the $effect from double-loading on initial mount
	let lastLoadedDate = $state<string | null>(null);
	let boxZoomActive = $state(false);
	let error = $state<string | null>(null);
	let currentValue = $state<number | null>(null);
	let currentDate = $state<string | null>(null);

	// Warm sequential scale: pale yellow → deep red (sourced from --choropleth-* tokens)
	const COLORS = choroplethScale();
	const MIN_VALUE = 230_000;
	const MAX_VALUE = 440_000;

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
	let tileLayer: import('leaflet').TileLayer | undefined;

	const TILE_URLS = {
		dark: 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
		light: 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png'
	};
	const TILE_ATTRIBUTION =
		'© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors © <a href="https://carto.com/attributions">CARTO</a>';

	async function loadLayer(L: typeof import('leaflet'), date?: string) {
		try {
			const geojson = stateFips
				? await getStateMetricGeoJSON(stateFips, metricId, date)
				: await getMetricGeoJSON(geographyId ?? '17031', metricId, date);
			const feature = geojson.features?.[0];
			if (!feature) {
				error = 'No map data available for this region yet.';
				return;
			}
			error = null;

			// For single-county view keep the badge; for region view use first feature for date
			if (!stateFips) {
				currentValue = feature.properties.value;
			}
			currentDate = feature.properties.period_start;

			if (geoJsonLayer) {
				geoJsonLayer.remove();
			}

			geoJsonLayer = L.geoJSON(geojson, {
				style: (feat) => ({
					fillColor: valueToColor(feat?.properties.value ?? feature.properties.value),
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
							<div class="credo-popup-meta">${p.metric_id.replace(/_/g, ' ')} · ${formatDate(p.period_start)}</div>
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
			leaflet = L;

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
					.credo-popup-label { font-size: 0.7rem; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; color: var(--color-text-muted); margin-bottom: 0.25rem; }
					.credo-popup-value { font-size: 1.3rem; font-weight: 600; color: var(--color-text); line-height: 1.2; }
					.credo-popup-meta { font-size: 0.75rem; color: var(--color-text-muted); margin-top: 0.25rem; }
					.leaflet-popup-content-wrapper { background: var(--color-surface) !important; border-radius: 10px !important; box-shadow: 0 8px 28px rgba(0,0,0,0.55) !important; border: 1px solid var(--color-border-strong) !important; padding: 0 !important; }
					.leaflet-popup-content { margin: 1rem 1.25rem !important; }
					.leaflet-popup-tip { background: var(--color-surface) !important; }
				`;
				document.head.appendChild(style);
			}

			map = L.map(node, { zoomControl: true, attributionControl: true });

			tileLayer = L.tileLayer(TILE_URLS[$theme], {
				attribution: TILE_ATTRIBUTION,
				subdomains: 'abcd',
				maxZoom: 19
			}).addTo(map);

			await loadLayer(L);
			// Record the date shown on initial load so the $effect doesn't reload it
			lastLoadedDate = values[selectedIndex]?.period_start ?? null;
			mapReady = true;
		})();

		return () => {
			stopBoxZoom();
			map?.remove();
			map = undefined;
		};
	}

	// Swap tile layer when theme changes
	$effect(() => {
		const t = $theme;
		if (!map || !leaflet || !tileLayer) return;
		tileLayer.remove();
		tileLayer = leaflet
			.tileLayer(TILE_URLS[t], {
				attribution: TILE_ATTRIBUTION,
				subdomains: 'abcd',
				maxZoom: 19
			})
			.addTo(map);
	});

	// Reload layer when selectedIndex changes — skip if this date was already loaded
	$effect(() => {
		const date = values[selectedIndex]?.period_start;
		if (leaflet && mapReady && date && date !== lastLoadedDate) {
			lastLoadedDate = date;
			loadLayer(leaflet, date);
		}
	});

	// Invalidate Leaflet size after map is un-collapsed (CSS transition ~300ms)
	$effect(() => {
		if (!collapsed && map && mapReady) {
			const id = setTimeout(() => map?.invalidateSize(), 320);
			return () => clearTimeout(id);
		}
	});

	// ── Box zoom ─────────────────────────────────────────────
	let boxZoomStart: import('leaflet').LatLng | null = null;
	let boxZoomRect: import('leaflet').Rectangle | null = null;
	let boxZoomKeyHandler: ((e: KeyboardEvent) => void) | null = null;

	function onBoxMouseMove(e: import('leaflet').LeafletMouseEvent) {
		if (!boxZoomStart || !leaflet || !map) return;
		boxZoomRect?.remove();
		boxZoomRect = leaflet
			.rectangle(leaflet.latLngBounds(boxZoomStart, e.latlng), {
				weight: 1.5,
				color: accentColor(),
				fillColor: accentColor(),
				fillOpacity: 0.08,
				dashArray: '4 4'
			})
			.addTo(map);
	}

	function onBoxMouseUp(e: import('leaflet').LeafletMouseEvent) {
		if (map && leaflet && boxZoomStart) {
			const bounds = leaflet.latLngBounds(boxZoomStart, e.latlng);
			// Only zoom if the user actually dragged (not just clicked)
			if (bounds.getNorthEast().distanceTo(bounds.getSouthWest()) > 500) {
				map.fitBounds(bounds, { animate: true, padding: [20, 20] });
			}
		}
		stopBoxZoom();
	}

	function onBoxMouseDown(e: import('leaflet').LeafletMouseEvent) {
		if (!map) return;
		boxZoomStart = e.latlng;
		map.on('mousemove', onBoxMouseMove);
		map.once('mouseup', onBoxMouseUp);
	}

	// Single teardown for box zoom — safe to call on cancel, completion, Escape,
	// or unmount. Always removes the document keydown listener so it can't leak.
	function stopBoxZoom() {
		if (boxZoomKeyHandler) {
			document.removeEventListener('keydown', boxZoomKeyHandler);
			boxZoomKeyHandler = null;
		}
		boxZoomRect?.remove();
		boxZoomRect = null;
		boxZoomStart = null;
		if (map) {
			map.off('mousedown', onBoxMouseDown);
			map.off('mousemove', onBoxMouseMove);
			map.off('mouseup', onBoxMouseUp);
			map.dragging.enable();
		}
		boxZoomActive = false;
	}

	function toggleBoxZoom() {
		if (!map) return;
		if (boxZoomActive) {
			stopBoxZoom();
			return;
		}
		boxZoomActive = true;
		map.dragging.disable();
		map.on('mousedown', onBoxMouseDown);
		boxZoomKeyHandler = (e) => {
			if (e.key === 'Escape') stopBoxZoom();
		};
		document.addEventListener('keydown', boxZoomKeyHandler);
	}
</script>

<div class="map-wrap" class:box-zoom-active={boxZoomActive}>
	{#if error}
		<div class="map-error">{error}</div>
	{/if}

	<div {@attach mapAttachment} class="map"></div>

	<!-- Box zoom toggle — sits below Leaflet's zoom control (top-left) -->
	{#if mapReady}
		<button
			class="box-zoom-btn"
			class:active={boxZoomActive}
			onclick={toggleBoxZoom}
			title={boxZoomActive ? 'Cancel box zoom (Esc)' : 'Box zoom: drag to select area'}
			aria-label={boxZoomActive ? 'Cancel box zoom' : 'Activate box zoom'}
		>
			<ScanSearch size={14} aria-hidden="true" />
			{boxZoomActive ? 'Cancel' : 'Box zoom'}
		</button>
	{/if}

	<!-- Metric badge (top-right overlay) -->
	<div class="metric-badge">
		<div class="metric-badge-label">Median Home Price</div>
		{#if stateFips}
			<div class="metric-badge-value">{values.length} counties</div>
		{:else if currentValue !== null}
			<div class="metric-badge-value">{formatUSD(currentValue)}</div>
		{/if}
		{#if currentDate}
			<div class="metric-badge-date">{formatDate(currentDate)}</div>
		{/if}
	</div>

	<!-- Color legend (bottom-left) -->
	<div class="legend">
		<div class="legend-title">Price range</div>
		<div class="legend-scale">
			{#each COLORS as _color, i (i)}
				<div
					class="legend-swatch"
					style="background: var(--choropleth-{i + 1})"
					title={formatUSD(MIN_VALUE + (i / (COLORS.length - 1)) * (MAX_VALUE - MIN_VALUE))}
				></div>
			{/each}
		</div>
		<div class="legend-labels">
			<span>{formatUSD(MIN_VALUE)}</span>
			<span>{formatUSD(MAX_VALUE)}</span>
		</div>
	</div>
</div>

<style>
	.map-wrap {
		position: relative;
		width: 100%;
		height: 100%;
		min-height: 300px;
		border-radius: var(--radius-lg);
		overflow: hidden;
		background: var(--color-bg);
	}

	.map {
		width: 100%;
		height: 100%;
		min-height: 300px;
	}

	.map-error {
		position: absolute;
		top: 1rem;
		left: 50%;
		transform: translateX(-50%);
		background: var(--color-error-bg);
		border: 1px solid var(--color-error-border);
		color: var(--color-error-text);
		font-size: 0.8rem;
		padding: 0.5rem 1rem;
		border-radius: var(--radius-md);
		z-index: 500;
		white-space: nowrap;
	}

	/* ── Box zoom button — below Leaflet zoom control (top-left) ── */
	.box-zoom-btn {
		position: absolute;
		top: 5rem; /* below Leaflet's ~74px zoom widget */
		left: 0.625rem; /* matches Leaflet's control left offset */
		z-index: 400;
		display: flex;
		align-items: center;
		gap: 0.35rem;
		background: var(--color-surface);
		border: 2px solid rgba(0, 0, 0, 0.2);
		border-radius: var(--radius-sm);
		padding: 0.3rem 0.5rem;
		font-family: inherit;
		font-size: 0.7rem;
		font-weight: 600;
		color: var(--color-text);
		cursor: pointer;
		white-space: nowrap;
		box-shadow: none;
		transition:
			background var(--transition-fast),
			border-color var(--transition-fast),
			color var(--transition-fast);
	}

	.box-zoom-btn:hover {
		background: var(--color-bg);
		border-color: color-mix(in srgb, black 40%, transparent);
	}

	.box-zoom-btn.active {
		background: var(--color-accent);
		border-color: var(--color-accent-dark);
		color: white;
	}

	/* ── Metric badge — top-right to clear Leaflet zoom controls ── */
	.metric-badge {
		position: absolute;
		top: 1rem;
		right: 1rem;
		z-index: 400;
		background: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-lg);
		padding: 0.75rem 1rem;
		box-shadow: var(--shadow-md);
		min-width: 160px;
	}

	.metric-badge-label {
		font-size: 0.65rem;
		font-weight: 600;
		letter-spacing: 0.1em;
		text-transform: uppercase;
		color: var(--color-text-faint);
		margin-bottom: 0.2rem;
	}

	.metric-badge-value {
		font-size: 1.35rem;
		font-weight: 600;
		color: var(--color-text);
		line-height: 1.2;
	}

	.metric-badge-date {
		font-size: 0.7rem;
		color: var(--color-text-faint);
		margin-top: 0.15rem;
	}

	/* ── Legend — bottom-left ── */
	.legend {
		position: absolute;
		bottom: 1rem;
		left: 1rem;
		z-index: 400;
		background: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-lg);
		padding: 0.85rem 1rem;
		box-shadow: var(--shadow-md);
		min-width: 200px;
	}

	.legend-title {
		font-size: 0.65rem;
		font-weight: 600;
		letter-spacing: 0.08em;
		text-transform: uppercase;
		color: var(--color-text-faint);
		margin-bottom: 0.6rem;
	}

	.legend-scale {
		display: flex;
		height: 16px;
		border-radius: 6px;
		overflow: hidden;
	}

	.legend-swatch {
		flex: 1;
	}

	.legend-labels {
		display: flex;
		justify-content: space-between;
		margin-top: 0.4rem;
		font-size: 0.7rem;
		font-weight: 500;
		color: var(--color-text-muted);
	}
</style>
