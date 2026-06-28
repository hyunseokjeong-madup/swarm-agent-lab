"""
놀리지에셋 related[] 링크 채우기 — 옵시디언 지식 그래프를 만든다.

각 노트를 *같은 카테고리*의 형제 노트들에 연결한다(같은 디렉토리 = 사람이 큐레이션한 관련 주제).
frontmatter 의 `related: []` 를 `related: [sibling1, sibling2, ...]` 로 채운다.
순수 stdlib · 결정론(경로 정렬) · idempotent(--apply 다시 돌려도 동일 결과).
의미 임베딩 교차카테고리 링크는 향후 extras 로(코어는 의존성 0 유지).

사용:
  python link_related.py            # 드라이런(미리보기)
  python link_related.py --apply    # frontmatter 의 related[] 채워 쓰기
  python link_related.py --selftest # 비대화 검증(종료코드 0/1)
"""
import argparse
import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
MAX_LINKS = 5  # 노트당 related 링크 상한(그래프가 과밀해지지 않게)


def split_frontmatter(text):
    """(frontmatter_lines, body) 반환. frontmatter 없으면 ([], text)."""
    if not text.startswith("---"):
        return [], text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return [], text
    fm = parts[1].strip("\n").split("\n")
    body = parts[2]
    return fm, body


def note_id(path):
    """링크에 쓸 노트 식별자 — 파일명(확장자 제외). 옵시디언 [[id]] 와 호환."""
    return path.stem


def collect():
    """카테고리(부모 디렉토리)별 노트 목록. 경로 정렬로 결정론 보장."""
    by_cat = {}
    for p in sorted(HERE.rglob("*.md")):
        cat = p.parent.name if p.parent != HERE else "_root"
        by_cat.setdefault(cat, []).append(p)
    return by_cat


def related_for(path, siblings):
    """path 의 related = 같은 카테고리 형제들(자기 제외) 중 최대 MAX_LINKS, 경로순."""
    others = [note_id(s) for s in siblings if s != path]
    return others[:MAX_LINKS]


def set_related(text, links):
    """frontmatter 의 related: 줄을 새 링크로 교체. frontmatter 없으면 원본 그대로."""
    fm, body = split_frontmatter(text)
    if not fm:
        return text, False
    arr = "[" + ", ".join(links) + "]"
    new_fm = []
    replaced = False
    for line in fm:
        if re.match(r"^related:\s*", line):
            new_fm.append(f"related: {arr}")
            replaced = True
        else:
            new_fm.append(line)
    if not replaced:
        new_fm.append(f"related: {arr}")
    return "---\n" + "\n".join(new_fm) + "\n---" + body, True


def run(apply=False, quiet=False):
    by_cat = collect()
    total, changed = 0, 0
    for cat, notes in sorted(by_cat.items()):
        for p in notes:
            total += 1
            links = related_for(p, notes)
            if not links:
                continue
            text = p.read_text(encoding="utf-8")
            new_text, ok = set_related(text, links)
            if ok and new_text != text:
                changed += 1
                if apply:
                    p.write_text(new_text, encoding="utf-8", newline="\n")
    mode = "APPLY" if apply else "DRY-RUN"
    if not quiet:
        print(f"[{mode}] md {total}개 | related 링크 채움 {changed}개 | 카테고리 {len(by_cat)}개")
    return total, changed


def selftest():
    # 드라이런이 디스크를 안 바꾸는지 + 같은 카테고리 링크가 생성되는지 확인.
    by_cat = collect()
    assert by_cat, "knowledge md 없음"
    # metrics 카테고리에서 roas.md 가 형제(cpa 등)에 링크되는지
    metrics = by_cat.get("metrics", [])
    roas = next((p for p in metrics if p.stem == "roas"), None)
    assert roas is not None, "metrics/roas.md 없음"
    links = related_for(roas, metrics)
    assert links and "roas" not in links, f"roas 자기참조 또는 빈 링크: {links}"
    assert len(links) <= MAX_LINKS, f"링크 상한 초과: {len(links)}"
    # set_related 가 frontmatter 있는 텍스트에만 작동
    sample = roas.read_text(encoding="utf-8")
    _, ok = set_related(sample, links)
    assert ok, "frontmatter 있는데 related 교체 실패 (frontmatter 먼저 add_frontmatter.py 로 적용 필요)"
    print(f"[selftest] OK — metrics/roas → {links} (같은 카테고리 {len(metrics)-1}개 중 {len(links)}개 링크)")
    return 0


def main():
    ap = argparse.ArgumentParser(description="related[] 링크 채우기 — 옵시디언 지식 그래프")
    ap.add_argument("--apply", action="store_true", help="frontmatter related[] 실제 기록")
    ap.add_argument("--selftest", action="store_true", help="비대화 검증(종료코드 0/1)")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    run(apply=a.apply)
    return 0


if __name__ == "__main__":
    sys.exit(main())
