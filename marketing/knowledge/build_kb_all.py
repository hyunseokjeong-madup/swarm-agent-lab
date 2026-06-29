"""
통합 놀리지에셋 빌더 — build_kb.py ~ build_kb5.py 5개 스크립트를 하나로 합친 단일 엔트리포인트.

배경: 기존 5개 빌더(build_kb.py, build_kb2.py..build_kb5.py)는 각자 write() 헬퍼 +
메인 루프를 반복 정의해 보일러플레이트가 371줄에 달했다. 데이터(딕셔너리)는 다르지만
"카테고리/이름/제목/불릿 → md 파일" 로직은 동일했다. 이 파일은 그 로직을 하나로 통합한다.

설계(중복 제거 핵심):
- 각 원본 모듈의 데이터(딕셔너리)·write 로직은 그대로 두고, 원본이 실제로 디스크에 쓰려는
  (경로, 내용) 쌍만 Path.write_text 레벨에서 가로채 기록한다. 그 바이트 그대로 --out 으로 재생.
  → 데이터·포맷 복붙 없이 단일 엔트리포인트로 통합. 바디는 원본과 바이트 동일(구성상 보장).
- 원본 모듈은 import 시점에 디스크를 건드리지 않는다(가로채기로 차단). 실제 md 안전.

안전장치(중요):
- 기본 출력 디렉토리는 --out 로 받는 임시 폴더(기본 /tmp/kb_check)다.
  이미 커밋·frontmatter 추가된 실제 marketing/knowledge/**/*.md 를 절대 덮어쓰지 않는다.
  실제 디렉토리에 쓰려면 --out 으로 명시적으로 그 경로를 지정해야 한다.

상태 메모(consolidation):
- build_kb.py, build_kb2.py, build_kb3.py, build_kb4.py, build_kb5.py 는 이 파일로 대체(superseded)됨.
  동등성(바디 바이트 동일) 검증 완료 후, 후속 작업에서 안전하게 제거 가능.
  (지금은 보존 — 삭제는 별도 PR에서. KARPATHY: 검증 없는 삭제 금지.)

사용:
  python3 build_kb_all.py                      # /tmp/kb_check 에 생성 (실제 md 안전)
  python3 build_kb_all.py --out /tmp/kb_check  # 동등성 검증용
"""
import argparse
import sys
from pathlib import Path

HERE = Path(__file__).parent

# 5개 원본 빌더 — import 순서대로 데이터를 수집한다.
_SOURCE_MODULES = ["build_kb", "build_kb2", "build_kb3", "build_kb4", "build_kb5"]


def _collect_writes():
    """각 원본 모듈을 exec 하되 Path.write_text 를 가로채, (상대경로, 내용) 만 기록한다.

    반환: [(rel_path, text), ...]  — rel_path 는 HERE 기준 상대경로(예: "verticals/ecommerce.md").
    원본 모듈은 import 시점에 디스크를 건드리지 못한다(가로채기). 따라서 실제 md 안전.
    """
    records = []
    real_write_text = Path.write_text
    real_mkdir = Path.mkdir

    def spy_write_text(self, data, *a, **k):
        # 원본이 쓰려던 (경로, 내용) 만 기록. 실제 디스크에는 쓰지 않는다.
        rel = self.resolve().relative_to(HERE.resolve())
        records.append((rel, data))
        return len(data)

    def noop_mkdir(self, *a, **k):
        # 원본의 d.mkdir(...) 부작용 차단 (실제 디렉토리 생성 방지).
        return None

    Path.write_text = spy_write_text
    Path.mkdir = noop_mkdir
    try:
        for mod_name in _SOURCE_MODULES:
            src_path = HERE / f"{mod_name}.py"
            text = src_path.read_text(encoding="utf-8")
            ns = {
                "__file__": str(src_path),
                "__name__": mod_name,
                "print": lambda *a, **k: None,  # 원본의 진행 출력 억제
            }
            exec(compile(text, str(src_path), "exec"), ns)
    finally:
        Path.write_text = real_write_text
        Path.mkdir = real_mkdir

    return records


def build(out_dir):
    out = Path(out_dir)
    records = _collect_writes()
    count = 0
    for rel, text in records:
        target = out / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
        count += 1
    return count


def main():
    ap = argparse.ArgumentParser(description="통합 놀리지에셋 빌더 (5개 빌더 합본)")
    ap.add_argument("--out", default="/tmp/kb_check",
                    help="출력 디렉토리 (기본: /tmp/kb_check — 실제 md 를 덮어쓰지 않음)")
    args = ap.parse_args()

    real = (HERE).resolve()
    out = Path(args.out).resolve()
    if out == real:
        print(f"[refuse] --out 이 실제 knowledge 디렉토리({real})를 가리킵니다. "
              f"커밋·frontmatter 가 추가된 md 를 덮어쓰지 않도록 다른 경로를 쓰세요.",
              file=sys.stderr)
        sys.exit(2)

    n = build(args.out)
    print(f"generated {n} knowledge files -> {out}")


if __name__ == "__main__":
    main()
