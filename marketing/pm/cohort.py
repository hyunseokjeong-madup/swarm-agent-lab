"""
코호트 리텐션 + LTV 곡선.
입력 CSV: cohort, period(0,1,2,...), active_users[, revenue]
- period0 대비 잔존율 행렬, 코호트 평균 리텐션 곡선, 1인당 누적매출(LTV) 곡선 산출.
계산은 정확(잔존율=active/active0, LTV=Σrevenue/users0).

Usage: python cohort.py cohorts.csv [--md out.md]
"""
import argparse, csv, re
from pathlib import Path
from _pmutil import load_rows  # 빈 데이터 우아한 처리
from collections import defaultdict

def num(s):
    s=str(s or "").replace(",","").strip()
    try: return float(s)
    except: return 0.0

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("csv"); ap.add_argument("--md",default=None)
    a=ap.parse_args()
    rows=load_rows(a.csv)
    h={c.lower():c for c in rows[0]}
    cc=h.get("cohort") or list(rows[0])[0]
    pc=h.get("period") or h.get("month") or h.get("day")
    uc=h.get("active_users") or h.get("users") or h.get("active")
    rc=h.get("revenue") or h.get("value")
    data=defaultdict(dict); rev=defaultdict(dict)
    for r in rows:
        co=r[cc].strip(); pr=int(num(r.get(pc)))
        data[co][pr]=num(r.get(uc));
        if rc: rev[co][pr]=num(r.get(rc))
    periods=sorted({p for co in data for p in data[co]})
    print(f"\n=== COHORT RETENTION ({len(data)} cohorts) ===")
    print("cohort".ljust(12)+"".join(f"P{p}".rjust(8) for p in periods))
    # retention matrix
    ret_acc=defaultdict(list)
    for co in sorted(data):
        base=data[co].get(0,0)
        line=co.ljust(12)
        for p in periods:
            if p in data[co] and base:
                r=data[co][p]/base; ret_acc[p].append(r); line+=f"{r*100:>7.0f}%"
            else: line+="    -   "
        print(line)
    print("\n평균 리텐션 곡선:")
    print("  "+"  ".join(f"P{p}:{(sum(ret_acc[p])/len(ret_acc[p])*100):.0f}%" for p in periods if ret_acc[p]))
    # LTV curve (per period0 user, cumulative)
    if rc:
        print("\n누적 LTV(1인당, 코호트 평균):")
        ltv=[]
        for p in periods:
            vals=[]
            for co in data:
                base=data[co].get(0,0)
                if base: vals.append(sum(rev[co].get(q,0) for q in periods if q<=p)/base)
            if vals: ltv.append((p,sum(vals)/len(vals)))
        print("  "+"  ".join(f"P{p}:{v:,.0f}" for p,v in ltv))
    if a.md:
        L=[f"# Cohort — `{Path(a.csv).name}`","","| cohort | "+" | ".join(f"P{p}" for p in periods)+" |","|"+"---|"*(len(periods)+1)]
        for co in sorted(data):
            base=data[co].get(0,0)
            L.append("| "+co+" | "+" | ".join((f"{data[co][p]/base*100:.0f}%" if (p in data[co] and base) else "-") for p in periods)+" |")
        Path(a.md).write_text("\n".join(L)+"\n",encoding="utf-8")
if __name__=="__main__": main()
