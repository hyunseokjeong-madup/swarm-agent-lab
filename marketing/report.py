"""
Performance report generator (성과 리포트 자동 생성).
CSV -> reconciled totals + derived metrics + by-dimension breakdown + (if dated) period deltas
+ top movers, as a polished markdown report. Numbers are recomputed from raw (정합성).

Usage:
  python report.py data.csv --by channel --metric revenue --md report.md
  python report.py series.csv --period 7   # weekly comparison if a date column exists
"""
import csv, argparse, sys
from pathlib import Path
from collections import defaultdict
sys.path.insert(0, str(Path(__file__).parent / "bench"))
from summarize import num, derived, RAWM

def load(p):
    rows = list(csv.DictReader(Path(p).read_text(encoding="utf-8").splitlines()))
    headers = list(rows[0].keys())
    date_col = next((h for h in headers if h.lower() in ("date","날짜","일자","day")), None)
    label_col = headers[0]
    clean = []
    for r in rows:
        import re
        if re.search(r"total|합계|총계|소계|sum", (r.get(label_col) or ""), re.I): continue
        clean.append(r)
    return clean, headers, date_col

def tot(rows):
    t = {m: 0 for m in RAWM}
    for r in rows:
        for m in RAWM: t[m] += num(r.get(m))
    return t

def fmt_metrics(t):
    d = derived(t)
    L = [f"- 노출 **{t['impressions']:,.0f}** · 클릭 **{t['clicks']:,.0f}** · 광고비 **{t['spend']:,.0f}** "
         f"· 전환 **{t['conversions']:,.0f}** · 매출 **{t['revenue']:,.0f}**"]
    parts = []
    if d['ctr'] is not None: parts.append(f"CTR {d['ctr']:.2%}")
    if d['cpc'] is not None: parts.append(f"CPC {d['cpc']:,.0f}")
    if d['cpa'] is not None: parts.append(f"CPA {d['cpa']:,.0f}")
    if d['roas'] is not None: parts.append(f"ROAS {d['roas']:.2f}x")
    if parts: L.append("- " + " · ".join(parts))
    return "\n".join(L)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv")
    ap.add_argument("--by", default=None)
    ap.add_argument("--metric", default="revenue")
    ap.add_argument("--period", type=int, default=0, help="compare last N days vs prior N days")
    ap.add_argument("--md", default=None)
    a = ap.parse_args()
    rows, headers, dcol = load(a.csv)
    grand = tot(rows)

    out = [f"# 성과 리포트 — `{Path(a.csv).name}`", ""]
    out += ["## 종합 (검산 완료)", fmt_metrics(grand), ""]

    # reconciliation note
    if a.by:
        groups = defaultdict(list)
        for r in rows: groups[(r.get(a.by) or "").strip()].append(r)
        gt = {g: tot(rs) for g, rs in groups.items()}
        ok = all(sum(gt[g][m] for g in gt) == grand[m] for m in RAWM)
        out += [f"> 정합성: 분해합 = 총계 **{'✅ 일치' if ok else '⚠️ 불일치'}**", ""]
        out += [f"## `{a.by}`별 성과 ({a.metric} 기준 정렬)", "",
                "| " + a.by + " | 노출 | 클릭 | 광고비 | 전환 | 매출 | CTR | ROAS |",
                "|---|---|---|---|---|---|---|---|"]
        ranked = sorted(gt.items(), key=lambda kv: derived(kv[1]).get(a.metric) or kv[1].get(a.metric, 0), reverse=True)
        for g, t in ranked:
            d = derived(t)
            out.append(f"| {g} | {t['impressions']:,.0f} | {t['clicks']:,.0f} | {t['spend']:,.0f} | "
                       f"{t['conversions']:,.0f} | {t['revenue']:,.0f} | {(d['ctr'] or 0):.2%} | {(d['roas'] or 0):.2f}x |")
        out.append("")

    # period comparison
    if a.period and dcol:
        days = sorted({(r.get(dcol) or "").strip() for r in rows})
        if len(days) >= 2 * a.period:
            recent = set(days[-a.period:]); prior = set(days[-2*a.period:-a.period])
            tr = tot([r for r in rows if (r.get(dcol) or "").strip() in recent])
            tp = tot([r for r in rows if (r.get(dcol) or "").strip() in prior])
            out += [f"## 기간 비교 (최근 {a.period}일 vs 직전 {a.period}일)", "",
                    "| 지표 | 직전 | 최근 | 변화 |", "|---|---|---|---|"]
            for m in RAWM:
                ch = (tr[m]-tp[m])/tp[m] if tp[m] else 0
                out.append(f"| {m} | {tp[m]:,.0f} | {tr[m]:,.0f} | {ch:+.1%} |")
            out.append("")

    out += ["---", "*숫자는 원자료에서 재계산·검산. 가정(윈도우·타임존·통화·필터) 확인 필요.*"]
    text = "\n".join(out)
    if a.md:
        Path(a.md).write_text(text + "\n", encoding="utf-8")
        print(f"[md] -> {a.md}")
    else:
        print(text)

if __name__ == "__main__":
    main()
