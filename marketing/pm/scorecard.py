"""
가중 점수카드 — 여러 지표를 0~1 정규화(min-max) 후 가중합으로 종합 순위.
lower-better 지표(cpa,cpc,cpm)는 역방향 정규화. 계산 정확.

입력 CSV: name(첫 열) + 지표 컬럼들
Usage: python scorecard.py data.csv --weights roas:0.5,ctr:0.3,conversions:0.2
"""
import argparse, csv, re
from pathlib import Path
from _pmutil import load_rows  # 빈 데이터 우아한 처리
LOWER={"cpa","cpc","cpm","cpi","cpl"}
def num(s):
    s=str(s or "").replace(",","").replace("₩","").replace("%","").replace("x","").strip()
    try: return float(s)
    except: return None
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("csv"); ap.add_argument("--weights",required=True)
    a=ap.parse_args()
    W={}
    for part in a.weights.split(","):
        k,v=part.split(":"); W[k.strip().lower()]=float(v)
    rows=load_rows(a.csv)
    name=list(rows[0])[0]; colmap={c.lower():c for c in rows[0]}
    ents=[r for r in rows if not re.search(r"total|합계|총계",(r.get(name) or ""),re.I)]
    # gather values per metric
    vals={m:[] for m in W}
    for m in W:
        col=colmap.get(m)
        for r in ents: vals[m].append(num(r.get(col)) if col else None)
    # normalize
    norm={}
    for m in W:
        xs=[x for x in vals[m] if x is not None]
        lo,hi=(min(xs),max(xs)) if xs else (0,1); rng=hi-lo or 1
        norm[m]=[]
        for x in vals[m]:
            if x is None: norm[m].append(0.5); continue
            z=(x-lo)/rng
            norm[m].append(1-z if m in LOWER else z)
    tw=sum(W.values()) or 1
    scores=[]
    for i,r in enumerate(ents):
        s=sum(W[m]*norm[m][i] for m in W)/tw
        scores.append(((r.get(name) or "").strip(),s))
    scores.sort(key=lambda x:-x[1])
    print(f"\n=== SCORECARD (weights {a.weights}) ===")
    for rank,(nm,s) in enumerate(scores,1):
        bar="█"*int(s*20); print(f"{rank:>2} {nm.ljust(16)} {s:.3f} {bar}")
    print("  · min-max 정규화·가중합. lower-better(cpa 등) 자동 역방향.")
if __name__=="__main__": main()
