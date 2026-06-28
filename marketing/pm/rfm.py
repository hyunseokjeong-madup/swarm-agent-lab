"""
RFM 세그멘테이션 — 거래 데이터로 Recency/Frequency/Monetary 5분위 점수화 후 세그먼트 분류.
계산 정확(분위는 동순위 안정 정렬). 세그먼트는 표준 규칙.

입력 CSV: customer_id, date(YYYY-MM-DD), amount
Usage: python rfm.py tx.csv [--asof 2026-01-31]
"""
import argparse, csv
from datetime import datetime
from pathlib import Path
from _pmutil import load_rows  # 빈 데이터 우아한 처리
from collections import defaultdict
def num(s):
    s=str(s or "").replace(",","").replace("₩","").strip()
    try: return float(s)
    except: return 0.0
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("csv"); ap.add_argument("--asof",default=None)
    a=ap.parse_args()
    rows=load_rows(a.csv)
    h={c.lower():c for c in rows[0]}
    cid=h.get("customer_id") or list(rows[0])[0]; dc=h.get("date"); ac=h.get("amount") or h.get("revenue")
    tx=defaultdict(list)
    for r in rows: tx[r[cid].strip()].append((r.get(dc,"").strip(), num(r.get(ac))))
    asof=datetime.strptime(a.asof,"%Y-%m-%d") if a.asof else max(datetime.strptime(d,"%Y-%m-%d") for v in tx.values() for d,_ in v)
    R={}; F={}; M={}
    for c,items in tx.items():
        last=max(datetime.strptime(d,"%Y-%m-%d") for d,_ in items)
        R[c]=(asof-last).days; F[c]=len(items); M[c]=sum(x for _,x in items)
    # scores: recency lower=better -> invert
    rs=sorted(R.values()); fs=sorted(F.values()); ms=sorted(M.values()); n=len(tx)
    import bisect
    def sc(sorted_vals,v,invert=False):
        r=bisect.bisect_right(sorted_vals,v)/n
        s=min(5,int(r*5)+1)
        return 6-s if invert else s
    seg_of=lambda r,f,m: ("Champions" if r>=4 and f>=4 else "Loyal" if f>=4 else "Recent" if r>=4 and f<=2 else "At Risk" if r<=2 and f>=3 else "Hibernating" if r<=2 else "Promising")
    counts=defaultdict(int); rev=defaultdict(float)
    out=[]
    for c in tx:
        r=sc(rs,R[c],invert=True); f=sc(fs,F[c]); m=sc(ms,M[c]); seg=seg_of(r,f,m)
        counts[seg]+=1; rev[seg]+=M[c]; out.append((c,R[c],F[c],M[c],r,f,m,seg))
    print(f"\n=== RFM ({n} customers, asof {asof.date()}) ===")
    print("segment".ljust(14)+"고객수".rjust(8)+"매출합".rjust(16)+"매출비중".rjust(10))
    tot=sum(rev.values()) or 1
    for s in sorted(counts,key=lambda s:-rev[s]):
        print(s.ljust(14)+f"{counts[s]:>8}"+f"{rev[s]:>16,.0f}"+f"{rev[s]/tot:>9.1%}")
    print("  · R=최근성(높을수록 최근), F=빈도, M=금액. 세그별 CRM 액션 차등.")
if __name__=="__main__": main()
