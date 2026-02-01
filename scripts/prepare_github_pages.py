#!/usr/bin/env python3
"""
GitHub Pages Preparation Script
Prepares the project for GitHub Pages deployment by:
1. Fixing absolute paths to relative paths
2. Removing localhost/port references
3. Creating necessary config files
4. Validating all links
"""

import os
import re
from pathlib import Path
from typing import List, Tuple

class GitHubPagesPreparer:
    """Prepare project for GitHub Pages deployment"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.fixes_made = []
        self.warnings = []
    
    def fix_absolute_paths(self):
        """Fix absolute paths in HTML files to be relative"""
        print("\n" + "="*60)
        print("Fixing Absolute Paths")
        print("="*60)
        
        # Patterns to fix
        patterns = [
            # Fix href="/swagger-xxx" to href="swagger-xxx"
            (r'href="/swagger-', 'href="swagger-'),
            # Fix href="/swagger-ui-xxx" patterns at root level
            (r'href="/swagger-ui-', 'href="swagger-ui-'),
            # Fix src="/swagger" patterns
            (r'src="/swagger-', 'src="swagger-'),
        ]
        
        html_files = list(self.project_root.glob('*.html'))
        
        for html_file in html_files:
            content = html_file.read_text(encoding='utf-8')
            original_content = content
            
            for pattern, replacement in patterns:
                content = re.sub(pattern, replacement, content)
            
            if content != original_content:
                html_file.write_text(content, encoding='utf-8')
                self.fixes_made.append(f"Fixed absolute paths in {html_file.name}")
                print(f"  ✓ Fixed: {html_file.name}")
    
    def fix_port_references(self):
        """Remove port 3004 references"""
        print("\n" + "="*60)
        print("Removing Port References")
        print("="*60)
        
        # Update index.html footer
        index_file = self.project_root / 'index.html'
        if index_file.exists():
            content = index_file.read_text(encoding='utf-8')
            
            # Remove "| Port 3004 |" from footer
            content = content.replace('| Port 3004 |', '|')
            content = content.replace('Port 3004 |', '')
            content = content.replace('| Port 3004', '')
            
            index_file.write_text(content, encoding='utf-8')
            self.fixes_made.append("Removed port references from index.html")
            print("  ✓ Removed port references from index.html")
    
    def update_stats(self):
        """Update statistics in index.html with accurate numbers"""
        print("\n" + "="*60)
        print("Updating Statistics")
        print("="*60)
        
        # Count actual specs
        spec_count = 0
        path_count = 0
        
        swagger_dirs = [
            'swagger-oper-model/api',
            'swagger-rpc-model/api', 
            'swagger-cfg-model/api',
            'swagger-openconfig-model/api',
            'swagger-native-config-model/api',
            'swagger-ietf-model/api',
            'swagger-events-model/api',
            'swagger-mib-model/api',
            'swagger-other-model/api'
        ]
        
        import json
        
        for swagger_dir in swagger_dirs:
            api_path = self.project_root / swagger_dir
            if api_path.exists():
                for json_file in api_path.glob('*.json'):
                    if json_file.name not in ['manifest.json', 'all-operations.json', 
                                               'all-configs.json', 'all-native.json',
                                               'all-ietf.json', 'all-events.json',
                                               'all-openconfig.json', 'all-rpc.json',
                                               'all-mibs.json', 'all-other.json']:
                        spec_count += 1
                        try:
                            with open(json_file, 'r', encoding='utf-8') as f:
                                spec = json.load(f)
                                path_count += len(spec.get('paths', {}))
                        except:
                            pass
        
        print(f"  Total specs: {spec_count}")
        print(f"  Total paths: {path_count}")
        
        # Update index.html with actual counts
        index_file = self.project_root / 'index.html'
        if index_file.exists():
            content = index_file.read_text(encoding='utf-8')
            
            # Update OpenAPI Specs count (find and replace the stat-number)
            content = re.sub(
                r'(<span class="stat-number">)\d+(<\/span>\s*<span class="stat-label">OpenAPI Specs)',
                rf'\g<1>{spec_count}\2',
                content
            )
            
            # Update API Paths count
            content = re.sub(
                r'(<span class="stat-number">)[\d,]+(<\/span>\s*<span class="stat-label">API Paths)',
                rf'\g<1>{path_count:,}\2',
                content
            )
            
            index_file.write_text(content, encoding='utf-8')
            self.fixes_made.append(f"Updated stats: {spec_count} specs, {path_count} paths")
            print(f"  ✓ Updated index.html stats")
    
    def create_github_pages_config(self):
        """Create Jekyll config and .nojekyll for GitHub Pages"""
        print("\n" + "="*60)
        print("Creating GitHub Pages Configuration")
        print("="*60)
        
        # Create .nojekyll to disable Jekyll processing (faster builds, supports directories starting with _)
        nojekyll_file = self.project_root / '.nojekyll'
        nojekyll_file.touch()
        self.fixes_made.append("Created .nojekyll file")
        print("  ✓ Created .nojekyll (disables Jekyll for faster builds)")
        
        # Create CNAME file placeholder (user should update with their domain)
        # cname_file = self.project_root / 'CNAME'
        # cname_file.write_text('your-custom-domain.com')
        # print("  ✓ Created CNAME placeholder")
        
        # Create a simple 404.html
        error_404 = self.project_root / '404.html'
        error_404_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>404 - Page Not Found</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0;
        }
        .container {
            background: white;
            padding: 40px 60px;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }
        h1 { color: #1e88e5; font-size: 48px; margin-bottom: 10px; }
        p { color: #666; font-size: 18px; margin-bottom: 20px; }
        a {
            display: inline-block;
            padding: 12px 24px;
            background: linear-gradient(135deg, #1e88e5 0%, #1565c0 100%);
            color: white;
            text-decoration: none;
            border-radius: 6px;
            font-weight: 500;
        }
        a:hover { background: linear-gradient(135deg, #1565c0 0%, #0d47a1 100%); }
    </style>
</head>
<body>
    <div class="container">
        <h1>404</h1>
        <p>Page not found. The documentation you're looking for doesn't exist.</p>
        <a href="index.html">← Back to Documentation Hub</a>
    </div>
</body>
</html>
'''
        error_404.write_text(error_404_content, encoding='utf-8')
        self.fixes_made.append("Created 404.html error page")
        print("  ✓ Created 404.html")
    
    def validate_links(self):
        """Validate internal links in HTML files"""
        print("\n" + "="*60)
        print("Validating Internal Links")
        print("="*60)
        
        broken_links = []
        checked = 0
        
        # Check links in index.html
        index_file = self.project_root / 'index.html'
        if index_file.exists():
            content = index_file.read_text(encoding='utf-8')
            
            # Find all href links
            hrefs = re.findall(r'href="([^"#]+)"', content)
            
            for href in hrefs:
                if href.startswith('http') or href.startswith('mailto:') or href.startswith('#'):
                    continue
                    
                # Resolve relative path
                target_path = self.project_root / href
                
                if not target_path.exists():
                    broken_links.append(f"index.html -> {href}")
                checked += 1
        
        print(f"  Checked {checked} internal links")
        
        if broken_links:
            print(f"  ⚠️  Found {len(broken_links)} potentially broken links:")
            for link in broken_links[:10]:
                print(f"      - {link}")
                self.warnings.append(f"Broken link: {link}")
            if len(broken_links) > 10:
                print(f"      ... and {len(broken_links) - 10} more")
        else:
            print("  ✓ All links validated successfully")
    
    def create_readme_for_pages(self):
        """Create a deployment README"""
        print("\n" + "="*60)
        print("Creating Deployment Documentation")
        print("="*60)
        
        deploy_readme = '''# GitHub Pages Deployment

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
'''
        
        deploy_file = self.project_root / 'GITHUB_PAGES_DEPLOY.md'
        deploy_file.write_text(deploy_readme, encoding='utf-8')
        self.fixes_made.append("Created GITHUB_PAGES_DEPLOY.md")
        print("  ✓ Created GITHUB_PAGES_DEPLOY.md")
    
    def run(self):
        """Run all preparation steps"""
        print("\n" + "="*60)
        print("GitHub Pages Preparation Tool")
        print("="*60)
        print(f"Project: {self.project_root}")
        
        self.fix_absolute_paths()
        self.fix_port_references()
        self.update_stats()
        self.create_github_pages_config()
        self.validate_links()
        self.create_readme_for_pages()
        
        # Summary
        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        print(f"\n✅ Fixes Made: {len(self.fixes_made)}")
        for fix in self.fixes_made:
            print(f"   - {fix}")
        
        if self.warnings:
            print(f"\n⚠️  Warnings: {len(self.warnings)}")
            for warn in self.warnings:
                print(f"   - {warn}")
        
        print("\n" + "="*60)
        print("NEXT STEPS")
        print("="*60)
        print("""
1. Review changes and commit to git:
   git add .
   git commit -m "Prepare for GitHub Pages deployment"
   git push origin main

2. Enable GitHub Pages in repository settings:
   Settings → Pages → Deploy from branch → main → / (root)

3. Your site will be available at:
   https://<username>.github.io/<repository>/
""")


def main():
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    preparer = GitHubPagesPreparer(str(project_root))
    preparer.run()


if __name__ == '__main__':
    main()
