# saba-swim-alert

부산광역시생활체육문화센터 [인터넷 접수](https://www.saba.or.kr/sub/progapp.php?pn=0506) 페이지를 GitHub Actions로 5분마다 확인하고, 감시 중인 강좌가 `마감` → `등록`으로 바뀌면 디스코드로 알립니다.

- 감시 대상: 기본값 `몸짱수영 C(상급)`. 바꾸려면 저장소 Variables에 `TARGETS`를 쉼표로 구분해 등록합니다 (예: `몸짱수영 C(상급),점심수영 A(상급)`)
- 디스코드 웹훅: 저장소 Secrets에 `DISCORD_WEBHOOK_URL` 등록
- `history.log`: 상태가 바뀐 시각 기록 (취소가 풀리는 패턴 확인용)
- 수동 실행: Actions 탭 → check → Run workflow

GitHub 예약 실행은 부하에 따라 수 분~십수 분 늦게 돌 수 있습니다.
