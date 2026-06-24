#!/bin/bash
# ValuedHR — One-time setup for automatic deployment to GitHub + Hostinger
# Run this once from Terminal, then never touch it again.

REPO_DIR="/Users/michellemendez/Documents/Claude/Projects/ValuedHR Website"
GITHUB_USER="bossladyover50"
GITHUB_REPO="valuedhr-website"
TOKEN=$(cat "$REPO_DIR/.github-token")

echo ""
echo "=== ValuedHR Auto-Deploy Setup ==="
echo ""

# 1. Make deploy.sh executable
chmod +x "$REPO_DIR/deploy.sh"
echo "✓ deploy.sh made executable"

# 2. Configure git remote (with token for passwordless push)
cd "$REPO_DIR" || exit 1
git remote remove origin 2>/dev/null
git remote add origin "https://$GITHUB_USER:$TOKEN@github.com/$GITHUB_USER/$GITHUB_REPO.git"
echo "✓ GitHub remote configured"

# 3. Check if repo has existing content to handle first push
BRANCHES=$(git ls-remote --heads origin 2>/dev/null | wc -l)
if [ "$BRANCHES" -eq 0 ]; then
  echo "  Repo is empty — doing initial push..."
  git push -u origin main
  echo "✓ Initial push complete"
else
  echo "  Repo already has content — pulling first to sync..."
  git fetch origin
  git push -u origin main --force
  echo "✓ Pushed to GitHub"
fi

# 4. Install the Launch Agent (Mac background watcher)
PLIST_DIR="$HOME/Library/LaunchAgents"
PLIST_FILE="$PLIST_DIR/com.valuedhr.deploy.plist"

mkdir -p "$PLIST_DIR"

cat > "$PLIST_FILE" << 'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.valuedhr.deploy</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string>
    <string>/Users/michellemendez/Documents/Claude/Projects/ValuedHR Website/deploy.sh</string>
  </array>
  <key>WatchPaths</key>
  <array>
    <string>/Users/michellemendez/Documents/Claude/Projects/ValuedHR Website/index.html</string>
    <string>/Users/michellemendez/Documents/Claude/Projects/ValuedHR Website/blog.html</string>
  </array>
  <key>StandardOutPath</key>
  <string>/Users/michellemendez/Library/Logs/valuedhr-deploy.log</string>
  <key>StandardErrorPath</key>
  <string>/Users/michellemendez/Library/Logs/valuedhr-deploy.log</string>
  <key>RunAtLoad</key>
  <false/>
</dict>
</plist>
PLIST

# Load the Launch Agent
launchctl unload "$PLIST_FILE" 2>/dev/null
launchctl load "$PLIST_FILE"
echo "✓ Auto-deploy watcher installed and running"

echo ""
echo "=== Setup complete! ==="
echo ""
echo "From now on: whenever Claude updates blog.html or index.html,"
echo "your Mac will automatically push the changes to GitHub,"
echo "and Hostinger will deploy them to your live website."
echo ""
echo "To check deploy logs: cat ~/Library/Logs/valuedhr-deploy.log"
echo ""
