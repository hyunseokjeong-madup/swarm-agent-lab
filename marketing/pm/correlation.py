"""
피어슨 상관 — 두 수치 컬럼의 상관계수(시너지/잠식/연관 탐지). r=cov/(sx·sy). 계산 정확.
* 상관≠인과. 교란요인 주의.

입력 CSV: 두 수치 컬럼
Usage: python correlation.py data.csv --x spend --y conversions
"""
import argparse, csv, math, re
from pathlib import Path
from _pmutil import load_rows  # 빈 데이터 우아한 처리
def num(s):
    s=str(s or "").replace(",","").replace("₩","").replace("%","").strip()
    try: return float(s)
    except: return None
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("csv"); ap.add_argument("--x",required=True); ap.add_argument("--y",required=True)
    a=ap.parse_args()
    rows=load_rows(a.csv)
    h={c.lower():c for c in rows[0]}; xc=h.get(a.x.lower()); yc=h.get(a.y.lower())
    first=list(rows[0])[0]
    rows=[r for r in rows if not re.search(r"total|합계|총계|소계",(r.get(first) or ""),re.I)]
    pts=[(num(r.get(xc)),num(r.get(yc))) for r in rows]
    pts=[(x,y) for x,y in pts if x is not None and y is not None]
    n=len(pts)
    if n<3: print("데이터 부족"); return
    mx=sum(x for x,_ in pts)/n; my=sum(y for _,y in pts)/n
    sxy=sum((x-mx)*(y-my) for x,y in pts)
    sxx=sum((x-mx)**2 for x,_ in pts); syy=sum((y-my)**2 for _,y in pts)
    r=sxy/math.sqrt(sxx*syy) if sxx>0 and syy>0 else 0
    print(f"\n=== CORRELATION ({a.x} vs {a.y}, n={n}) ===")
    print(f"피어슨 r = {r:+.3f}  ·  r² = {r*r:.3f}")
    s=abs(r); kind=("매우 강함" if s>0.8 else "강함" if s>0.6 else "중간" if s>0.4 else "약함" if s>0.2 else "거의 없음")
    sign="양(동반 상승)" if r>0 else "음(상충/잠식 가능)"
    print(f"해석: {kind} {sign} 상관. * 상관≠인과.")
if __name__=="__main__": main()
