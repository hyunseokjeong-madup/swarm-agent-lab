"""
가격탄력성 추정 — log(수량) = a + e·log(가격)의 OLS 기울기 e가 탄력성.
|e|>1 탄력적(가격↓→매출↑), |e|<1 비탄력적. 회귀 계산 정확. * 외생요인 통제 가정.

입력 CSV: price, quantity(또는 units)
Usage: python price_elasticity.py pq.csv
"""
import argparse, csv, math
from pathlib import Path
def num(s):
    s=str(s or "").replace(",","").strip()
    try: return float(s)
    except: return 0.0
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("csv"); a=ap.parse_args()
    rows=list(csv.DictReader(Path(a.csv).read_text(encoding="utf-8").splitlines()))
    h={c.lower():c for c in rows[0]}
    pc=h.get("price"); qc=h.get("quantity") or h.get("units") or h.get("qty")
    xs=[]; ys=[]
    for r in rows:
        p=num(r.get(pc)); q=num(r.get(qc))
        if p>0 and q>0: xs.append(math.log(p)); ys.append(math.log(q))
    n=len(xs)
    if n<2: print("데이터 부족"); return
    mx=sum(xs)/n; my=sum(ys)/n
    sxx=sum((x-mx)**2 for x in xs); sxy=sum((xs[i]-mx)*(ys[i]-my) for i in range(n))
    e=sxy/sxx if sxx else 0; a0=my-e*mx
    # R^2
    pred=[a0+e*x for x in xs]; ssr=sum((ys[i]-pred[i])**2 for i in range(n)); sst=sum((y-my)**2 for y in ys) or 1e-9
    r2=1-ssr/sst
    print(f"\n=== PRICE ELASTICITY (n={n}) ===")
    print(f"탄력성 e = {e:.3f}  (R²={r2:.4f})")
    kind="탄력적(가격민감)" if abs(e)>1 else "비탄력적(가격둔감)"
    print(f"해석: {kind}. 가격 1%↑ 시 수량 {e:.2f}% 변화 추정.")
    if e<0 and abs(e)>1: print("  → 가격 인하가 매출 증대에 유리할 수 있음(마진 동시 고려).")
    print("  * 추정치(상관). 프로모션/시즌 등 교란요인 통제 필요.")
if __name__=="__main__": main()
