"""
주간 롤업 — 일별 CSV를 ISO 주 단위로 집계하고 WoW(주간대비) 증감 산출. 가중지표 정확.

입력 CSV: date + impressions,clicks,spend,conversions,revenue
Usage: python weekly_rollup.py daily.csv
"""
import argparse, csv
from datetime import datetime
from pathlib import Path
from collections import defaultdict
RAWM=["impressions","clicks","spend","conversions","revenue"]
def num(s):
    s=str(s or "").replace(",","").replace("₩","").strip()
    try: return float(s)
    except: return 0.0
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("csv"); a=ap.parse_args()
    rows=list(csv.DictReader(Path(a.csv).read_text(encoding="utf-8").splitlines()))
    dcol=next((h for h in rows[0] if h.lower() in ("date","날짜","일자","day")),None)
    h={c.lower():c for c in rows[0]}
    wk=defaultdict(lambda:{m:0.0 for m in RAWM})
    for r in rows:
        try: d=datetime.strptime(r[dcol].strip(),"%Y-%m-%d")
        except: continue
        iso=d.isocalendar(); key=f"{iso[0]}-W{iso[1]:02d}"
        for m in RAWM:
            c=h.get(m)
            if c: wk[key][m]+=num(r.get(c))
    weeks=sorted(wk)
    print(f"\n=== WEEKLY ROLLUP ({len(weeks)} weeks) ===")
    print("week".ljust(10)+"spend".rjust(14)+"conv".rjust(9)+"revenue".rjust(15)+"ROAS".rjust(7)+"  WoW매출")
    prev=None
    for w in weeks:
        v=wk[w]; roas=v["revenue"]/v["spend"] if v["spend"] else 0
        wow=f"{(v['revenue']/prev-1):+.1%}" if (prev and prev>0) else "—"
        print(f"{w.ljust(10)}{v['spend']:>14,.0f}{v['conversions']:>9,.0f}{v['revenue']:>15,.0f}{roas:>6.2f}x{wow:>9}")
        prev=v["revenue"]
    print("  · ISO주 집계·가중 ROAS. WoW로 추세 진단.")
if __name__=="__main__": main()
