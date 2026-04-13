# Harness Use Cases

하네스를 실제로 쓴 기록. 글 쓸 때 사례로 활용.

| 날짜 | 태스크 | 유형 | 결과 | 체인 | 인사이트 |
|------|--------|------|------|------|----------|
| 2026-04-03 | evan-harness 구조 리뷰 | PM | PASS (7/7 기준 충족) | 0 | 도구 제한 불일치·경로 패턴 혼재·미참조 자원 등 12건 발견. 요약 숫자 오류 등 경미한 concern 3건 |
| 2026-04-06 | 디렉토리 파일 뷰어 | Coding | PASS (9/9) | 0 | 단일 Python 파일 602줄. marked.js+highlight.js CDN으로 마크다운/코드 렌더링. Reviewer가 실제 서버 실행+curl 테스트까지 수행 |
| 2026-04-06 | MD 파일 뷰어 | Coding | PASS (9/9, 재검증 1회) | 0 | viewer.py 스타일 재활용. TOC+라이브리로드+진행률바. 미사용 import 1건으로 FAIL→수정→PASS |
| 2026-04-06 | /view 커맨드 통합 | Coding | PASS (6/6) | 0 | 기존 디렉토리 전용 /view를 파일+디렉토리 통합으로 확장. view.md + plugin.json 2파일만 수정 |
