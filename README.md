# GenieBot Smart Contract Reviewer

A lightweight, ready-to-deploy contract risk screener that produces schema-compliant JSON outputs for GenieBot.pro.

## Features

### Application Enhancements
1. Automatic theme selection across 10 US agreement types.
2. Penalty extraction with annualized interest estimation.
3. Asymmetry detection for sanctions and termination rights.
4. Schema validation to guarantee deploy-safe JSON.
5. Export-ready output for API ingestion or downstream workflows.

### User Experience Enhancements
1. Sample contract loader for instant demos.
2. Copy + download buttons for quick sharing.
3. Real-time analysis metadata with theme/risk badges.
4. Accessible, high-contrast layout optimized for scanning.
5. Pretty-print toggle for readable or compact JSON.

## Quick Start

```bash
python -m http.server 8080
```

Then open `http://localhost:8080` in your browser.

## Usage

1. Paste contract text between `<<<CONTRACT_TEXT_START>>>` and `<<<CONTRACT_TEXT_END>>>`.
2. Click **Analyze Contract**.
3. Copy or download the JSON output for use in your workflow.

## Deployment

This is a static site. Deploy the contents of this folder to any static hosting service (Netlify, Vercel, GitHub Pages, S3, etc.).
