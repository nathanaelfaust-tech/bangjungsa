#!/usr/bin/env python3
"""
Downloads 폴더에서 bangjungsa 프로젝트 관련 이미지를 찾아
assets/s1/ 하위 적절한 폴더에 분류하는 스크립트.

직접 실행: python3 sort_downloads.py
  --dry-run  : 실제 복사 없이 분류 결과만 미리 보기
  --move     : 복사 대신 이동 (기본값은 복사)
"""

import argparse
import re
import shutil
from pathlib import Path

# ── 경로 설정 ──────────────────────────────────────────────────────────────
DOWNLOADS = Path.home() / "Downloads"
ASSETS_S1 = Path(__file__).parent / "assets" / "s1"
ASSETS_S2 = Path(__file__).parent / "assets" / "s2"
VERIFY_DIR = Path(__file__).parent / "verify"
REFS_DIR   = Path(__file__).parent / "refs"

# ── 알려진 캐릭터 / 유닛 이름 ───────────────────────────────────────────────
UNITS = {"jeong2", "nyangsan", "mender", "kimwear", "guard", "hero", "abel"}

# ── 분류 규칙 (순서대로 첫 매칭) ────────────────────────────────────────────
#  각 항목: (설명, 정규식 패턴, 목적 폴더 결정 함수(match, filename) → Path)
RULES = [

    # 1. STG2 레이아웃 / 맵 프리뷰 → assets/s2/
    (
        "STG2 레이아웃·맵 프리뷰",
        re.compile(r"(?i)^stg2_"),
        lambda m, f: ASSETS_S2 / "maps",
    ),

    # 2. *_sheet* → refs/  (스프라이트 시트 원본)
    (
        "스프라이트 시트 원본 (refs)",
        re.compile(r"(?i)_(sheet|toprow)"),
        lambda m, f: REFS_DIR / _sheet_subfolder(f),
    ),

    # 3. 유닛명 + (card|idle|talk|focus|sleep|portrait) → units/
    (
        "캐릭터 초상화 (units/)",
        re.compile(r"(?i)^(" + "|".join(UNITS) + r")_(card|idle|talk|focus|sleep|portrait)"),
        lambda m, f: ASSETS_S1 / "units",
    ),

    # 4. 유닛명 + _ssot_ 또는 _ssot suffix → sprites_ssot/
    (
        "SSOT 스프라이트 (sprites_ssot/)",
        re.compile(r"(?i)^(" + "|".join(UNITS) + r").*_ssot"),
        lambda m, f: ASSETS_S1 / "sprites_ssot",
    ),

    # 5. 유닛명 + _raw_alpha_48 / raw_alpha → sprites_raw_alpha*
    (
        "알파 처리 48px 스프라이트 (sprites_raw_alpha_48/)",
        re.compile(r"(?i)^(" + "|".join(UNITS) + r").*_raw_alpha_48"),
        lambda m, f: ASSETS_S1 / "sprites_raw_alpha_48",
    ),
    (
        "알파 처리 스프라이트 (sprites_raw_alpha/)",
        re.compile(r"(?i)^(" + "|".join(UNITS) + r").*_raw_alpha"),
        lambda m, f: ASSETS_S1 / "sprites_raw_alpha",
    ),

    # 6. 유닛명 + _raw → sprites_raw/
    (
        "원본 스프라이트 (sprites_raw/)",
        re.compile(r"(?i)^(" + "|".join(UNITS) + r").*_raw"),
        lambda m, f: ASSETS_S1 / "sprites_raw",
    ),

    # 7. 유닛명 + _clean → sprites_clean/
    (
        "정제 스프라이트 (sprites_clean/)",
        re.compile(r"(?i)^(" + "|".join(UNITS) + r").*_clean"),
        lambda m, f: ASSETS_S1 / "sprites_clean",
    ),

    # 8. 유닛명 + 방향 (F/B/L/R) 또는 번호(_1/_2/_3) → sprites/
    #    예: jeong2_F.png  jeong2_1.png  nyangsan_new.png
    (
        "4방향·번호 스프라이트 (sprites/)",
        re.compile(r"(?i)^(" + "|".join(UNITS) + r")(_[FBLR]|_\d+|_new|_idle)"),
        lambda m, f: ASSETS_S1 / "sprites",
    ),

    # 9. Gemini / ChatGPT 생성 이미지 → refs/generated/
    (
        "AI 생성 이미지 (refs/generated/)",
        re.compile(r"(?i)^(gemini_generated|chatgpt.image)"),
        lambda m, f: REFS_DIR / "generated",
    ),

    # 10. verify / formal / stg2-verify 패턴 → verify/
    (
        "검증 이미지 (verify/)",
        re.compile(r"(?i)^(formal|stg2.verify|verify)"),
        lambda m, f: VERIFY_DIR,
    ),
]

