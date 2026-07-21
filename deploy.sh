#!/bin/bash
# ValuedHR Website — Auto-deploy to GitHub
# This script commits any changes and pushes to GitHub.
# Hostinger then picks up the update automatically.

REPO_DIR="/Users/michellemendez/Documents/Claude/Projects/ValuedHR Website"
GITHUB_USER="bossladyover50"
GITHUB_REPO="valuedhr-website"
cd "$REPO_DIR" || exit 1

# Only run if there are actual changes
if git diff --quiet && git diff --cached --quiet; then
  echo "No changes to deploy."
  exit 0
fi

# Stage, commit, and push
git add index.html blog.html use-cases.html articles/ assets/ services/ robots.txt sitemap.xml .htaccess 404.html privacy.html terms.html
git commit -m "Site update — $(date '+%B %d, %Y')"
git push origin main

echo "✓ Deployed to GitHub successfully."
