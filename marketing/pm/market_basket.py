"""
시장바구니 분석 — 연관규칙(support/confidence/lift). 함께 구매되는 품목쌍 발굴(번들·교차판매).
support(A,B)=둘다 든 바구니/전체, confidence(A→B)=supp(A,B)/supp(A), lift=conf/supp(B). 계산 정확.

입력 CSV: transaction_id, item  (long format; 한 행 = 한 품목)
Usage: python market_basket.py baskets.csv --min-support 0.1 --top 10
"""
import argparse, csv
from pathlib import Path
from collections import defaultdict
from itertools import combinations
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("csv")
    ap.add_argument("--min-support",type=float,default=0.1); ap.add_argument("--top",type=int,default=10)
    a=ap.parse_args()
    rows=list(csv.DictReader(Path(a.csv).read_text(encoding="utf-8").splitlines()))
    tcol,icol=list(rows[0])[0],list(rows[0])[1]
    baskets=defaultdict(set)
    for r in rows: baskets[r[tcol].strip()].add(r[icol].strip())
    N=len(baskets)
    item_ct=defaultdict(int); pair_ct=defaultdict(int)
    for items in baskets.values():
        for it in items: item_ct[it]+=1
        for x,y in combinations(sorted(items),2): pair_ct[(x,y)]+=1
    rules=[]
    for (x,y),c in pair_ct.items():
        s=c/N
        if s<a.min_support: continue
        sx=item_ct[x]/N; sy=item_ct[y]/N
        # both directions
        rules.append((x,y,s,c/item_ct[x],s/(sx*sy)))
        rules.append((y,x,s,c/item_ct[y],s/(sx*sy)))
    rules.sort(key=lambda r:-r[4])
    print(f"\n=== MARKET BASKET ({N} baskets) ===")
    print("rule".ljust(28)+"support".rjust(9)+"conf".rjust(8)+"lift".rjust(8))
    for x,y,s,conf,lift in rules[:a.top]:
        print(f"{(x+' → '+y).ljust(28)}{s:>8.1%}{conf:>8.1%}{lift:>7.2f}x")
    print("  · lift>1 = 양의 연관(번들/교차판매 후보). conf=A 구매시 B 동반 비율.")
if __name__=="__main__": main()
