"""
집중도 HHI — Herfindahl-Hirschman 지수(점유율 제곱합)로 채널/상품 집중도 측정.
HHI=Σ s_i^2 (0~1). 유효 개수 = 1/HHI. 낮을수록 분산(리스크↓), 높을수록 집중. 계산 정확.

입력 CSV: name(첫 열), value(spend/revenue)
Usage: python hhi.py data.csv --value spend
"""
import argparse, csv, re
from pathlib import Path
from _pmutil import load_rows  # 빈 데이터 우아한 처리(IndexError 방지)
def num(s):
    s=str(s or "").replace(",","").replace("₩","").strip()
    try: return float(s)
    except: return 0.0
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("csv"); ap.add_argument("--value",default=None)
    a=ap.parse_args()
    rows=load_rows(a.csv)
    name=list(rows[0])[0]; vc=a.value or next((c for c in rows[0] if c.lower() in ("spend","revenue","value")),list(rows[0])[1])
    items=[((r.get(name) or "").strip(),num(r.get(vc))) for r in rows if not re.search(r"total|합계|총계",(r.get(name) or ""),re.I)]
    tot=sum(v for _,v in items) or 1
    shares=[(nm,v/tot) for nm,v in items]
    hhi=sum(s*s for _,s in shares)
    eff=1/hhi if hhi else 0
    shares.sort(key=lambda x:-x[1])
    print(f"\n=== CONCENTRATION (HHI, {vc}) ===")
    for nm,s in shares: print(f"  {nm.ljust(16)} 점유율 {s:>6.1%}")
    print(f"\nHHI = {hhi:.4f} (0~1) · 유효 {vc} 개수 = {eff:.2f}")
    lvl="고집중(리스크)" if hhi>0.25 else ("중간" if hhi>0.15 else "분산(건전)")
    print(f"판정: {lvl}. 단일 채널 의존도 높으면 분산 검토.")
if __name__=="__main__": main()
