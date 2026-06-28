"""
일원배치 ANOVA — 3개 이상 그룹 평균 차이의 유의성(F-검정). 예: 여러 변형의 지표 비교.
F = MSB/MSW, MSB=SSB/(k−1), MSW=SSW/(N−k). 계산 정확. (임계 F는 표 참조 안내.)

입력 CSV: group, value  (long format)
Usage: python anova.py data.csv
"""
import argparse, csv
from pathlib import Path
from collections import defaultdict
def num(s):
    s=str(s or "").replace(",","").strip()
    try: return float(s)
    except: return None
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("csv"); a=ap.parse_args()
    rows=list(csv.DictReader(Path(a.csv).read_text(encoding="utf-8").splitlines()))
    h={c.lower():c for c in rows[0]}; gc=h.get("group") or list(rows[0])[0]; vc=h.get("value") or list(rows[0])[1]
    groups=defaultdict(list)
    for r in rows:
        v=num(r.get(vc))
        if v is not None: groups[(r.get(gc) or "").strip()].append(v)
    k=len(groups); N=sum(len(v) for v in groups.values())
    if k<2 or N<=k: print("그룹/표본 부족"); return
    allv=[x for v in groups.values() for x in v]; grand=sum(allv)/N
    ssb=sum(len(v)*(sum(v)/len(v)-grand)**2 for v in groups.values())
    ssw=sum((x-sum(v)/len(v))**2 for v in groups.values() for x in v)
    dfb=k-1; dfw=N-k
    msb=ssb/dfb; msw=ssw/dfw if dfw else 0
    F=msb/msw if msw else float('inf')
    print(f"\n=== ONE-WAY ANOVA (k={k} groups, N={N}) ===")
    for g,v in groups.items(): print(f"  {g.ljust(12)} n={len(v)} 평균={sum(v)/len(v):,.2f}")
    print(f"\nSSB={ssb:,.2f} (df {dfb}) · SSW={ssw:,.2f} (df {dfw})")
    print(f"F = {F:.3f}")
    crit={(2,'~'):3.0}  # 안내용
    print(f"  · F가 임계값(F표, α=0.05, df1={dfb},df2={dfw}) 초과면 그룹 간 평균차 유의. 사후검정으로 쌍별 비교.")
if __name__=="__main__": main()
