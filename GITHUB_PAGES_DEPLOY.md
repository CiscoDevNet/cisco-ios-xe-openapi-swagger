# GitHub Pages Deployment

## How It Works

This site is deployed automatically using **GitHub Actions**. Every push to main triggers the workflow at .github/workflows/deploy-pages.yml.

### Deployment Flow

1. **Push to main branch** - triggers GitHub Actions
2. **Workflow prepares deploy directory** - copies only website-relevant files
3. **Uploads artifact** - uses ctions/upload-pages-artifact
4. **Deploys to Pages** - uses ctions/deploy-pages

No manual setup required. Just push and it deploys.

### What Gets Deployed

| Included | Description |
|----------|-------------|
| swagger-*-model/ | All 9 model directories (HTML + JSON specs) |
| yang-trees/ | 768 YANG/MIB tree visualizations |
| docs/ | Getting Started guide, Project Summary |
| 	ools/ | Postman collection and environment |
| *.html | Landing page, 404, code generator, tree compare, accountability |
| *.js | Search engine, recent favorites |
| *.json | Search index, YANG accountability data |
| README.md | Repository documentation |
| .nojekyll | Disables Jekyll processing |

| Excluded | Reason |
|----------|--------|
| 
eferences/ | 848 YANG source modules (heavy, not needed for site) |
| generators/ | Python YANG parsers (dev tools only) |
| scripts/ | Validation/analysis tools (dev tools only) |
| rchive/ | Completed TODO/phase tracking docs |
| .github/ | Workflow configs (not site content) |

### First-Time Setup

1. Go to repo **Settings > Pages**
2. Under **Source**, select **GitHub Actions**
3. The workflow will handle the rest on next push

## Access Your Site

**Live URL:** https://ciscodevnet.github.io/cisco-ios-xe-openapi-swagger/

## Statistics

| Metric | Count |
|--------|-------|
| OpenAPI Specifications | 747 |
| API Paths | 34,694 |
| API Operations | 58,001 |
| YANG Tree Files | 768 |
| Model Types | 9 |
| IOS XE Version | 17.18.1 |

## Custom Domain (Optional)

1. Create a CNAME file in root with your domain (e.g., docs.example.com)
2. Configure DNS to point to GitHub Pages
3. Enable HTTPS in Settings > Pages

## Troubleshooting

- **Pages don't load?** Check Settings > Pages shows "GitHub Actions" as source
- **Stale content?** Check Actions tab for failed workflow runs
- **404 errors?** Ensure paths are relative (not starting with /)
- **Large deploy?** Workflow has 15-minute timeout; should complete in about 2 minutes

Last updated: March 27, 2026
