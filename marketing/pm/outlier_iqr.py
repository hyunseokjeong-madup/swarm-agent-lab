"""
IQR 이상치 탐지 — Tukey 울타리(Q1−1.5·IQR, Q3+1.5·IQR) 밖 값을 이상치로 표시.
시계열 무관 분포 기반(단일 컬럼). 사분위 계산 정확.

입력 CSV: name(첫 열) + 대상 수치 컬럼
Usage: python outlier_iqr.py data.csv --col cpa [--k 1.5]
"""
import argparse, csv, re
from pathlib import Path
def num(s):
    s=str(s or "").replace(",","").replace("₩","").replace("%","").replace("x","").strip()
    try: return float(s)
    except: return None
def quantile(sorted_v, q):
    n=len(sorted_v)
    if n==1: return sorted_v[0]
    pos=q*(n-1); lo=int(pos); frac=pos-lo
    return sorted_v[lo] + (sorted_v[lo+1]-sorted_v[lo])*frac if lo+1<n else sorted_v[lo]
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("csv"); ap.add_argument("--col",required=True); ap.add_argument("--k",type=float,default=1.5)
    a=ap.parse_args()
    rows=list(csv.DictReader(Path(a.csv).read_text(encoding="utf-8").splitlines()))
    name=list(rows[0])[0]; h={c.lower():c for c in rows[0]}; col=h.get(a.col.lower())
    ents=[((r.get(name) or "").strip(),num(r.get(col))) for r in rows if not re.search(r"total|합계|총계",(r.get(name) or ""),re.I)]
    vals=sorted(v for _,v in ents if v is not None)
    if len(vals)<4: print("데이터 부족"); return
    q1=quantile(vals,0.25); q3=quantile(vals,0.75); iqr=q3-q1
    lo=q1-a.k*iqr; hi=q3+a.k*iqr
    print(f"\n=== IQR OUTLIERS ({a.col}, k={a.k}) ===")
    print(f"Q1={q1:,.2f} · Q3={q3:,.2f} · IQR={iqr:,.2f} · 울타리 [{lo:,.2f}, {hi:,.2f}]")
    out=[(nm,v) for nm,v in ents if v is not None and (v<lo or v>hi)]
    if out:
        print(f"이상치 {len(out)}건:")
        for nm,v in out: print(f"  ⚠️ {nm}: {v:,.2f} ({'하단' if v<lo else '상단'})")
    else: print("이상치 없음")
    print("  · 분포 기반(로버스트). 보고 전 극단값 점검.")
if __name__=="__main__": main()
