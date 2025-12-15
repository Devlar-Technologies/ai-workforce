#!/bin/bash

# Setup script for AI Workforce git hooks
# This script configures git hooks to enforce development standards

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}🔧 Setting up AI Workforce git hooks...${NC}"

# Check if we're in the right directory
if [ ! -f "README.md" ] || [ ! -d ".githooks" ]; then
    echo -e "${YELLOW}⚠️  Please run this script from the ai-workforce root directory${NC}"
    exit 1
fi

# Configure git to use our custom hooks directory
echo -e "${BLUE}📁 Configuring git hooks path...${NC}"
git config core.hooksPath .githooks

# Make hooks executable
echo -e "${BLUE}🔐 Setting executable permissions...${NC}"
chmod +x .githooks/pre-commit

# Verify setup
if [ -x ".githooks/pre-commit" ]; then
    echo -e "${GREEN}✅ Git hooks configured successfully!${NC}"
    echo ""
    echo -e "${BLUE}🛡️  Active protections:${NC}"
    echo "  • No emojis in public-facing documentation"
    echo "  • Documentation updates required with code changes"
    echo "  • Secret detection"
    echo "  • Python/YAML syntax validation"
    echo "  • Conventional commit message format"
    echo ""
    echo -e "${YELLOW}📝 Note: Hooks only apply to commits made after this setup${NC}"
    echo -e "${YELLOW}🔍 Test the hook: Try committing a file with emojis${NC}"
else
    echo -e "${RED}❌ Failed to set up git hooks${NC}"
    exit 1
fi

echo -e "${GREEN}🎉 Setup complete!${NC}"