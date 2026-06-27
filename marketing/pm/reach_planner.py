"""
도달 플래너 — 예산·CPM·모수에서 노출/도달/빈도 추정(미디어 플래닝).
노출 = 예산/CPM×1000. 도달 ≈ 모수×(1−e^(−노출/모수)) (무작위 전달 가정). 빈도 = 노출/도달. 계산 정확(모델 추정).

Usage: python reach_planner.py --budget 10000000 --cpm 5000 --audience 1000000
"""
import argparse, math
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--budget",type=float,required=True); ap.add_argument("--cpm",type=float,required=True)
    ap.add_argument("--audience",type=float,required=True)
    a=ap.parse_args()
    impr=a.budget/a.cpm*1000
    reach=a.audience*(1-math.exp(-impr/a.audience))
    freq=impr/reach if reach else 0
    print(f"\n=== REACH PLANNER ===")
    print(f"예산 {a.budget:,.0f} · CPM {a.cpm:,.0f} · 모수 {a.audience:,.0f}")
    print(f"예상 노출 = {impr:,.0f}")
    print(f"예상 도달 = {reach:,.0f} (모수의 {reach/a.audience:.1%})")
    print(f"예상 빈도 = {freq:.2f}")
    if freq>3: print("  ⚠️ 빈도 과다(피로 위험) → 모수 확대 또는 예산 분산")
    elif freq<1.5: print("  ℹ️ 빈도 낮음 → 인지 강화 위해 빈도 확보 검토")
    else: print("  🟢 빈도 적정 범위")
    print("  · 무작위 전달 가정 추정. 실제는 타게팅·중복으로 달라짐.")
if __name__=="__main__": main()