# ── 헬퍼 ───────────────────────────────────────────────────────────────────
def _sheet_subfolder(filename: str) -> str:
    """시트 파일을 캐릭터명 기반 refs 하위 폴더로 매핑."""
    stem = Path(filename).stem.lower()
    for unit in UNITS:
        if stem.startswith(unit):
            return f"{unit}-sheets"
    return "misc-sheets"


def classify(filename: str):
    """파일명을 보고 (설명, 목적 폴더 Path) 반환. 미매칭이면 None."""
    for desc, pattern, dest_fn in RULES:
        m = pattern.search(filename)
        if m:
            return desc, dest_fn(m, filename)
    return None


IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp"}

def collect_candidates():
    """Downloads 에서 이미지 파일 목록 반환."""
    return [
        f for f in DOWNLOADS.iterdir()
        if f.is_file() and f.suffix.lower() in IMAGE_EXTS
    ]

# ── 메인 ───────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dry-run", action="store_true",
                        help="실제 파일 조작 없이 분류 결과만 출력")
    parser.add_argument("--move", action="store_true",
                        help="복사 대신 이동 (기본: 복사)")
    args = parser.parse_args()

    candidates = collect_candidates()
    if not candidates:
        print("Downloads 폴더에 이미지 파일이 없습니다.")
        return

    matched, skipped = [], []

    for src in sorted(candidates):
        result = classify(src.name)
        if result:
            matched.append((src, *result))
        else:
            skipped.append(src)

    # ── 미리보기 출력 ──────────────────────────────────────────────────────
    action_label = "이동" if args.move else "복사"
    mode_label   = "[DRY-RUN] " if args.dry_run else ""

    print(f"\n{mode_label}=== 분류 대상 ({len(matched)}개) ===")
    for src, desc, dest_dir in matched:
        rel = dest_dir.relative_to(Path(__file__).parent)
        print(f"  [{desc}]")
        print(f"    {src.name}  →  {rel}/")

    if skipped:
        print(f"\n{mode_label}=== 미매칭 (건너뜀, {len(skipped)}개) ===")
        for src in skipped:
            print(f"  {src.name}")

    if args.dry_run:
        print("\n(--dry-run 모드: 실제 파일 조작 없음)")
        return

    # ── 실제 파일 조작 ─────────────────────────────────────────────────────
    print(f"\n{len(matched)}개 파일을 {action_label}합니다...")
    ok, fail = 0, 0
    for src, desc, dest_dir in matched:
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / src.name

        # 같은 이름 파일이 이미 있으면 덮어쓰기 전 확인
        if dest.exists():
            ans = input(f"  이미 존재: {dest.name} — 덮어쓰시겠습니까? [y/N] ").strip().lower()
            if ans != "y":
                print(f"  건너뜀: {src.name}")
                continue

        try:
            if args.move:
                shutil.move(str(src), dest)
            else:
                shutil.copy2(src, dest)
            print(f"  ✓ {src.name}  →  {dest.relative_to(Path(__file__).parent)}")
            ok += 1
        except Exception as e:
            print(f"  ✗ {src.name}: {e}")
            fail += 1

    print(f"\n완료: 성공 {ok}개" + (f", 실패 {fail}개" if fail else ""))


if __name__ == "__main__":
    main()
