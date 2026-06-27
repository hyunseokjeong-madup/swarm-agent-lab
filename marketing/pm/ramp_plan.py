"""
예산 램프 플랜 — 학습 리셋 없이 일일 최대 증액률(기본 20%)로 현재→목표 일예산 점진 증액 계획.
필요일수 = ceil(log(target/current)/log(1+step)). 일자별 예산 산출(정확).

Usage: python ramp_plan.py --current-daily 1000000 --target-daily 3000000 [--step 0.2]
"""
import argparse, math
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--current-daily",type=float,required=True); ap.add_argument("--target-daily",type=float,required=True)
    ap.add_argument("--step",type=float,default=0.2)
    a=ap.parse_args()
    if a.target_daily<=a.current_daily:
        print("목표가 현재 이하 — 즉시 가능(감액은 자유)."); return
    days=math.ceil(math.log(a.target_daily/a.current_daily)/math.log(1+a.step))
    print(f"\n=== BUDGET RAMP PLAN (max +{a.step:.0%}/day) ===")
    print(f"현재 일예산 {a.current_daily:,.0f} → 목표 {a.target_daily:,.0f}  ({a.target_daily/a.current_daily:.1f}배)")
    print(f"안전 도달 {days}일 (학습기 리셋 방지):")
    cur=a.current_daily
    for d in range(1,days+1):
        cur=min(cur*(1+a.step),a.target_daily)
        print(f"  Day {d}: {cur:,.0f}")
    print("  · 급격한 증액은 알고리즘 재학습·CPA 급등 유발. 점진 증액 권장.")
if __name__=="__main__": main()
