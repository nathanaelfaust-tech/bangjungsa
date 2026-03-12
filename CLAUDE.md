# CLAUDE.md — bangjungsa 프로젝트 규칙

## 프로젝트 개요

한국어 SRPG(전술 턴제 RPG) 웹 프로토타입.
게임 로직은 `index.html` / `srpg.html` 내 인라인 JavaScript로 구현.
외부 빌드 시스템 없음 — 브라우저에서 직접 열어서 실행.

---

## 이미지 자산 규칙

### 절대 금지
- **이미지 파일을 직접 생성하지 않는다.** PNG·JPG 등 바이너리 이미지를 코드로 만들거나 플레이스홀더를 생성하는 행위 금지.
- **이미지 파일을 임의로 수정하지 않는다.** PIL/Pillow 등으로 기존 이미지를 가공하는 코드를 실행하기 전에 반드시 확인을 받는다.
- **없는 자산을 플레이스홀더 코드로 대체하지 않는다.** 자산이 누락된 경우 임시 색상 블록·더미 데이터 등으로 메우지 말고, 사용자에게 먼저 알린다.

### 이미지 공급 경로
새 이미지가 필요하면 사용자가 직접 제공한다.
- 외부 툴(Gemini, ChatGPT, 등)로 생성 → Downloads 폴더에 저장 → `sort_downloads.py` 로 분류

### 에셋 폴더 구조 (변경 전 확인 필요)
```
assets/s1/
  sprites/          # 4방향(F/B/L/R) 맵용 스프라이트, idle
  sprites_clean/    # 정제 버전
  sprites_raw/      # 원본
  sprites_raw_alpha/   # 알파 처리
  sprites_raw_alpha_48/
  sprites_ssot/     # Single Source of Truth (최종본)
  units/            # 캐릭터 초상화 (card, idle, talk, focus, sleep)
  icons/
  vfx/
assets/s2/
  maps/             # STG2 맵 레이아웃 프리뷰
refs/
  jeong2-sheets/    # jeong2 스프라이트 시트 원본
  nyangsan-sheets/  # nyangsan 스프라이트 시트 원본
  generated/        # AI 생성 참조 이미지
  jeong2-genref-v1/ # jeong2 생성 참조 세트
  jeong2-static-v1/ # jeong2 정적 참조 세트
verify/             # 검증 이미지, 로그, HTML 비교 도구
```

---

## 파일 덮어쓰기 규칙

- **기존 파일을 덮어쓰기 전에 반드시 사용자에게 확인을 요청한다.**
- 특히 `assets/`, `refs/`, `verify/` 하위 파일은 수작업으로 제작된 에셋이므로 더욱 주의.
- `manifest.json` 수정 시 변경 내용을 먼저 설명하고 승인을 받는다.

---

## 코드 규칙

- `index.html` / `srpg.html` 은 인라인 JS/CSS가 포함된 대형 파일(6천~1만 줄). 편집 시 해당 섹션을 Read로 먼저 확인하고 수정한다.
- `manifest.json` 은 에셋 경로의 Single Source of Truth. 새 에셋 추가 시 manifest도 함께 업데이트한다.
- 알려진 유닛: `jeong2`, `nyangsan`, `mender`, `kimwear`, `guard`, `hero`, `abel`

---

## Git 규칙

- 이미지 파일과 스크립트/코드는 **별도 커밋**으로 분리한다.
- 푸시 전에 무엇을 커밋하는지 사용자에게 확인한다.
- 커밋 메시지는 영어로, 변경 내용을 간결하게 기술한다.

---

## 유틸리티

- `sort_downloads.py` — Downloads 폴더 이미지를 패턴 기반으로 assets/ 에 분류
  - `--dry-run` : 미리보기
  - `--move` : 복사 대신 이동
