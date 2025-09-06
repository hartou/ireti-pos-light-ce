# 📄 GitHub Pages Setup for Ireti POS Light CE

This guide explains how to set up GitHub Pages to publish the project roadmap and documentation for public access.

## 🎯 Overview

GitHub Pages will provide a public-facing documentation site that includes:
- **Project Roadmap**: Development timeline and feature planning
- **API Documentation**: Technical specifications and integration guides  
- **User Guides**: Setup instructions and troubleshooting
- **Release Notes**: Version history and upgrade information

## 🚀 Quick Setup (Repository Owner)

### Option 1: Automatic GitHub Pages Setup

1. **Navigate to Repository Settings**
   - Go to: https://github.com/hartou/ireti-pos-light-ce/settings/pages

2. **Configure Source**
   - Source: `Deploy from a branch`
   - Branch: `main`
   - Folder: `/ (root)` or `/docs` (recommended)

3. **Save Configuration**
   - GitHub will automatically build and deploy
   - Site will be available at: https://hartou.github.io/ireti-pos-light-ce/

### Option 2: Custom GitHub Actions Workflow

Create `.github/workflows/pages.yml`:

```yaml
name: Deploy Documentation to GitHub Pages

on:
  push:
    branches: [ main ]
    paths:
      - 'docs/**'
      - 'README.md'
      - '.github/workflows/pages.yml'
  
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: "pages"
  cancel-in-progress: false

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        
      - name: Setup Pages
        uses: actions/configure-pages@v4
        
      - name: Build Documentation
        run: |
          mkdir -p _site/docs
          cp -r docs/* _site/docs/
          cp README.md _site/index.md
          
          # Create navigation index
          cat > _site/index.html << 'EOF'
          <!DOCTYPE html>
          <html>
          <head>
            <title>Ireti POS Light CE - Documentation</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
              body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 2rem; }
              .container { max-width: 800px; margin: 0 auto; }
              .nav-link { display: block; padding: 0.5rem 0; text-decoration: none; }
              .nav-link:hover { text-decoration: underline; }
            </style>
          </head>
          <body>
            <div class="container">
              <h1>🛒 Ireti POS Light CE - Documentation</h1>
              <p>Welcome to the documentation site for Ireti POS Light Community Edition.</p>
              
              <h2>📚 Documentation</h2>
              <a href="docs/ROADMAP.html" class="nav-link">🗺️ Development Roadmap</a>
              <a href="docs/SYSTEM_INSTRUCTIONS.html" class="nav-link">⚙️ System Instructions</a>
              <a href="docs/COPILOT_WORKFLOW.html" class="nav-link">🤖 Copilot Workflow</a>
              
              <h2>📖 Guides</h2>
              <a href="DEPLOYMENT.html" class="nav-link">🚀 Deployment Guide</a>
              <a href="CONTRIBUTING-CE.html" class="nav-link">🤝 Contributing Guide</a>
              
              <h2>🔗 Links</h2>
              <a href="https://github.com/hartou/ireti-pos-light-ce" class="nav-link">📦 GitHub Repository</a>
              <a href="https://github.com/hartou/ireti-pos-light-ce/releases" class="nav-link">📋 Releases</a>
              <a href="https://github.com/hartou/ireti-pos-light-ce/issues" class="nav-link">🐛 Issues</a>
            </div>
          </body>
          </html>
          EOF
          
      - name: Upload Artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: '_site'
          
  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    needs: build
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

## 📝 Documentation Structure

Recommended structure for GitHub Pages:

```
docs/
├── index.md                    # Landing page
├── ROADMAP.md                  # Development roadmap (main content)
├── ROADMAP_USER_STORIES.md     # Structured roadmap items
├── SYSTEM_INSTRUCTIONS.md      # Development guidelines
├── COPILOT_WORKFLOW.md         # AI assistant workflows
├── API/                        # API documentation
│   ├── README.md
│   └── endpoints.md
├── guides/                     # User guides
│   ├── deployment.md
│   ├── configuration.md
│   └── troubleshooting.md
└── _config.yml                 # Jekyll configuration
```

## 🎨 Jekyll Theme Configuration

Create `docs/_config.yml` for better styling:

```yaml
# Site settings
title: "Ireti POS Light CE"
description: "Open-source Point of Sale system with Stripe integration"
url: "https://hartou.github.io"
baseurl: "/ireti-pos-light-ce"

