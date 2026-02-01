#!/bin/bash
set -e

# Get the directory of the script
script_dir=$(dirname "$0")
cd "$script_dir"

# Load environment variables from .env if it exists
if [ -f ".env" ]; then
    echo "Loading environment variables from .env"
    export $(grep -v '^#' .env | xargs)
fi

# Configuration - update with your repo details
REPO_URL="github.com/ch2ohch2oh/leetcodepulse.git"

echo "========================================"
echo "Pulling latest changes from remote..."
echo "========================================"
git pull origin main

echo ""
echo "========================================"
echo "Running site update..."
echo "========================================"
./update_site.sh

echo ""
echo "========================================"
echo "Committing and pushing changes..."
echo "========================================"

# Add data files and generated html
git add data/ 

# Prepare git commit with optional bot identity
GIT_COMMIT_CMD="git"
if [ -n "$GIT_USER_NAME" ]; then
    GIT_COMMIT_CMD="$GIT_COMMIT_CMD -c user.name=\"$GIT_USER_NAME\""
fi
if [ -n "$GIT_USER_EMAIL" ]; then
    GIT_COMMIT_CMD="$GIT_COMMIT_CMD -c user.email=\"$GIT_USER_EMAIL\""
fi

$GIT_COMMIT_CMD commit -m "Auto-update: $(date '+%Y-%m-%d %H:%M:%S')"

# Use GITHUB_TOKEN if available
TOKEN="${GITHUB_TOKEN}"

if [ -n "$TOKEN" ]; then
    echo "Pushing to remote using token..."
    # Hide token from output if it was printed, but here we just use it in the URL
    git push "https://${TOKEN}@${REPO_URL}" main
else
    echo "Warning: github_token not set. Attempting default push..."
    git push origin main
fi


echo ""
echo "Automation complete!"
