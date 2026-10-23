"""부산광역시생활체육문화센터 인터넷 접수 페이지에서 취소 자리를 감시해 디스코드로 알린다."""
import html
import json
import os
import re
import sys
import urllib.request
from datetime import datetime, timedelta, timezone

PAGE_URL = "https://www.saba.or.kr/sub/progapp.php?pn=0506"
TARGETS = [t.strip() for t in os.environ.get("TARGETS", "몸짱수영 C(상급)").split(",") if t.strip()]
WEBHOOK = os.environ.get("DISCORD_WEBHOOK_URL", "")
STATE_FILE = "state.json"
HISTORY_FILE = "history.log"
KST = timezone(timedelta(hours=9))


def fetch_page():
    req = urllib.request.Request(PAGE_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as res:
        return res.read().decode("utf-8", errors="replace")


def parse_programs(page):
    """프로그램명 -> (상태, 요일, 시간) 딕셔너리."""
    programs = {}
    for block in page.split('<ul class="prog_request_cont">')[1:]:
        block = block.split("</ul>")[0]
        cells = re.findall(r"<li>(.*?)</li>", block, re.S)
        if len(cells) < 3:
            continue
        name = html.unescape(re.sub(r"<[^>]+>", "", cells[0])).strip()
        if "btn_reg" in block:
            status = "등록가능"
        elif "btn_end" in block:
            status = "마감"
        else:
            status = "알수없음"
        programs[name] = (status, cells[1].strip(), cells[2].strip())
    return programs


def notify(message):
    if not WEBHOOK:
        print("[webhook 없음]", message)
        return
    body = json.dumps({"content": message}).encode("utf-8")
    req = urllib.request.Request(
        WEBHOOK, data=body, headers={"Content-Type": "application/json", "User-Agent": "saba-swim-alert"}
    )
    urllib.request.urlopen(req, timeout=30)


def main():
    try:
        programs = parse_programs(fetch_page())
    except Exception as e:  # 사이트 일시 장애로 매번 실패 메일이 오지 않도록 조용히 종료
        print(f"페이지 조회 실패: {e}")
        return 0

    try:
        with open(STATE_FILE, encoding="utf-8") as f:
            state = json.load(f)
    except FileNotFoundError:
        state = {}

    now = datetime.now(KST).strftime("%Y-%m-%d %H:%M")
    changed = False
    for target in TARGETS:
        if target not in programs:
            print(f"'{target}' 프로그램을 페이지에서 찾지 못함")
            continue
        status, days, time = programs[target]
        print(f"{target}: {status}")
        prev = state.get(target)
        if status == prev:
            continue
        state[target] = status
        changed = True
        with open(HISTORY_FILE, "a", encoding="utf-8") as f:
            f.write(f"{now}\t{target}\t{prev} -> {status}\n")
        if prev is None:
            continue  # 첫 실행은 기준값만 저장
        if status == "등록가능":
            notify(f"🏊 **{target}** ({days} {time}) 자리 났어요! ({now})\n👉 {PAGE_URL}")
        elif status == "마감":
            notify(f"🔒 {target} 다시 마감됐어요 ({now})")

    if changed:
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
    return 0


if __name__ == "__main__":
    sys.exit(main())
