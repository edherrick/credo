// JS accessor for the design-token color scales — for canvas / Leaflet / SVG
// contexts that can't reference CSS var(). Values are read live from the tokens
// defined in app.css, so app.css stays the single source of truth; the literals
// below are only SSR fallbacks (and match the tokens). Data colors are
// theme-independent, so reading once at module load is fine.

function readVar(name: string, fallback: string): string {
	if (typeof document === 'undefined') return fallback;
	const v = getComputedStyle(document.documentElement).getPropertyValue(name).trim();
	return v || fallback;
}

/** Sequential choropleth scale (pale yellow → deep red) — mirrors --choropleth-1..5. */
export function choroplethScale(): string[] {
	const fallback = ['#ffffb2', '#fecc5c', '#fd8d3c', '#f03b20', '#bd0026'];
	return fallback.map((fb, i) => readVar(`--choropleth-${i + 1}`, fb));
}

/** Compare-series line colors for the metric chart. */
export function compareSeriesColors(): string[] {
	return [readVar('--cat-teal', '#0d9488'), readVar('--cat-purple', '#7c3aed')];
}

/** The brand accent, for canvas overlays (box-zoom rectangle, etc.). */
export function accentColor(): string {
	return readVar('--color-accent', '#f03b20');
}
