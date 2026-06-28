"""
검색어 클러스터링 — 공통 토큰으로 검색어를 묶고 클러스터별 성과 집계.
각 검색어는 '가장 흔한 공유 토큰'으로 클러스터 배정(문서빈도 최대 토큰). 집계는 정확.

입력 CSV: term(첫 열), spend, clicks, conversions[, revenue]
Usage: python cluster_terms.py terms.csv
"""
import argparse, csv, re
from pathlib import Path
from _pmutil import load_rows  # 빈 데이터 우아한 처리
from collections import defaultdict, Counter
def num(s):
    s=str(s or "").replace(",","").replace("₩","").strip()
    try: return float(s)
    except: return 0.0
STOP={"의","공식","및","the","a","for","에","를","을","이","가"}
def tokens(t):
    return [w for w in re.split(r"\s+", t.strip().lower()) if len(w)>=2 and w not in STOP]
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("csv"); a=ap.parse_args()
    rows=load_rows(a.csv)
    h={c.lower():c for c in rows[0]}; tc=list(rows[0])[0]
    sc,cc,vc,rc=h.get("spend"),h.get("clicks"),h.get("conversions"),h.get("revenue")
    df=Counter()
    for r in rows:
        for w in set(tokens(r[tc])): df[w]+=1
    clusters=defaultdict(lambda:[0.0,0.0,0.0,0.0,[]])
    for r in rows:
        toks=tokens(r[tc])
        key=max(toks,key=lambda w:df[w]) if toks else "(기타)"
        c=clusters[key]
        c[0]+=num(r.get(sc)); c[1]+=num(r.get(cc)); c[2]+=num(r.get(vc)); c[3]+=num(r.get(rc)); c[4].append(r[tc])
    print(f"\n=== SEARCH-TERM CLUSTERS ({len(rows)} terms → {len(clusters)} clusters) ===")
    print("cluster".ljust(12)+"terms".rjust(6)+"spend".rjust(12)+"conv".rjust(7)+"CPA".rjust(10)+"  examples")
    for k,(sp,ck,cv,rv,ex) in sorted(clusters.items(),key=lambda x:-x[1][0]):
        cpa=sp/cv if cv else 0
        print(f"{k.ljust(12)}{len(ex):>6}{sp:>12,.0f}{cv:>7,.0f}{cpa:>10,.0f}  {', '.join(ex[:2])}")
    print("  · 클러스터 단위로 입찰/네거티브/확장 판단(개별 검색어 변동 완화).")
if __name__=="__main__": main()
