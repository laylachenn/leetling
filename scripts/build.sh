#!/usr/bin/env bash
# Builds Leetling.app (with its widget extension) using only the Command Line Tools,
# ad-hoc signs it, and installs it to ~/Applications.
#
#   scripts/build.sh            build + install + launch
#   scripts/build.sh --no-open  build + install only
#   scripts/build.sh --content  also regenerate Resources/problems.json first
set -euo pipefail
cd "$(dirname "$0")/.."
ROOT="$PWD"
BUILD="$ROOT/.build/app"
APP="$BUILD/Leetling.app"
DEST="$HOME/Applications/Leetling.app"
OPEN=1
for arg in "$@"; do
  case "$arg" in
    --no-open) OPEN=0 ;;
    --content) python3 content/build_problems.py ;;
  esac
done

[ -f Resources/problems.json ] || python3 content/build_problems.py

echo "🌸 Compiling…"
swift build -c release --product Leetling
swift build -c release --product LeetlingWidget
BIN="$(swift build -c release --show-bin-path)"
BUILD_NUMBER="$(date +%Y%m%d%H%M)"

echo "🎀 Assembling bundle…"
rm -rf "$APP"
mkdir -p "$APP/Contents/MacOS" "$APP/Contents/Resources" "$APP/Contents/PlugIns/LeetlingWidget.appex/Contents/MacOS"
cp "$BIN/Leetling" "$APP/Contents/MacOS/Leetling"
sed "s/BUILD_NUMBER/$BUILD_NUMBER/" Support/App-Info.plist > "$APP/Contents/Info.plist"
cp Resources/problems.json Resources/runner.py Resources/AppIcon.icns "$APP/Contents/Resources/"

WX="$APP/Contents/PlugIns/LeetlingWidget.appex"
cp "$BIN/LeetlingWidget" "$WX/Contents/MacOS/LeetlingWidget"
sed "s/BUILD_NUMBER/$BUILD_NUMBER/" Support/Widget-Info.plist > "$WX/Contents/Info.plist"

echo "✍️  Signing (ad-hoc)…"
codesign --force --sign - --entitlements Support/Widget.entitlements "$WX"
codesign --force --sign - "$APP"
codesign --verify --deep --strict "$APP"

echo "🏡 Installing to ${DEST}…"
pkill -x Leetling 2>/dev/null || true
mkdir -p "$HOME/Applications"
rm -rf "$DEST"
cp -R "$APP" "$DEST"
LSREGISTER=/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister
"$LSREGISTER" -f "$DEST" >/dev/null 2>&1 || true
pluginkit -a "$DEST/Contents/PlugIns/LeetlingWidget.appex" >/dev/null 2>&1 || true

echo "✨ Done! Leetling is installed at ${DEST}"
if [ "$OPEN" = 1 ]; then open "$DEST"; fi
