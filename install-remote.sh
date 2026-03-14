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

# Add void-fortress alias to shell config
ALIAS_LINE="alias void-fortress='cd $INSTALL_DIR && python3 gui.py'"

add_alias() {
    local rc="$1"
    if [ -f "$rc" ] && grep -q "void-fortress" "$rc" 2>/dev/null; then
        return  # already there
    fi
    if [ -f "$rc" ]; then
        echo "" >> "$rc"
        echo "# Void Fortress" >> "$rc"
        echo "$ALIAS_LINE" >> "$rc"
        echo -e "  ${GREEN}✓${NC} Added alias to $rc"
    fi
}

add_alias "$HOME/.zshrc"
add_alias "$HOME/.bashrc"

echo ""
echo -e "  ${GREEN}Run ${CYAN}void-fortress${GREEN} to launch (restart your shell or run ${CYAN}source ~/.zshrc${GREEN})${NC}"
echo -e "  ${GREEN}Run ${CYAN}void-fortress --demo${GREEN} to try without Claude Code${NC}"
echo ""
