# Emoji Oracle

Emoji Oracle is a lightweight, colorful browser game that teaches players to translate between emojis and messages. Players can decode emoji clues into words, translate text prompts into emojis, type answers, use browser speech recognition where supported, earn streaks, climb a local leaderboard, and share their score.

## Features

- Two challenge directions: Emoji → Message and Message → Emoji.
- Mixed mode for replayable mastery.
- Rookie, Spark, and Pro difficulty levels.
- Timed rounds, streak bonuses, hint penalties, progress tracking, and educational lessons.
- Local leaderboard stored on the player device.
- Share button using native share when available or clipboard fallback.
- Browser-native speech recognition support where available, with typing as the dependable fallback.
- Static, dependency-light architecture that can deploy to any static host.

## Run locally

```bash
npm start
```

Then open `http://localhost:4173`.

## Test

Run the full validation suite:

```bash
npm run test:all
```

Run only the fast unit tests:

```bash
npm run test:unit
```

Run static app smoke tests:

```bash
npm run test:smoke
```

## Architecture

- `index.html` contains the semantic app shell.
- `styles.css` contains the responsive visual design system.
- `src/challenges.js` contains difficulty metadata and challenge content.
- `src/gameLogic.js` contains pure matching, scoring, deck, and share helpers.
- `src/app.js` contains browser rendering, speech recognition, localStorage, and game state.
- `docs/cad-plan.md` contains the CAD architecture, UX, automation, testing, deployment, and roadmap plan.

## Local launch

Preview on the current machine:

```bash
npm start
```

Expose on the local network for phone/tablet testing:

```bash
npm run launch:local
```

## Deployment

The recommended MVP launch target is GitHub Pages because the app is fully static and does not require a backend, build step, database, or secrets. This repository includes a GitHub Actions Pages workflow at `.github/workflows/pages.yml` that runs `npm run test:all` before deploying.

For the full launch checklist, see `docs/launch-plan.md`. Netlify, Vercel, or Cloudflare Pages are also compatible static hosts.
