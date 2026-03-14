#!/bin/bash
# Void Fortress - remote installer
# Usage: curl -fsSL https://raw.githubusercontent.com/klietzau280/void-fortress/main/install-remote.sh | bash

set -e

INSTALL_DIR="$HOME/.void-fortress"
REPO_URL="https://github.com/klietzau280/void-fortress.git"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

echo ""
echo -e "${CYAN}  ╔══════════════════════════════════════╗${NC}"
echo -e "${CYAN}  ║        V O I D   F O R T R E S S     ║${NC}"
echo -e "${CYAN}  ║         Remote Installation           ║${NC}"
echo -e "${CYAN}  ╚══════════════════════════════════════╝${NC}"
echo ""

# Check dependencies
if ! command -v git &>/dev/null; then
    echo -e "${RED}ERROR: git not found. Install git first.${NC}"
    exit 1
fi

if ! command -v python3 &>/dev/null; then
    echo -e "${RED}ERROR: python3 not found. Install Python 3.9+${NC}"
    exit 1
fi

# Clone or update
if [ -d "$INSTALL_DIR" ]; then
    echo -e "${YELLOW}Updating existing installation...${NC}"
    cd "$INSTALL_DIR"
    git pull --ff-only origin main 2>/dev/null || {
        echo -e "${YELLOW}Pull failed, re-cloning...${NC}"
        cd ..
        rm -rf "$INSTALL_DIR"
        git clone "$REPO_URL" "$INSTALL_DIR"
        cd "$INSTALL_DIR"
    }
else
    echo -e "${YELLOW}Cloning Void Fortress...${NC}"
    git clone "$REPO_URL" "$INSTALL_DIR"
    cd "$INSTALL_DIR"
fi

echo ""

# Run the local installer
chmod +x install.sh
./install.sh

# Add convenience alias hint
echo ""
echo -e "  ${YELLOW}Pro tip:${NC} Add an alias to your shell config:"
echo -e "    ${CYAN}alias void-fortress='cd $INSTALL_DIR && python3 gui.py'${NC}"
echo ""
