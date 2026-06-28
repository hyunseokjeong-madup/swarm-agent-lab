"""
회귀/예측 잔차 진단 — 잔차(actual−pred)의 편향·표준편차·Durbin-Watson 자기상관.
DW≈2 무상관, <2 양의 자기상관(추세 미반영), >2 음의 자기상관. 계산 정확.

입력 CSV: actual, predicted (또는 a/f)
Usage: python regression_residuals.py af.csv
"""
import argparse, csv, math
from pathlib import Path
def num(s):
    s=str(s or "").replace(",","").strip()
    try: return float(s)
    except: return None
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("csv"); a=ap.parse_args()
    rows=list(csv.DictReader(Path(a.csv).read_text(encoding="utf-8").splitlines()))
    h={c.lower():c for c in rows[0]}; ac=h.get("actual") or h.get("a"); fc=h.get("predicted") or h.get("forecast") or h.get("f")
    res=[]
    for r in rows:
        x=num(r.get(ac)); y=num(r.get(fc))
        if x is not None and y is not None: res.append(x-y)
    n=len(res)
    if n<3: print("데이터 부족"); return
    mean=sum(res)/n
    sd=math.sqrt(sum((e-mean)**2 for e in res)/n)
    dw=sum((res[i]-res[i-1])**2 for i in range(1,n))/(sum(e*e for e in res) or 1e-9)
    print(f"\n=== RESIDUAL DIAGNOSTICS (n={n}) ===")
    print(f"평균 잔차(bias) = {mean:+,.2f}  ({'과소예측' if mean>0 else '과대예측' if mean<0 else '무편향'})")
    print(f"잔차 표준편차 = {sd:,.2f}")
    print(f"Durbin-Watson = {dw:.3f}")
    if dw<1.5: print("  ⚠️ 양의 자기상관 — 모델이 추세/계절을 못 잡음(체계적 패턴 잔존). 항 추가 검토.")
    elif dw>2.5: print("  ⚠️ 음의 자기상관 — 과도 보정 가능성.")
    else: print("  🟢 자기상관 미미 — 잔차 무작위(양호).")
if __name__=="__main__": main()
