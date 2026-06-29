"""
자기개선 루프 관찰 리포트 — FEEDBACK_LOG.md 를 파싱해 학습 이력을 요약한다.

순수 observer: 부작용 0, 네트워크 0, 쓰기 0. 로그에 *실제로 있는 것만* 센다.
  - 총 피드백 건수, scope(global/account)별·tag별 분포, 최초/최근 날짜.

의도적으로 *하지 않는* 것: 성공률·태그별 정확도·루프 효과 같은 지표.
FEEDBACK_LOG 엔 success/outcome 필드가 없다 → 그런 산술을 내면 없는 데이터를 날조하는
것이고 madobi 의 핵심 약속('산술은 코드가 보장')을 정면으로 깬다. 효과 판단은 LLM/사람 몫.

사용:
  python marketing/loop_report.py            # 요약 리포트
  python marketing/loop_report.py --selftest # 비대화 검증(종료코드 0/1)
"""
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOG = ROOT / "FEEDBACK_LOG.md"

# learn.py 가 쓰는 줄 포맷: "- [<ts>] scope=<scope>[/acct] tag=<tag>: <body>"
_LINE_RE = re.compile(
    r"^- \[(?P<ts>[^\]]+)\] scope=(?P<scope>[^\s/]+)(?:/(?P<acct>\S+))? tag=(?P<tag>\S+): (?P<body>.*)$"
)
_DATE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})")


def parse_log(text):
    """FEEDBACK_LOG 본문 → [{ts, scope, acct, tag, body, date}]. 매칭 안 되는 줄은 무시."""
    rows = []
    for line in text.splitlines():
        m = _LINE_RE.match(line.strip())
        if not m:
            continue
        d = m.groupdict()
        dm = _DATE_RE.match(d["ts"])
        d["date"] = dm.group(1) if dm else None
        rows.append(d)
    return rows


def _counts(rows, key):
    """key 별 건수 dict (결정론 — 키 정렬은 호출측에서)."""
    out = {}
    for r in rows:
        out[r[key]] = out.get(r[key], 0) + 1
    return out


def summarize(rows):
    """로그에 실제 있는 사실만 요약(dict). 없는 지표는 만들지 않는다."""
    dates = sorted(r["date"] for r in rows if r["date"])
    return {
        "total": len(rows),
        "by_scope": _counts(rows, "scope"),
        "by_tag": _counts(rows, "tag"),
        "first_date": dates[0] if dates else None,
        "last_date": dates[-1] if dates else None,
    }


def render(summary):
    L = ["\n=== SELF-IMPROVEMENT LOOP REPORT ===",
         f"누적 피드백(학습) {summary['total']}건"]
    if summary["first_date"]:
        L.append(f"기간: {summary['first_date']} ~ {summary['last_date']}")
    if summary["by_scope"]:
        L.append("\nscope별:")
        for k in sorted(summary["by_scope"]):
            L.append(f"  - {k}: {summary['by_scope'][k]}건")
    if summary["by_tag"]:
        L.append("\ntag별:")
        for k in sorted(summary["by_tag"], key=lambda t: (-summary["by_tag"][t], t)):
            L.append(f"  - {k}: {summary['by_tag'][k]}건")
    L.append("\n  · observer 전용 — 로그에 있는 것만 집계. 성공률/효과는 데이터에 없어 출력 안 함(추측 금지).")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser(description="자기개선 루프 관찰 리포트(FEEDBACK_LOG observer)")
    ap.add_argument("--selftest", action="store_true", help="비대화 검증(종료코드 0/1)")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not LOG.exists():
        print("FEEDBACK_LOG.md 없음 — 아직 학습 이력이 없습니다.")
        return 0
    rows = parse_log(LOG.read_text(encoding="utf-8"))
    print(render(summarize(rows)))
    return 0


def _selftest():
    # 합성 샘플로 파서·집계의 정확성을 단언(실 로그 상태에 의존하지 않게).
    sample = (
        "# Feedback Log\n\n"
        "- [2026-06-01 10:00 KST] scope=global tag=report: ROAS는 배수\n"
        "- [2026-06-02 11:00 KST] scope=account/acme tag=report: 18-24 핵심\n"
        "- [2026-06-03 12:00 KST] scope=global tag=reconciliation: 검산 후 보고\n"
        "garbage line that should be ignored\n"
    )
    rows = parse_log(sample)
    assert len(rows) == 3, f"파싱 건수 오류: {len(rows)}"
    s = summarize(rows)
    assert s["total"] == 3
    assert s["by_scope"] == {"global": 2, "account": 1}, f"scope 집계 오류: {s['by_scope']}"
    assert s["by_tag"] == {"report": 2, "reconciliation": 1}, f"tag 집계 오류: {s['by_tag']}"
    assert s["first_date"] == "2026-06-01" and s["last_date"] == "2026-06-03", "날짜 범위 오류"
    # account 줄의 acct 캡처 확인
    acct_row = next(r for r in rows if r["scope"] == "account")
    assert acct_row["acct"] == "acme", f"account 캡처 오류: {acct_row['acct']}"
    # 결정론: 같은 입력 두 번 → 같은 요약
    assert summarize(parse_log(sample)) == s, "비결정적"
    print("SELF-IMPROVEMENT LOOP REPORT self-test: PASS  (파서·scope/tag 집계·날짜범위·결정론)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
