# Credo Frontend

SvelteKit + Leaflet app. Built with [`sv`](https://github.com/sveltejs/cli).

## Developing

```sh
npm install        # first time only
npm run dev        # Vite dev server on :5173 (HMR)
```

Or run the full stack (DB + backend + frontend) from the repo root with `bash dev.sh`.

The Vite dev server proxies `/api` → `http://localhost:8000`, so there are no CORS issues in development.

## Building

```sh
npm run build      # production build
npm run preview    # preview the production build
```

## Tooling

The toolchain is deliberately layered: **each tool owns one job** and they're chained so they never overlap or fight over the same line.

| Tool | Config file | Owns |
|------|-------------|------|
| Prettier | `.prettierrc` | Formatting (whitespace, quotes, commas) |
| ESLint | `eslint.config.js` | JS/TS/Svelte *logic* correctness |
| Stylelint | `.stylelintrc.json` | CSS *token discipline* (design system) |
| svelte-check | `tsconfig.json` | Type checking |

`npm run lint` chains the first three:

```jsonc
"lint": "prettier --check . && eslint . && npm run lint:css"
```

It runs **Prettier → ESLint → Stylelint** in sequence and fails fast (if Prettier finds problems, ESLint never runs). Type-checking (`svelte-check`) is a *separate* command, not part of `lint`.

### 1. Prettier — formatting only

```jsonc
{
  "useTabs": true,
  "singleQuote": true,
  "trailingComma": "none",
  "printWidth": 100,
  "plugins": ["prettier-plugin-svelte"]
}
```

Tabs, single quotes, no trailing commas, 100-char lines. `prettier-plugin-svelte` (plus the `*.svelte → parser: "svelte"` override) formats `.svelte` files. `--check` verifies; `npm run format` rewrites.

This is the **only** tool allowed opinions about style — the other two are configured to stay out of its way.

### 2. ESLint — logic, flat config

`eslint.config.js` uses the modern **flat config** (`defineConfig` with an array of layers applied in order):

```js
includeIgnoreFile(gitignorePath),   // reuse .gitignore so it skips build output
js.configs.recommended,             // core JS rules
ts.configs.recommended,             // typescript-eslint rules
svelte.configs.recommended,         // Svelte component rules
prettier,                           // ← disables all formatting rules
svelte.configs.prettier,            // ← same, for Svelte-specific ones
```

The two `prettier` entries come **last on purpose** — `eslint-config-prettier` turns *off* every ESLint rule that overlaps with formatting, so ESLint never reports something Prettier would just reformat. Order matters: the last layer wins.

Custom rules:

- **`'no-undef': 'off'`** — TypeScript already detects undefined variables; typescript-eslint explicitly recommends disabling this on TS projects.
- **`'@typescript-eslint/no-unused-vars'`** is an `error`, but with `^_` ignore patterns — so `_x`, unused `catch (_e)`, and `{#each items as _x, i}` index loops are intentionally allowed.

Two scoped layers at the bottom:

- The `**/*.svelte` block wires up the TS parser for Svelte files (`projectService: true` enables type-aware linting; `svelteConfig` lets it understand runes mode).
- The last block turns off `svelte/no-navigation-without-resolve` for just `Button.svelte` and `Card.svelte` — generic href-forwarding primitives where the `href` is a caller-supplied prop, so the rule doesn't apply.

### 3. Stylelint — design-token enforcement

Custom to this repo: it enforces the design system (see `DESIGN.md` and the design-token section of the root `CLAUDE.md`). Runs on `src/**/*.{css,svelte}` via two plugins:

```jsonc
"plugins": [
  "stylelint-value-no-unknown-custom-properties",
  "stylelint-declaration-strict-value"
]
```

**Rule A — no undefined tokens** (applies everywhere):

```jsonc
"csstools/value-no-unknown-custom-properties": [
  true, { "importFrom": ["src/app.css"] }
]
```

Flags any `var(--something)` not defined in `app.css`. Typos like `var(--color-navvy)` or references to nonexistent tokens error out. `app.css` is the single source of truth; this keeps references honest.

**Rule B — no raw color values** (in the `**/*.svelte` override):

```jsonc
"scale-unlimited/declaration-strict-value": [
  ["/color/", "fill", "stroke", "background"],
  { "ignoreValues": ["transparent", "currentColor", "...", "/^color-mix\\(/", "/gradient\\(/"],
    "disableFix": true }
]
```

For any property matching `/color/` (`color`, `background-color`, `border-color`…) plus `fill`/`stroke`/`background`, the value **must be a `var(--token)`** — not a raw `#hex` or `rgba()`. `ignoreValues` carves out legitimate keywords (`transparent`, `currentColor`, `white`, `black`) and lets `color-mix()` / gradients through. `disableFix: true` reports without auto-rewriting (there's no safe automatic fix — you must pick the right token). The `.svelte` override sets `customSyntax: "postcss-html"` so Stylelint can parse the `<style>` block inside components.

Net effect: you cannot hardcode a color in a component — you're forced to add/use a token in `app.css`.

### 4. svelte-check — types (separate)

```jsonc
"check": "svelte-kit sync && svelte-check --tsconfig ./tsconfig.json"
```

`svelte-kit sync` regenerates `.svelte-kit/` types (route params, generated `$types`), then `svelte-check` type-checks `.svelte`/`.ts` against the strict `tsconfig.json`. **Run this before pushing** — it is not part of `npm run lint`.

## Commands

| Command | What |
|---------|------|
| `npm run dev` | Vite dev server (:5173, HMR) |
| `npm run build` | Production build |
| `npm run preview` | Preview the production build |
| `npm run lint` | Prettier check + ESLint + Stylelint (the full gate) |
| `npm run lint:css` | Stylelint only — fastest way to check token discipline |
| `npm run format` | Prettier auto-fix |
| `npm run check` | Type check (run before pushing) |
| `npm run test:unit` | Vitest unit tests |
| `npm run test:e2e` | Playwright E2E (needs both servers — `bash test.sh`) |

A practical workflow: `npm run format` first (clears Prettier noise), then `npm run lint` for real ESLint/Stylelint issues, then `npm run check` for types.
