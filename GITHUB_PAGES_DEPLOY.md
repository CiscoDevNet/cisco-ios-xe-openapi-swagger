# GitHub Pages Deployment

## How It Works

This site is deployed automatically using **GitHub Actions**. Every push to main triggers the workflow at .github/workflows/deploy-pages.yml.

### Deployment Flow

1. **Push to main branch** - triggers GitHub Actions
2. **Workflow prepares deploy directory** - copies only website-relevant files
3. **Uploads artifact** - uses `actions/upload-pages-artifact`
4. **Deploys to Pages** - uses `actions/deploy-pages`

No manual setup required. Just push and it deploys.

### What Gets Deployed

| Included | Description |
|----------|-------------|
| releases/ | Per-release specs, YANG tree pages (~4,200), search indexes, device data, exports (Postman/Bruno archives are built during the deploy) |
| swagger-*-model/ | The 8 model viewers (HTML; specs are read from `releases/<ver>/`) |
| yang-trees/ | Redirect stubs to the default release's tree pages |
| docs/ | Getting Started guide, Project Summary |
| tools/ | Postman collection and environment |
| assets/ | Shared CSS (site, viewer, tree-page themes), JS, icons, vendored Swagger UI |
| *.html | Hub and tool pages, 404, App Map, Changelog |
| *.js | Search engine, recent favorites |
| *.json | Search index, YANG accountability data, device datasets |
| README.md | Repository documentation |
| .nojekyll | Disables Jekyll processing |

| Excluded | Reason |
|----------|--------|
| references/ | YANG source modules (heavy, not needed for site) |
| generators/ | Python YANG parsers (dev tools only) |
| scripts/ | Validation/analysis tools (dev tools only) |
| archive/ | Completed TODO/phase tracking docs |
| .github/ | Workflow configs (not site content) |

### First-Time Setup

1. Go to repo **Settings > Pages**
2. Under **Source**, select **GitHub Actions**
3. The workflow will handle the rest on next push

## Access Your Site

**Live URL:** https://ciscodevnet.github.io/cisco-ios-xe-openapi-swagger/

## Statistics (default release 26.2.1)

| Metric | Count |
|--------|-------|
| OpenAPI Specifications | 953 |
| API Paths | 81,560 |
| API Operations | 243,024 |
| YANG Tree Files | 758 (about 4,200 across all releases) |
| Model Types | 8 viewers + notification catalog |
| IOS XE Releases | 6 (17.9.x to 26.2.1) |

## Custom Domain (Optional)

1. Create a CNAME file in root with your domain (e.g., docs.example.com)
2. Configure DNS to point to GitHub Pages
3. Enable HTTPS in Settings > Pages

## Troubleshooting

- **Pages don't load?** Check Settings > Pages shows "GitHub Actions" as source
- **Stale content?** Check Actions tab for failed workflow runs
- **404 errors?** Ensure paths are relative (not starting with /)
- **Large deploy?** The workflow builds Postman/Bruno archives and validates every release before deploying; expect about 12 minutes

Last updated: October 5, 2026
