"""
시계열 이상탐지 — 추세(이동중앙값) + 요일계절 + 잔차(MAD) 분해.
단순 z보다 견고: 추세·요일효과 제거 후 잔차의 로버스트 z(0.6745*(x-med)/MAD)로 탐지.
계산 정확. 임계는 |robust z| >= k.

입력 CSV: date, <metric>
Usage: python anomaly_ts.py series.csv --metric revenue --k 3.5 [--window 7]
"""
import argparse, csv
from datetime import datetime
from pathlib import Path
from _pmutil import load_rows  # 빈 데이터 우아한 처리
from statistics import median

def num(s):
    s=str(s or "").replace(",","").replace("₩","").replace("%","").strip()
    try: return float(s)
    except: return 0.0

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("csv")
    ap.add_argument("--metric",default="revenue"); ap.add_argument("--k",type=float,default=3.5); ap.add_argument("--window",type=int,default=7)
    a=ap.parse_args()
    rows=load_rows(a.csv)
    dcol=next((h for h in rows[0] if h.lower() in ("date","날짜","일자","day")),None)
    s=sorted(((r[dcol].strip(),num(r.get(a.metric))) for r in rows),key=lambda x:x[0])
    days=[d for d,_ in s]; v=[x for _,x in s]; n=len(v)
    if n<5: print("데이터 부족"); return
    # 1) trend: centered moving median
    w=a.window; half=w//2
    trend=[]
    for i in range(n):
        lo=max(0,i-half); hi=min(n,i+half+1); trend.append(median(v[lo:hi]))
    detr=[v[i]-trend[i] for i in range(n)]
    # 2) weekday seasonal (median per weekday on detrended)
    wd=[datetime.strptime(d,"%Y-%m-%d").weekday() for d in days]
    seas_map={}
    for k_ in set(wd):
        seas_map[k_]=median([detr[i] for i in range(n) if wd[i]==k_])
    resid=[detr[i]-seas_map[wd[i]] for i in range(n)]
    # 3) robust z on residual
    med=median(resid); mad=median([abs(r-med) for r in resid]) or 1e-9
    anomalies=[(days[i],v[i],0.6745*(resid[i]-med)/mad) for i in range(n) if abs(0.6745*(resid[i]-med)/mad)>=a.k]
    print(f"\n=== TS ANOMALY ({a.metric}, k={a.k}, window={w}) ===")
    print(f"기간 {days[0]}..{days[-1]} ({n}일) · 추세·요일 제거 후 잔차 MAD={mad:,.0f}")
    print(f"이상치 {len(anomalies)}건:")
    for d,val,z in anomalies: print(f"  ⚠️ {d}: {val:,.0f}  (robust z={z:+.1f}) → 원자료/타임존/중복 점검")
    if not anomalies: print("  (없음)")
if __name__=="__main__": main()
