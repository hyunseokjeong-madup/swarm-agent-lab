"""
계정 헬스 스코어 — 캠페인 CSV에서 효율(ROAS/목표)·집중도(HHI)·데이터품질을 종합해 0~100 점수.
각 구성요소 0~1 정규화 후 가중합. 계산 정확(요약 수치 검산 가능).

입력 CSV: name + impressions,clicks,spend,conversions,revenue
Usage: python account_health.py data.csv --target-roas 2.5
"""
import argparse, csv, re
from pathlib import Path
from _pmutil import load_rows  # 빈 데이터 우아한 처리
def num(s):
    s=str(s or "").replace(",","").replace("₩","").replace("%","").strip()
    try: return float(s)
    except: return 0.0
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("csv"); ap.add_argument("--target-roas",type=float,default=2.5)
    a=ap.parse_args()
    rows=load_rows(a.csv)
    h={c.lower():c for c in rows[0]}; name=list(rows[0])[0]
    ic,cc,sc,vc,rc=(h.get(k) for k in ("impressions","clicks","spend","conversions","revenue"))
    tot={k:0.0 for k in ("impr","clk","sp","cv","rv")}; spends=[]; dq_bad=0; nrows=0
    for r in rows:
        if re.search(r"total|합계|총계",(r.get(name) or ""),re.I): continue
        nrows+=1
        I,C,S,V,R=(num(r.get(x)) for x in (ic,cc,sc,vc,rc))
        tot["impr"]+=I; tot["clk"]+=C; tot["sp"]+=S; tot["cv"]+=V; tot["rv"]+=R; spends.append(S)
        if (C>I and I>0) or (V>C and C>0) or I<0 or S<0: dq_bad+=1
    roas=tot["rv"]/tot["sp"] if tot["sp"] else 0
    eff=min(roas/a.target_roas,1.0) if a.target_roas else 0
    tsp=sum(spends) or 1; hhi=sum((s/tsp)**2 for s in spends); diversification=1-hhi
    dq=1-(dq_bad/nrows) if nrows else 1
    W={"efficiency":0.5,"diversification":0.2,"data_quality":0.3}
    comp={"efficiency":eff,"diversification":diversification,"data_quality":dq}
    score=sum(W[k]*comp[k] for k in W)*100
    print(f"\n=== ACCOUNT HEALTH ===")
    print(f"블렌디드 ROAS {roas:.2f}x (목표 {a.target_roas}x) · 채널수 {nrows} · HHI {hhi:.3f}")
    print(f"\n구성요소(0~1):")
    for k in W: print(f"  {k.ljust(16)} {comp[k]:.2f} × 가중 {W[k]}")
    grade="🟢 건강" if score>=75 else ("🟡 주의" if score>=50 else "🔴 위험")
    print(f"\n종합 헬스 스코어 = {score:.0f}/100  {grade}")
    print("  · 효율·분산·품질 종합. 낮은 구성요소부터 개선.")
if __name__=="__main__": main()
