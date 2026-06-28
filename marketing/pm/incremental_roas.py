"""
한계 ROAS — 두 구간(증액 전/후)의 추가매출/추가지출. marginal ROAS=Δrevenue/Δspend.
평균 ROAS보다 낮으면 증액 효율 체감(추가 지출의 회수율 하락). 계산 정확.

입력 CSV: channel, spend_a, rev_a, spend_b, rev_b
Usage: python incremental_roas.py data.csv
"""
import argparse, csv
from pathlib import Path
def num(s):
    s=str(s or "").replace(",","").strip()
    try: return float(s)
    except: return 0.0
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("csv"); a=ap.parse_args()
    rows=list(csv.DictReader(Path(a.csv).read_text(encoding="utf-8").splitlines()))
    name=list(rows[0])[0]
    print(f"\n=== INCREMENTAL ROAS ===")
    print("channel".ljust(12)+"평균ROAS(b)".rjust(12)+"한계ROAS".rjust(11)+"  판정")
    for r in rows:
        c=(r.get(name) or "").strip()
        sa,ra,sb,rb=(num(r.get(k)) for k in ("spend_a","rev_a","spend_b","rev_b"))
        avg=rb/sb if sb else 0
        ds=sb-sa; dr=rb-ra
        if ds<=0:
            print(f"{c.ljust(12)}{avg:>11.2f}x{'—':>11}  (증액 없음)"); continue
        m=dr/ds
        verdict="🟢 한계≥평균(증액 여지)" if m>=avg else ("🔴 한계<평균(효율 체감)" if m<avg*0.8 else "🟡 비슷")
        print(f"{c.ljust(12)}{avg:>11.2f}x{m:>10.2f}x  {verdict}")
    print("  · 한계 ROAS가 목표 미만 채널은 증액 중단/재배분. 평균만 보면 한계 체감 놓침.")
if __name__=="__main__": main()