# Theme
theme: minima
# Alternative themes: jekyll-theme-minimal, jekyll-theme-cayman

# Markdown processor
markdown: kramdown
highlighter: rouge

# Plugins
plugins:
  - jekyll-feed
  - jekyll-sitemap
  - jekyll-seo-tag

# Navigation
header_pages:
  - docs/ROADMAP.md
  - docs/SYSTEM_INSTRUCTIONS.md
  - DEPLOYMENT.md
  - CONTRIBUTING-CE.md

# Collections
collections:
  guides:
    output: true
    permalink: /:collection/:name/

# Defaults
defaults:
  - scope:
      path: ""
      type: "pages"
    values:
      layout: "page"
  - scope:
      path: "docs"
      type: "pages"
    values:
      layout: "page"
      nav_order: 1
```

## 🔧 Advanced Features

### Custom Domain Setup

1. **Add CNAME file** to repository root:
   ```
   docs.iretipos.com
   ```

2. **Configure DNS** at your domain provider:
   - Type: CNAME
   - Name: docs (or subdomain)
   - Value: hartou.github.io

3. **Enable HTTPS** in repository settings

### Search Functionality

Add to `docs/_includes/search.html`:

```html
<script src="https://cdn.jsdelivr.net/npm/lunr@2.3.9/lunr.min.js"></script>
<script>
  // Simple search implementation
  const documents = [
    {% for page in site.pages %}
      {
        "title": "{{ page.title | escape }}",
        "content": "{{ page.content | strip_html | escape }}",
        "url": "{{ page.url | relative_url }}"
      }{% unless forloop.last %},{% endunless %}
    {% endfor %}
  ];
  
  const idx = lunr(function () {
    this.field('title');
    this.field('content');
    this.ref('url');
    
    documents.forEach(function (doc) {
      this.add(doc);
    }, this);
  });
  
  function search(query) {
    return idx.search(query);
  }
</script>
```

## 📊 Analytics and Monitoring

### Google Analytics (Optional)

Add to `docs/_config.yml`:

```yaml
google_analytics: G-XXXXXXXXXX
```

### GitHub Pages Insights

Monitor usage at:
- Repository → Insights → Traffic
- Track page views and referrers
- Monitor documentation usage patterns

## 🚀 Deployment Workflow

### Automated Updates

The roadmap and documentation will automatically update when:

1. **Push to main branch** with changes in `docs/` folder
2. **Manual workflow dispatch** for immediate updates
3. **Release creation** triggers documentation rebuild

### Manual Deployment

```bash
# Local preview (requires Jekyll)
gem install bundler jekyll
cd docs
bundle exec jekyll serve

# View at: http://localhost:4000
```

## 📋 Checklist for Setup

- [ ] Repository owner enables GitHub Pages in settings
- [ ] Configure source branch and folder
- [ ] Test initial deployment
- [ ] Verify roadmap.md displays correctly
- [ ] Configure custom domain (if desired)
- [ ] Enable HTTPS
- [ ] Test navigation and links
- [ ] Set up automated workflow (optional)
- [ ] Configure analytics (optional)

## 🔗 Useful Links

- [GitHub Pages Documentation](https://docs.github.com/en/pages)
- [Jekyll Documentation](https://jekyllrb.com/docs/)
- [Markdown Guide](https://www.markdownguide.org/)
- [GitHub Pages Themes](https://pages.github.com/themes/)

---

*Once GitHub Pages is configured, the roadmap will be publicly accessible and automatically updated with each documentation change.*