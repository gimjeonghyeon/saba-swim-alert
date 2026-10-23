#!/bin/bash
# 맥에서 5분마다 check.py를 실행하도록 launchd에 등록한다.
# 사용법: bash install-mac.sh "<디스코드 웹훅 URL>"
set -e

WEBHOOK="$1"
DIR="$HOME/saba-swim-alert"
PLIST="$HOME/Library/LaunchAgents/com.saba.swimalert.plist"

[ -d "$DIR" ] || git clone https://github.com/gimjeonghyeon/saba-swim-alert.git "$DIR"
cd "$DIR"
git pull -q || true
[ -n "$WEBHOOK" ] && echo "$WEBHOOK" > webhook.txt

PY="$(command -v python3)"
mkdir -p "$HOME/Library/LaunchAgents"
cat > "$PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>com.saba.swimalert</string>
  <key>ProgramArguments</key>
  <array><string>$PY</string><string>$DIR/check.py</string></array>
  <key>StartInterval</key><integer>300</integer>
  <key>RunAtLoad</key><true/>
  <key>StandardOutPath</key><string>$DIR/run.log</string>
  <key>StandardErrorPath</key><string>$DIR/run.log</string>
</dict>
</plist>
EOF

launchctl unload "$PLIST" 2>/dev/null || true
launchctl load "$PLIST"

"$PY" check.py
"$PY" -c "import check; check.notify('✅ 맥북에서 수영 자리 알림 시작! 5분마다 확인할게요.')"
echo "설치 완료. 로그: $DIR/run.log"
