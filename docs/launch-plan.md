# Emoji Oracle Launch Plan

## Best launch approach
The best first launch path is **GitHub Pages** because Emoji Oracle is a static, dependency-light application with no required backend, build step, database, or secrets. GitHub Pages keeps the launch simple, free for public repositories, easy to roll back through Git history, and compatible with the current HTML/CSS/JavaScript architecture.

Use Cloudflare Pages or Netlify later if you need edge redirects, advanced preview environments, custom analytics, A/B testing, or serverless APIs.

## Launch execution added to this repo
This repository now includes `.github/workflows/pages.yml`, which:

1. Runs the full Node test suite with `npm run test:all`.
2. Uploads the static repository as a GitHub Pages artifact.
3. Deploys the site to GitHub Pages after tests pass.
4. Supports manual deploys with `workflow_dispatch`.

## How to launch on GitHub Pages

1. Push or merge this branch into `main`.
2. In GitHub, open **Settings → Pages**.
3. Set **Source** to **GitHub Actions**.
4. Open **Actions → Test and deploy static site**.
5. Run the workflow manually, or let it run after pushing to `main`.
6. Confirm the workflow prints the deployed Pages URL.

## Local launch command

```bash
npm run launch:local
```

Then open the machine IP or `http://localhost:4173` if testing on the same device.

## Pre-launch validation checklist

- `npm run test:all` passes.
- The app loads locally with `npm start` or `npm run preview`.
- A human completes at least one Emoji → Message round.
- A human completes at least one Message → Emoji round.
- Leaderboard entries persist after refresh.
- Reset leaderboard works.
- Share uses native sharing or clipboard fallback.
- Speech input is tested in Chrome or Edge with microphone permission.
- Mobile layout is checked at phone width.
- GitHub Pages workflow deploys successfully.

## Post-launch checks

- Open the production URL on desktop and mobile.
- Confirm static assets load with no console errors.
- Confirm `localStorage` leaderboard works on the production domain.
- Confirm share text references Emoji Oracle correctly.
- Ask 3-5 users to play and record confusing prompts or accepted-answer gaps.
