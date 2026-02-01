# GitHub Pages Deployment

## How to Deploy

1. **Push to GitHub Repository**
   ```bash
   git add .
   git commit -m "Prepare for GitHub Pages deployment"
   git push origin main
   ```

2. **Enable GitHub Pages**
   - Go to your repository on GitHub
   - Navigate to Settings → Pages
   - Under "Source", select "Deploy from a branch"
   - Select `main` branch and `/ (root)` folder
   - Click Save

3. **Access Your Site**
   - Your site will be available at: `https://<username>.github.io/<repository-name>/`
   - It may take a few minutes for the first deployment

## What's Included

- **index.html** - Main landing page
- **all-models.html** - Overview of all model types  
- **swagger-*/index.html** - Individual model type pages
- **swagger-*/all-*.html** - Combined views per model type
- **swagger-*/api/*.json** - OpenAPI 3.0 specifications
- **swagger-ui-5.11.0/** - Swagger UI framework
- **.nojekyll** - Disables Jekyll for faster builds
- **404.html** - Custom error page

## Custom Domain (Optional)

To use a custom domain:
1. Create a file named `CNAME` in the root directory
2. Add your domain name (e.g., `docs.example.com`)
3. Configure DNS to point to GitHub Pages

## Troubleshooting

- If pages don't load, check that paths are relative (not starting with `/`)
- If Swagger UI doesn't load, ensure `swagger-ui-5.11.0/dist/` exists
- Check browser console for 404 errors on resources

## Statistics

- OpenAPI Specifications: 597+
- API Paths: 15,000+
- Model Types: 9
- IOS-XE Version: 17.18.1

Last prepared: February 2026
