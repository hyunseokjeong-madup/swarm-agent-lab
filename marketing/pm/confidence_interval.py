"""
Wilson 신뢰구간 — 비율(전환율 등)의 정확한 CI. 소표본·극단비율에서 정규근사보다 정확.
center=(p+z²/2n)/(1+z²/n), half=z·√(p(1-p)/n+z²/4n²)/(1+z²/n). 계산 정확.

Usage: python confidence_interval.py --conv 50 --n 1000 [--z 1.96]
"""
import argparse, math
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--conv",type=int,required=True); ap.add_argument("--n",type=int,required=True); ap.add_argument("--z",type=float,default=1.96)
    a=ap.parse_args()
    p=a.conv/a.n; z=a.z; n=a.n
    denom=1+z*z/n
    center=(p+z*z/(2*n))/denom
    half=z*math.sqrt(p*(1-p)/n + z*z/(4*n*n))/denom
    lo,hi=center-half,center+half
    # 정규근사 비교
    nlo,nhi=p-z*math.sqrt(p*(1-p)/n), p+z*math.sqrt(p*(1-p)/n)
    lvl={1.96:"95%",2.576:"99%",1.645:"90%"}.get(round(z,3),f"z={z}")
    print(f"\n=== CONFIDENCE INTERVAL (Wilson, {lvl}) ===")
    print(f"비율 p = {p:.4%} ({a.conv}/{a.n})")
    print(f"Wilson CI : [{lo:.4%}, {hi:.4%}]  (폭 {hi-lo:.4%})")
    print(f"정규근사  : [{nlo:.4%}, {nhi:.4%}]  (소표본·극단에서 부정확)")
    print("  · Wilson은 0/1 경계·소표본에서 더 신뢰. 보고에 CI 동반 권장.")
if __name__=="__main__": main()
