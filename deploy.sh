#!/bin/bash
# ValuedHR Website — Auto-deploy to GitHub
# This script commits any changes and pushes to GitHub.
# Hostinger then picks up the update automatically.

REPO_DIR="/Users/michellemendez/Documents/Claude/Projects/ValuedHR Website"
GITHUB_USER="bossladyover50"
GITHUB_REPO="valuedhr-website"
TOKEN_FILE="$REPO_DIR/.github-token"

# Load token
if [ ! -f "$TOKEN_FILE" ]; then
  echo "ERROR: Token file not found at $TOKEN_FILE"
  exit 1
fi
TOKEN=$(cat "$TOKEN_FILE")

cd "$REPO_DIR" || exit 1

# Only run if there are actual changes
if git diff --quiet && git diff --cached --quiet; then
  echo "No changes to deploy."
  exit 0
fi

# Stage, commit, and push
git add index.html blog.html valuedhr-website.html proposal.html
git commit -m "Site update — $(date '+%B %d, %Y')"
git push https://$GITHUB_USER:$TOKEN@github.com/$GITHUB_USER/$GITHUB_REPO.git main

echo "✓ Deployed to GitHub successfully."
