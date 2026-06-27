"""
이탈위험 스코어 — 최근성 대비 기대 구매주기로 위험 산출.
기대주기 = 관측기간/빈도. 위험비 = 최근성(미구매일)/기대주기. >1.5 경고. 계산 정확(해석가능).

입력 CSV: customer_id, date(YYYY-MM-DD), amount
Usage: python churn_score.py tx.csv [--asof 2026-01-31] [--threshold 1.5]
"""
import argparse, csv
from datetime import datetime
from pathlib import Path
from collections import defaultdict
def num(s):
    s=str(s or "").replace(",","").strip()
    try: return float(s)
    except: return 0.0
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("csv")
    ap.add_argument("--asof",default=None); ap.add_argument("--threshold",type=float,default=1.5)
    a=ap.parse_args()
    rows=list(csv.DictReader(Path(a.csv).read_text(encoding="utf-8").splitlines()))
    h={c.lower():c for c in rows[0]}; cid=h.get("customer_id") or list(rows[0])[0]; dc=h.get("date")
    tx=defaultdict(list)
    for r in rows: tx[r[cid].strip()].append(datetime.strptime(r.get(dc).strip(),"%Y-%m-%d"))
    asof=datetime.strptime(a.asof,"%Y-%m-%d") if a.asof else max(d for v in tx.values() for d in v)
    res=[]
    for c,ds in tx.items():
        ds=sorted(ds); first=ds[0]; last=ds[-1]; freq=len(ds)
        span=max((last-first).days,1)
        expected=span/max(freq-1,1) if freq>1 else span  # 평균 구매간격
        recency=(asof-last).days
        risk=recency/expected if expected else 0
        res.append((c,freq,recency,expected,risk))
    res.sort(key=lambda x:-x[4])
    atrisk=[r for r in res if r[4]>=a.threshold]
    print(f"\n=== CHURN RISK ({len(tx)} customers, asof {asof.date()}, thr {a.threshold}) ===")
    print("customer".ljust(10)+"freq".rjust(6)+"recency".rjust(9)+"기대주기".rjust(10)+"위험비".rjust(8))
    for c,f,rec,exp,risk in res:
        tag=" ⚠️" if risk>=a.threshold else ""
        print(f"{c.ljust(10)}{f:>6}{rec:>9}{exp:>10.0f}{risk:>8.2f}{tag}")
    print(f"\n이탈위험 {len(atrisk)}명 (위험비≥{a.threshold}) → 윈백 캠페인 대상")
if __name__=="__main__": main()
