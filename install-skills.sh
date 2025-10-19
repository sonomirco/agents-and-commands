#!/bin/bash
# Installation script for Claude Code Skills
# This script copies skills from this repository to ~/.claude/skills/

set -e

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_DIR="$HOME/.claude/skills"
SKILLS_MANIFEST="$REPO_DIR/skills-registry.json"

echo "📦 Installing Claude Code Skills from agents-and-commands repository"
echo ""

# Ensure manifest exists
if [ ! -f "$SKILLS_MANIFEST" ]; then
    echo "❌ Skill manifest not found at $SKILLS_MANIFEST"
    exit 1
fi

# Create skills directory if it doesn't exist
if [ ! -d "$SKILLS_DIR" ]; then
    echo "Creating $SKILLS_DIR..."
    mkdir -p "$SKILLS_DIR"
fi

# Function to install a single skill
install_skill() {
    local skill_name="$1"
    local relative_path
    relative_path="$(jq -r --arg name "$skill_name" '.skills[] | select(.name == $name) | .path // empty' "$SKILLS_MANIFEST")"

    if [ -z "$relative_path" ]; then
        echo "❌ Skill not found in manifest: $skill_name"
        return 1
    fi

    local source_path="$REPO_DIR/$relative_path"
    local dest_path="$SKILLS_DIR/$skill_name"

    if [ ! -d "$source_path" ]; then
        echo "❌ Skill not found: $skill_name"
        return 1
    fi

    if [ -d "$dest_path" ]; then
        echo "⚠️  $skill_name already exists. Overwrite? (y/n)"
        read -r response
        if [[ ! "$response" =~ ^[Yy]$ ]]; then
            echo "⏭️  Skipped: $skill_name"
            return 0
        fi
        rm -rf "$dest_path"
    fi

    echo "✅ Installing: $skill_name"
    cp -r "$source_path" "$dest_path"
}

# Install all skills or specific ones
if [ $# -eq 0 ]; then
    echo "Installing all skills..."
    echo ""
    while IFS= read -r skill_name; do
        install_skill "$skill_name"
    done < <(jq -r '.skills[].name' "$SKILLS_MANIFEST")
else
    echo "Installing specified skills..."
    echo ""
    for skill_name in "$@"; do
        install_skill "$skill_name"
    done
fi

echo ""
echo "✨ Installation complete!"
echo ""
echo "Installed skills are now available in Claude Code."
echo "You can invoke them by name or via the Skill tool."
echo ""
echo "Example usage:"
echo "  - 'Use grasshopper-analyzer to analyze this file'"
echo "  - 'Run dynamo-analyzer on this graph'"
echo "  - 'Convert this article with markdown-to-xml'"
