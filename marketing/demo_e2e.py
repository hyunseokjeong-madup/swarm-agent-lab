"""
E2E 데모 — 마케터가 캠페인 CSV를 던졌을 때 MADOBI가 하는 전체 흐름을 한 번에 보여준다.
"산술은 코드가 보장, 통찰은 LLM이 판단"의 *코드 보장* 파트를 실제로 실행한다.

흐름: 맥락 회상 → 검산(reconcile) → 집계(summarize, TOTAL행 제외) → 삼중검증(있으면) → 정합성 판정.
이 스크립트는 기존 도구를 오케스트레이션만 한다(새 계산 로직 없음). 순수 stdlib.

사용:
  python marketing/demo_e2e.py                                  # 기본 샘플로 데모
  python marketing/demo_e2e.py marketing/samples/sample_campaign.csv --account demo_ecommerce
  python marketing/demo_e2e.py <your.csv> --selftest            # 비대화 검증(종료코드 0/1)
"""
import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent  # repo root
MARKETING = ROOT / "marketing"
DEFAULT_CSV = MARKETING / "samples" / "sample_campaign.csv"


def run(cmd):
    """도구 하나를 실행하고 (returncode, stdout) 반환. 순수 stdlib subprocess."""
    r = subprocess.run(
        [sys.executable, *cmd], cwd=str(ROOT),
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def step(title):
    print(f"\n{'─' * 56}\n▶ {title}\n{'─' * 56}")


def demo(csv_path, account=None, quiet=False):
    """전체 E2E 흐름. 각 단계의 핵심 출력을 모아 dict로 반환(셀프테스트용)."""
    csv_path = Path(csv_path)
    out = {"csv": str(csv_path), "steps": {}}

    # 1) 맥락 회상 (계정 지정 시) — 검색 기반, 214개 전체 read 금지
    if account:
        if not quiet:
            step(f"1. 맥락 회상 — recall.py (account={account})")
        rc, o = run(["marketing/knowledge/recall.py", "--account", account, "--query", "ROAS CPA", "--limit", "3"])
        out["steps"]["recall"] = rc
        if not quiet:
            print(o.strip()[:600] or "(회상 결과 없음)")

    # 2) 검산 — reconcile.py: 보고값 vs 원자료 불일치 적발
    if not quiet:
        step("2. 검산 — reconcile.py (산술 오류·합계≠총계 적발)")
    rc, o = run(["marketing/reconcile.py", str(csv_path)])
    out["steps"]["reconcile_rc"] = rc
    out["steps"]["reconcile_verdict"] = "INCONSISTENCY" if "INCONSISTENCY" in o else "CONSISTENT"
    if not quiet:
        print(o.strip()[-700:])

    # 3) 집계 — summarize.py (TOTAL행 제외 = 이중계산 방지)
    if not quiet:
        step("3. 집계 — summarize.py (가중평균 Σ/Σ, TOTAL행 제외)")
    rc, o = run(["marketing/bench/summarize.py", str(csv_path), "--by", "creative"])
    out["steps"]["summarize_rc"] = rc
    if not quiet:
        print(o.strip()[:700])

    # 4) 삼중검증 — sql_query.py (duckdb 있으면 SQL↔파이썬 일치 확인, 없으면 자동 스킵)
    if not quiet:
        step("4. 삼중검증 — sql_query.py (DuckDB↔Python, 없으면 파이썬만)")
    rc, o = run(["marketing/sql_query.py", str(csv_path), "--group-by", "creative", "--metric", "roas"])
    out["steps"]["sql_query_rc"] = rc
    if not quiet:
        verdict = "VERIFIED" if "VERIFIED" in o or "verified" in o.lower() else "PYTHON-ONLY"
        print(f"  → {verdict}\n" + o.strip()[:400])

    # 5) 정합성 판정 한 줄
    if not quiet:
        step("5. 정합성 판정")
        verdict = out["steps"].get("reconcile_verdict")
        if verdict == "CONSISTENT":
            print("  ✅ CONSISTENT — 보고 가능 (산술 검산 통과)")
        else:
            print("  ⚠️  INCONSISTENCY 발견 — 원자료 spot-check 권고 (보고 전 점검)")
        print("\n  ※ 코드가 보장하는 것: 위 산술의 정확성. 보장 못 하는 것: 데이터 품질(채널 오분류 등).")

    return out


def selftest():
    """비대화 검증: 기본 샘플로 흐름이 끝까지 도는지 + 알려진 불일치를 잡는지."""
    res = demo(DEFAULT_CSV, account="demo_ecommerce", quiet=True)
    s = res["steps"]
    # sample_campaign.csv 엔 의도된 불일치(C_carousel CTR, SUM spend)가 있음 → 반드시 적발해야 함
    assert s.get("reconcile_verdict") == "INCONSISTENCY", "reconcile이 알려진 불일치를 놓침"
    assert s.get("summarize_rc") == 0, "summarize 실행 실패"
    assert s.get("sql_query_rc") == 0, "sql_query 실행 실패"
    print("[selftest] OK — E2E 흐름 정상 + 알려진 불일치 적발(reconcile=INCONSISTENCY)")
    return 0


def main():
    ap = argparse.ArgumentParser(description="MADOBI E2E 데모 — 검산→집계→삼중검증 흐름")
    ap.add_argument("csv", nargs="?", default=str(DEFAULT_CSV), help="캠페인 CSV (기본: sample_campaign.csv)")
    ap.add_argument("--account", default=None, help="맥락 회상할 계정(예: demo_ecommerce)")
    ap.add_argument("--selftest", action="store_true", help="비대화 검증(종료코드 0/1)")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not Path(a.csv).exists():
        print(f"[error] CSV 없음: {a.csv}")
        return 1
    print("MADOBI E2E 데모 — '산술은 코드가 보장, 통찰은 LLM이 판단'")
    demo(a.csv, account=a.account)
    return 0


if __name__ == "__main__":
    sys.exit(main())
