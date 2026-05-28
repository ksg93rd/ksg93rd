# Emoji Oracle CAD Blueprint

## 1. Project Understanding
Emoji Oracle is a lightweight browser game where players translate emoji strings into messages and translate words or sentences back into emojis. It supports typed answers, optional browser speech recognition, beginner-to-pro difficulty, learning feedback, a local leaderboard, and shareable score text.

## 2. Important Clarifying Questions
The first version is intentionally offline-first and local-device only. Future decisions include whether accounts, cloud leaderboards, classroom rooms, AI-generated prompts, or multiplayer should be added.

## 3. Recommended Architecture
The MVP uses static HTML, CSS, and native JavaScript modules to minimize dependencies and make hosting simple on GitHub Pages, Netlify, Vercel, or any static server. Game data lives in a challenge catalog, scoring and answer evaluation live in a pure logic module, and browser-only capabilities are isolated in the app controller.

## 4. UX/UI Strategy
The interface is mobile-first, colorful, glassy, and game-like. It uses high-contrast cards, large prompt typography, clear action buttons, immediate feedback, and short lessons to reduce cognitive load while preserving energy and delight.

## 5. Automation Opportunities
A future n8n workflow can generate new challenge packs, review inappropriate content, publish weekly leaderboard digests, send classroom progress emails, and sync anonymized game analytics into Airtable, Google Sheets, Supabase, or a CRM.

## 6. Psychological/Behavioral Optimization
The game uses immediate feedback, variable prompt formats, streaks, timed rounds, visible progress, low-stakes hints, and replayable difficulty levels. These mechanics support mastery, curiosity, competence, and retention without overwhelming new players.

## 7. File Structure
- `index.html`: semantic app shell and game controls.
- `styles.css`: responsive visual system and game UI.
- `src/challenges.js`: prompt catalog and difficulty metadata.
- `src/gameLogic.js`: pure scoring, normalization, matching, deck, and sharing utilities.
- `src/app.js`: browser state, events, speech recognition, local leaderboard, and rendering.
- `tests/gameLogic.test.js`: Node unit tests for core game logic.

## 8. Database & API Design
The MVP uses `localStorage` for preferences and leaderboard entries. A production cloud version should use tables such as `profiles`, `challenge_packs`, `rounds`, `answers`, and `leaderboard_entries`, with row-level security and rate-limited API routes.

## 9. Implementation Plan
The current implementation prioritizes a fast static MVP, accessible controls, a reusable challenge model, browser speech support where available, local persistence, and testable scoring logic.

## 10. Production-Ready Code
The app has no runtime build step, avoids unnecessary dependencies, separates data from logic, escapes leaderboard names before rendering, and keeps reusable functions testable outside the browser.

## 11. n8n Workflow Logic
Recommended workflow: Cron trigger → load prompt themes from Google Sheets/Airtable → OpenAI content generation → moderation/safety filter → human approval step → commit challenge JSON to GitHub or insert into Supabase → notify Discord/Slack → weekly digest email. Add retry policies, idempotency keys, and error branches for every external service.

## 12. Security & Performance Notes
The static MVP avoids server-side attack surface. User display names are escaped before insertion into the leaderboard. Speech recognition stays browser-native. Future APIs should add authentication, request validation, rate limiting, audit logs, and content moderation.

## 13. Testing & QA
Core matching and scoring are covered with Node tests. Manual QA should verify keyboard navigation, speech fallback, mobile layout, localStorage persistence, leaderboard reset, share fallback, and high-contrast readability.

## 14. Deployment Instructions
Run `npm test`, then serve the repository with `npm start` or deploy the static files directly. No secrets are required for the MVP.

## 15. Recommended Enhancements
Add AI-generated daily puzzles, classroom packs, multiplayer rooms, badges, seasonal challenge themes, accessibility settings, cloud save, and teacher dashboards.

## 16. Future Scalability Roadmap
Phase 1 is static local play. Phase 2 adds authenticated cloud leaderboards and prompt packs. Phase 3 adds AI moderation and generation pipelines. Phase 4 adds real-time multiplayer, classrooms, subscriptions, and analytics-driven personalization.
