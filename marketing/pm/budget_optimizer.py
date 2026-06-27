"""
예산 최적화 — 한계수익(marginal return) 기반 채널 배분.
응답곡선 revenue = k * spend^p (0<p<1, 체감수익). 현재 (spend,revenue)로 k를 보정하고,
총예산을 작은 단위로 '현재 한계수익이 가장 큰 채널'에 그리디 배분(라그랑주 최적과 동치).
* 배분 산술은 정확. 매출은 곡선 가정에 따른 '추정'(라벨 명시). 실집행은 점진 테스트로 검증.

입력 CSV: channel, spend, revenue
Usage: python budget_optimizer.py channels.csv [--budget N] [--p 0.5] [--steps 2000]
"""
import argparse, csv, re
from pathlib import Path

def num(s):
    s=str(s or "").replace(",","").replace("₩","").replace("$","").replace("%","").strip()
    try: return float(s)
    except: return 0.0

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("csv"); ap.add_argument("--budget",type=float,default=None)
    ap.add_argument("--p",type=float,default=0.5); ap.add_argument("--steps",type=int,default=2000)
    ap.add_argument("--by",default=None)
    a=ap.parse_args()
    rows=list(csv.DictReader(Path(a.csv).read_text(encoding="utf-8").splitlines()))
    by=a.by or list(rows[0])[0]
    def find(p): return next((c for c in rows[0] if re.fullmatch(p,c,re.I)),None)
    sc,rc=find("spend|cost|비용|광고비"),find("revenue|매출|수익")
    ch={}
    for r in rows:
        if re.search(r"total|합계|총계",(r.get(by) or ""),re.I): continue
        k=(r.get(by) or "").strip(); ch.setdefault(k,[0.0,0.0])
        ch[k][0]+=num(r.get(sc)); ch[k][1]+=num(r.get(rc))
    p=a.p
    # k from current point: revenue = k*spend^p -> k = revenue/spend^p
    K={c: (rv/(sp**p) if sp>0 else 0.0) for c,(sp,rv) in ch.items()}
    cur_spend=sum(v[0] for v in ch.values())
    budget=a.budget if a.budget is not None else cur_spend
    # greedy marginal allocation: dRev/dSpend = K*p*spend^(p-1)
    alloc={c:1.0 for c in ch}  # start tiny to avoid div0
    step=budget/a.steps
    def marginal(c): return K[c]*p*(alloc[c]**(p-1)) if alloc[c]>0 else float('inf')
    remaining=budget-sum(alloc.values())
    while remaining>0:
        c=max(ch, key=marginal)
        add=min(step,remaining); alloc[c]+=add; remaining-=add
    est_rev={c: K[c]*(alloc[c]**p) for c in ch}
    cur_rev={c: ch[c][1] for c in ch}
    print(f"\n=== BUDGET OPTIMIZER (budget {budget:,.0f}, p={p}) ===")
    print("channel".ljust(14)+"현재지출".rjust(14)+"추천지출".rjust(14)+"현재매출".rjust(14)+"추정매출".rjust(14))
    for c in sorted(ch,key=lambda c:-alloc[c]):
        print(c.ljust(14)+f"{ch[c][0]:>14,.0f}"+f"{alloc[c]:>14,.0f}"+f"{cur_rev[c]:>14,.0f}"+f"{est_rev[c]:>14,.0f}")
    tot_cur=sum(cur_rev.values()); tot_est=sum(est_rev.values())
    print(f"\n총 추정매출 {tot_est:,.0f} vs 현재 {tot_cur:,.0f}  (추정 변화 {(tot_est-tot_cur)/max(tot_cur,1):+.1%})")
    print("  * 매출은 체감곡선(p) 가정 추정. 한계수익 균등화가 최적. 점진 테스트로 검증.")

if __name__=="__main__": main()
