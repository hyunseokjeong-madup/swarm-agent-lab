"""
미디어믹스 간이 회귀(MMM) — OLS로 채널별 매출 기여 계수 추정.
revenue ~ b0 + b1*spend_ch1 + ... (정규방정식 (X'X)^-1 X'y, 가우스 소거로 정확 해).
* 선형대수 계산은 정확. 계수는 모델 '추정'(인과 아님; 다중공선성·시차 주의).

입력 CSV: 각 채널 지출 컬럼들 + revenue 컬럼.
Usage: python mmm.py data.csv --channels meta,google,naver --target revenue
"""
import argparse, csv
from pathlib import Path
from _pmutil import load_rows  # 빈 데이터 우아한 처리

def num(s):
    s=str(s or "").replace(",","").replace("₩","").replace("%","").strip()
    try: return float(s)
    except: return 0.0

def solve(A, b):  # Gaussian elimination, returns x for A x = b
    n=len(A); M=[row[:]+[b[i]] for i,row in enumerate(A)]
    for c in range(n):
        piv=max(range(c,n), key=lambda r:abs(M[r][c]))
        M[c],M[piv]=M[piv],M[c]
        if abs(M[c][c])<1e-12: M[c][c]=1e-12
        for r in range(n):
            if r!=c:
                f=M[r][c]/M[c][c]
                for k in range(c,n+1): M[r][k]-=f*M[c][k]
    return [M[i][n]/M[i][i] for i in range(n)]

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("csv"); ap.add_argument("--channels",required=True); ap.add_argument("--target",default="revenue")
    a=ap.parse_args()
    chs=a.channels.split(",")
    rows=load_rows(a.csv)
    X=[]; y=[]
    for r in rows:
        X.append([1.0]+[num(r.get(c)) for c in chs]); y.append(num(r.get(a.target)))
    k=len(chs)+1
    # normal equations: (X'X) b = X'y
    XtX=[[sum(X[m][i]*X[m][j] for m in range(len(X))) for j in range(k)] for i in range(k)]
    Xty=[sum(X[m][i]*y[m] for m in range(len(X))) for i in range(k)]
    b=solve(XtX,Xty)
    # R^2
    ybar=sum(y)/len(y);
    pred=[sum(b[i]*X[m][i] for i in range(k)) for m in range(len(X))]
    ss_res=sum((y[m]-pred[m])**2 for m in range(len(y))); ss_tot=sum((v-ybar)**2 for v in y) or 1e-9
    r2=1-ss_res/ss_tot
    print(f"\n=== MMM (OLS, n={len(X)}) ===")
    print(f"intercept b0 = {b[0]:,.2f}")
    for i,c in enumerate(chs): print(f"  {c}: 계수 {b[i+1]:.4f}  (지출 1단위당 매출 기여 추정)")
    print(f"R^2 = {r2:.4f}")
    print("  * 추정치(상관 기반). 인과·증분은 holdout/MMM 정식 모델로 검증. 다중공선성 주의.")

if __name__=="__main__": main()
