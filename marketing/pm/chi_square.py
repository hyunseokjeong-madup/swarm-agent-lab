"""
카이제곱 독립성 검정 — 분할표(예: 기기×전환)에서 두 범주변수의 연관성. chi²=Σ(O−E)²/E,
E=행합×열합/총합, df=(r−1)(c−1). 계산 정확. 임계 3.841(df1,95%) 등 안내.

입력 CSV: 첫 열=행 라벨, 나머지 열=각 결과 빈도 (예: device, converted, not_converted)
Usage: python chi_square.py table.csv
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
    cols=list(rows[0].keys()); rlab=cols[0]; ccols=cols[1:]
    M=[[num(r.get(c)) for c in ccols] for r in rows]; labels=[r.get(rlab) for r in rows]
    R=len(M); C=len(ccols)
    rt=[sum(M[i]) for i in range(R)]; ct=[sum(M[i][j] for i in range(R)) for j in range(C)]; G=sum(rt)
    chi=0
    for i in range(R):
        for j in range(C):
            E=rt[i]*ct[j]/G if G else 0
            if E>0: chi+=(M[i][j]-E)**2/E
    df=(R-1)*(C-1)
    crit={1:3.841,2:5.991,3:7.815,4:9.488}.get(df,None)
    print(f"\n=== CHI-SQUARE INDEPENDENCE ({R}×{C}) ===")
    for i in range(R): print(f"  {str(labels[i]).ljust(12)} " + " ".join(f"{M[i][j]:,.0f}" for j in range(C)) + f"  (행합 {rt[i]:,.0f})")
    print(f"\nchi² = {chi:.3f} · df = {df}" + (f" · 임계 {crit} @95%" if crit else ""))
    if crit:
        print("🔴 연관 있음(독립 기각)" if chi>crit else "🟢 독립(연관 근거 부족)")
    print("  · 유의하면 범주 간 연관 존재(예: 기기별 전환율 차이). 효과크기도 함께 보기.")
if __name__=="__main__": main()
