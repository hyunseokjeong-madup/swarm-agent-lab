"""
입찰 시뮬레이터 — 입찰 랜드스케이프(CPC→클릭량)에서 이익 최대 입찰 탐색.
각 입찰: conv=clicks*cvr, revenue=conv*value, cost=clicks*cpc, profit=revenue-cost. 계산 정확.

입력 CSV: cpc, clicks
Usage: python bid_sim.py landscape.csv --value 50000 --cvr 0.05
"""
import argparse, csv
from pathlib import Path
from _pmutil import load_rows  # 빈 데이터 우아한 처리
def num(s):
    s=str(s or "").replace(",","").strip()
    try: return float(s)
    except: return 0.0
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("csv")
    ap.add_argument("--value",type=float,required=True,help="전환당 매출"); ap.add_argument("--cvr",type=float,required=True)
    a=ap.parse_args()
    rows=load_rows(a.csv)
    best=None; out=[]
    print(f"\n=== BID SIMULATOR (value/conv={a.value:,.0f}, cvr={a.cvr:.1%}) ===")
    print("cpc".rjust(8)+"clicks".rjust(9)+"conv".rjust(8)+"revenue".rjust(13)+"cost".rjust(13)+"profit".rjust(13)+"roas".rjust(7))
    for r in rows:
        cpc=num(r.get("cpc")); clk=num(r.get("clicks"))
        conv=clk*a.cvr; rev=conv*a.value; cost=clk*cpc; profit=rev-cost; roas=rev/cost if cost else 0
        print(f"{cpc:>8,.0f}{clk:>9,.0f}{conv:>8,.0f}{rev:>13,.0f}{cost:>13,.0f}{profit:>13,.0f}{roas:>6.2f}x")
        if best is None or profit>best[1]: best=(cpc,profit,roas)
    print(f"\n최적 입찰 CPC={best[0]:,.0f}  (이익 {best[1]:,.0f}, ROAS {best[2]:.2f}x)")
    print(f"  · 손익분기 CPC = value×cvr = {a.value*a.cvr:,.0f} (이보다 낮아야 흑자). 랜드스케이프는 추정.")
if __name__=="__main__": main()
