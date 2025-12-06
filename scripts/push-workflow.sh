#!/bin/bash
# Automated push workflow script for Devlar AI Workforce

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Devlar AI Workforce - Push Workflow${NC}"

# Verify we're on qc branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$CURRENT_BRANCH" != "qc" ]; then
    echo -e "${RED}❌ Error: Must be on qc branch to run workflow${NC}"
    echo -e "${YELLOW}💡 Switch to qc branch: git checkout qc${NC}"
    exit 1
fi

# Check if there are uncommitted changes
if ! git diff-index --quiet HEAD --; then
    echo -e "${RED}❌ Error: Uncommitted changes detected${NC}"
    echo -e "${YELLOW}💡 Commit changes first: git add . && git commit -m \"...\"${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Ready to execute push workflow${NC}"

# Get the latest commit message for merge
COMMIT_MESSAGE=$(git log -1 --pretty=format:'%s')
echo -e "${BLUE}📝 Latest commit: ${COMMIT_MESSAGE}${NC}"

# Step 1: Switch to main
echo -e "${BLUE}🔄 Step 1: Switching to main branch${NC}"
git checkout main

# Step 2: Merge qc into main
echo -e "${BLUE}🔄 Step 2: Merging qc into main${NC}"
git merge qc -m "$COMMIT_MESSAGE" --no-edit

# Step 3: Push to origin
echo -e "${BLUE}🔄 Step 3: Pushing to GitHub${NC}"
git push origin main

# Step 4: Switch back to qc
echo -e "${BLUE}🔄 Step 4: Switching back to qc branch${NC}"
git checkout qc

echo -e "${GREEN}🎉 Push workflow completed successfully!${NC}"
echo -e "${BLUE}📊 Status:${NC}"
echo -e "${YELLOW}• Changes merged from qc → main${NC}"
echo -e "${YELLOW}• Pushed to GitHub origin/main${NC}"
echo -e "${YELLOW}• Back on qc branch for continued development${NC}"