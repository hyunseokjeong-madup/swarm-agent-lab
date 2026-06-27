"""
ROAS 목표 갭 — 채널별 실제 ROAS vs 목표. 미달 채널의 매출 부족분(목표달성 필요 추가매출) 집계.
부족분 = max(0, spend×목표ROAS − revenue). 계산 정확.

입력 CSV: channel, spend, revenue
Usage: python roas_gap.py data.csv --target 3.0
"""
import argparse, csv, re
from pathlib import Path
def num(s):
    s=str(s or "").replace(",","").replace("₩","").strip()
    try: return float(s)
    except: return 0.0
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("csv"); ap.add_argument("--target",type=float,required=True); ap.add_argument("--by",default=None)
    a=ap.parse_args()
    rows=list(csv.DictReader(Path(a.csv).read_text(encoding="utf-8").splitlines()))
    by=a.by or list(rows[0])[0]; h={c.lower():c for c in rows[0]}
    sc,rc=h.get("spend"),h.get("revenue")
    agg={}
    for r in rows:
        if re.search(r"total|합계|총계",(r.get(by) or ""),re.I): continue
        k=(r.get(by) or "").strip(); agg.setdefault(k,[0.0,0.0])
        agg[k][0]+=num(r.get(sc)); agg[k][1]+=num(r.get(rc))
    print(f"\n=== ROAS GAP (목표 {a.target}x) ===")
    print("channel".ljust(14)+"ROAS".rjust(8)+"갭".rjust(8)+"매출부족분".rjust(15))
    tot_gap=0
    for k,(sp,rv) in sorted(agg.items(),key=lambda x:(x[1][1]/x[1][0] if x[1][0] else 0)):
        roas=rv/sp if sp else 0; short=max(0,sp*a.target-rv); tot_gap+=short
        tag="🔴" if roas<a.target else "🟢"
        print(f"{k.ljust(14)}{roas:>7.2f}x{(roas-a.target):>+7.2f}{short:>15,.0f} {tag}")
    print(f"\n총 매출 부족분 {tot_gap:,.0f} (목표 ROAS 달성에 필요한 추가매출). 미달 채널 소재/타깃 개선·재배분.")
if __name__=="__main__": main()
