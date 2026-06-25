# Credo — Design System

> The visual language and how it's structured. Tokens live in `frontend/src/app.css`;
> reusable UI lives in `frontend/src/lib/components/ui/`. Stylelint enforces token usage.

## Identity — "civic cartographic ledger"

Credo is open civic infrastructure: communities tracking measurable outcomes on maps,
arguing from stated beliefs, and holding entities accountable. The look is **deep navy +
a warm data-accent + an editorial serif** — it should read as cartographic, evidence-based,
and editorial, not as a generic dark SaaS theme.

Three deliberate moves carry the identity:

1. **One warm accent, with a job.** `--color-accent` (`#f03b20`, the hot end of the
   choropleth) is reserved for **interactive / live** signals only — primary CTAs, the
   active tab, focus rings. It is never decorative.
2. **Data has its own colors.** The map uses the sequential **choropleth** scale; entity
   scoring uses the diverging **accountability** scale (`--score-hero … --score-villain`,
   green→crimson). Data-red is deep crimson (`--score-villain`), *not* the brand accent, so
   "the app is talking to you" never collides with "this datum is hot/bad."
3. **Three type voices.** Serif = civic/editorial authority; sans = working UI/body;
   **mono = data & labels**. The mono voice (metric values, geo codes, eyebrows, badge
   labels) is what makes the product read cartographic rather than templated.

## Color (tokens in `app.css`)

| Role | Token | Notes |
|---|---|---|
| Navy chrome | `--color-navy` `#07111e` | nav + credo bar (always dark, both themes) |
| Page / surface | `--color-bg` `#0c1929` / `--color-surface` `#132338` | luminance stepping = elevation |
| Borders | `--color-border` / `--color-border-strong` | whisper-thin cool separators |
| Text | `--color-text` / `-muted` / `-faint` | cool blue-grays; never pure `#fff` for body |
| Accent (interactive) | `--color-accent` / `-dark` | CTAs, active tab, focus — **interactive only** |
| Data — value | `--choropleth-1…5` | sequential yellow→red, the map |
| Data — score | `--score-hero/positive/neutral/negative/villain` | diverging green→crimson |
| On-navy overlays | `--overlay-1/2/3`, `--text-on-navy` | white fills/borders/text on the dark chrome |

Elevation is **background luminance stepping** (deeper = darker, raised = lighter surface)
plus thin cool borders — not heavy drop shadows.

## Type — three voices

- **Serif** `--font-serif` (DM Serif Display) — civic/editorial authority: credo titles,
  section headings, beliefs, hero numbers. Display only, used with restraint.
- **Sans** `--font-sans` (Inter, `"cv01","ss03"` globally) — working UI and body.
- **Mono** `--font-mono` — data & labels: metric values, geo/FIPS codes, eyebrows/overlines,
  badge category labels. This is the ledger voice.

## Components

Reusable UI is hand-rolled primitives in `lib/components/ui/` (typed `variant` props →
autocomplete). Build features from these, not from copy-pasted CSS:

- **Button** — `variant: primary | ghost | subtle | danger`, `size: sm | md`. `primary` is
  the only place a solid accent appears.
- **Field** — label + input/textarea + hint/error, accent focus ring. `bind:value`.
- **Card** — translucent surface + cool border; `interactive` adds hover lift.
- **Section** — serif `title` + mono `eyebrow` + `sub`; `alt` = raised surface.
- **Badge** — mono small-caps; `tone` incl. the score tiers.
- **EmptyState** — quiet, centered, action-oriented.

Numbered markers (`01 / 02`) are reserved for genuinely ordered content (the Founding
Beliefs axiom list) — not decoration.

## How it's structured

```
tokens (app.css)  →  primitives (lib/components/ui)  →  features (routes, components)
```

- Change a value once in `app.css`; it propagates everywhere.
- Change a component's look once in its `ui/` primitive.
- **Stylelint** (`npm run lint`) flags raw hex/`rgba` where a token belongs and any
  `var(--typo)` that isn't defined in `app.css` — so the available tokens stay discoverable
  and drift gets caught. Component styles use scoped `<style>` referencing tokens; never
  `:global()` in a component (global rules belong in `app.css`).

## Do / Don't

**Do** — reserve the accent for interactive/live; use the score scale (crimson villain) for
data, never the brand accent; pick the type voice by role (serif authority / sans UI / mono
data); build from `ui/` primitives; reference tokens, never raw values.

**Don't** — use the brand red to mean "bad" (that's `--score-villain`); use pure white for
body text; introduce raw hex/`rgba` in components (Stylelint will flag it); re-define a
button/field/card in a feature file — extend or add a primitive instead.
