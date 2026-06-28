"""
Geo 증분성(geo holdout) — 이중차분(difference-in-differences)으로 광고 순증분 추정.
test(광고 노출) vs control(미노출) 그룹의 pre/post를 비교, control 성장으로 보정한 반사실 대비 증분.
계산 정확. * 지역 동질성·외생요인 통제 가정.

입력 CSV: geo, group(test/control), pre, post
Usage: python geo_lift.py geos.csv
"""
import argparse, csv, re
from pathlib import Path
from _pmutil import load_rows  # 빈 데이터 우아한 처리
def num(s):
    s=str(s or "").replace(",","").strip()
    try: return float(s)
    except: return 0.0
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("csv"); a=ap.parse_args()
    rows=load_rows(a.csv)
    g={"test":[0,0],"control":[0,0]}
    for r in rows:
        grp=(r.get("group") or "").strip().lower()
        if grp in g: g[grp][0]+=num(r.get("pre")); g[grp][1]+=num(r.get("post"))
    tp,tq=g["test"]; cp,cq=g["control"]
    growth=cq/cp if cp else 1.0
    expected=tp*growth
    inc=tq-expected
    lift=inc/expected if expected else 0
    print(f"\n=== GEO INCREMENTALITY (DiD) ===")
    print(f"test  pre={tp:,.0f} post={tq:,.0f}")
    print(f"control pre={cp:,.0f} post={cq:,.0f}  (organic growth {growth:.3f}x = {growth-1:+.1%})")
    print(f"반사실 기대 test_post = {expected:,.0f}")
    print(f"증분(incremental) = {inc:,.0f}  ·  증분 리프트 = {lift:+.1%}")
    print("  * DiD 추정. 지역 동질성·동시 외생요인 통제 필요.")
if __name__=="__main__": main()
