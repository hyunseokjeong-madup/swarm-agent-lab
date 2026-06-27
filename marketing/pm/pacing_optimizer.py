"""
페이싱 최적화 — 잔여 예산을 남은 일자에 가중치(요일/시즌)대로 재분배해 일별 목표 산출.
가중 없으면 균등. 일일 상한(--max-daily) 초과 시 경고. 배분 산술 정확.

Usage: python pacing_optimizer.py --budget 30000000 --spent 12000000 --remaining-days 6 \
        [--weights 1,1,1,1,1.3,1.2] [--max-daily 4000000]
"""
import argparse
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--budget",type=float,required=True); ap.add_argument("--spent",type=float,default=0)
    ap.add_argument("--remaining-days",type=int,required=True)
    ap.add_argument("--weights",default=None); ap.add_argument("--max-daily",type=float,default=None)
    a=ap.parse_args()
    rem=a.budget-a.spent; nd=a.remaining_days
    if a.weights:
        w=[float(x) for x in a.weights.split(",")]
        if len(w)!=nd: w=(w*nd)[:nd]
    else: w=[1.0]*nd
    sw=sum(w) or 1
    plan=[rem*wi/sw for wi in w]
    print(f"\n=== PACING OPTIMIZER ===")
    print(f"예산 {a.budget:,.0f} · 소진 {a.spent:,.0f} · 잔여 {rem:,.0f} · 남은 {nd}일")
    over=0
    for i,(wi,p) in enumerate(zip(w,plan),1):
        flag=""
        if a.max_daily and p>a.max_daily: flag=" ⚠️ 상한초과"; over+=1
        print(f"  Day {i} (w={wi:g}): {p:,.0f}{flag}")
    print(f"합계 {sum(plan):,.0f} (=잔여예산)")
    if over: print(f"  ⚠️ {over}일이 일일상한 초과 → 기간 연장 또는 상한 상향 검토")
    print(f"  · 균등 대비 가중 배분으로 성과 요일에 집중. 정확 배분(합=잔여).")
if __name__=="__main__": main()
