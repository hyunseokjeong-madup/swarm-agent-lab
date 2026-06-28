"""
Shapley 값 데이터기반 어트리뷰션 — 채널 조합(coalition) 기여를 Shapley 값으로 공정 배분.
v(S) = 채널집합이 S의 부분집합인 전환 경로 수. phi_i = Σ_S∋i [(|S|-1)!(n-|S|)!/n!]·(v(S)-v(S\i)).
정확한 조합 계산(채널 수 ≤ ~10). 합 = 총 전환수(효율성 공리).

입력 CSV: path_id, channel, converted(1/0; 경로 내 어느 행이든 1이면 전환)
Usage: python shapley_attribution.py paths.csv
"""
import argparse, csv, math
from pathlib import Path
from _pmutil import load_rows  # 빈 데이터 우아한 처리
from collections import defaultdict
from itertools import combinations
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("csv"); a=ap.parse_args()
    rows=load_rows(a.csv)
    h={c.lower():c for c in rows[0]}
    pc=h.get("path_id") or list(rows[0])[0]; cc=h.get("channel"); vc=h.get("converted")
    paths=defaultdict(lambda:[set(),0])
    for r in rows:
        p=r[pc].strip(); paths[p][0].add(r.get(cc,"").strip())
        if vc and str(r.get(vc)).strip() in ("1","1.0","true","True"): paths[p][1]=1
    universe=sorted({c for s,_ in paths.values() for c in s})
    n=len(universe); idx={c:i for i,c in enumerate(universe)}
    # v(S): converted paths whose channel-set ⊆ S. Represent S as frozenset.
    conv_sets=[frozenset(s) for s,conv in paths.values() if conv]
    def v(S):
        S=set(S); return sum(1 for cs in conv_sets if cs<=S)
    # Shapley via subset enumeration
    phi={c:0.0 for c in universe}
    from math import factorial as f
    allset=set(universe)
    # iterate all subsets S that contain i
    for c in universe:
        others=[u for u in universe if u!=c]
        for k in range(0,len(others)+1):
            for combo in combinations(others,k):
                S=set(combo)|{c}; s=len(S)
                w=f(s-1)*f(n-s)/f(n)
                phi[c]+=w*(v(S)-v(S-{c}))
    total=sum(phi.values()); conv_total=len(conv_sets)
    print(f"\n=== SHAPLEY ATTRIBUTION ({len(paths)} paths, {conv_total} conversions, {n} channels) ===")
    for c in sorted(universe,key=lambda c:-phi[c]):
        print(f"  {c.ljust(12)} {phi[c]:>8.2f}  ({phi[c]/conv_total*100 if conv_total else 0:>5.1f}%)")
    print(f"합 {total:.2f} (= 전환수 {conv_total}, 효율성 공리 충족)")
    print("  · 공정한 한계기여 배분. 채널 수 많으면 근사(샘플링) 필요.")
if __name__=="__main__": main()
