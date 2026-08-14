#!/usr/bin/env bash
# DeepSeek CLI Tools — Linux/macOS installer
# Adds dsh-poster / dsh-drama / dsh-monetize / dsh-studio commands to PATH.
set -euo pipefail

INSTALL_DIR="${DEEPSEEK_TOOLS_DIR:-$HOME/.deepseek-cli-tools}"
BIN_DIR="$INSTALL_DIR/bin"

mkdir -p "$BIN_DIR"

# Copy tools
cp -r "$(dirname "$0")/poster" "$(dirname "$0")/drama" \
      "$(dirname "$0")/book-monetize" "$(dirname "$0")/content-studio" "$INSTALL_DIR/" 2>/dev/null \
  || { echo "Please run install.sh from inside the deepseek-cli-tools repo"; exit 1; }

# Create launchers
cat > "$BIN_DIR/dsh-poster" <<'EOF'
#!/usr/bin/env bash
exec python3 "$HOME/.deepseek-cli-tools/poster/poster.py" "$@"
EOF
cat > "$BIN_DIR/dsh-drama" <<'EOF'
#!/usr/bin/env bash
exec python3 "$HOME/.deepseek-cli-tools/drama/drama.py" "$@"
EOF
cat > "$BIN_DIR/dsh-monetize" <<'EOF'
#!/usr/bin/env bash
exec python3 "$HOME/.deepseek-cli-tools/book-monetize/monetize.py" "$@"
EOF
cat > "$BIN_DIR/dsh-studio" <<'EOF'
#!/usr/bin/env bash
exec python3 "$HOME/.deepseek-cli-tools/content-studio/studio.py" "$@"
EOF

chmod +x "$BIN_DIR"/dsh-*

# Add to PATH in shell profile
PROFILE_FILE=""
if [ -n "${ZSH_VERSION:-}" ] || [ -f "$HOME/.zshrc" ]; then PROFILE_FILE="$HOME/.zshrc";
elif [ -f "$HOME/.bashrc" ]; then PROFILE_FILE="$HOME/.bashrc";
else PROFILE_FILE="$HOME/.profile"; fi

if ! grep -q "deepseek-cli-tools/bin" "$PROFILE_FILE" 2>/dev/null; then
  echo "export PATH=\"\$HOME/.deepseek-cli-tools/bin:\$PATH\"" >> "$PROFILE_FILE"
  echo "✅ Added to $PROFILE_FILE"
fi

echo ""
echo "🎉 Installed! Usage:"
echo "   dsh-poster    'AI course' --layout portrait"
echo "   dsh-drama     'a broke student finds a magic notebook'"
echo "   dsh-monetize  book.txt"
echo "   dsh-studio    'topic' --count 5"
echo ""
echo "👉 Run: source $PROFILE_FILE   (or open a new terminal)"
echo "👉 Set your key: export DEEPSEEK_API_KEY=sk-xxxx"
