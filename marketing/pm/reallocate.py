"""예산 재배분 제안 (budget reallocation). 저효율 → 고효율 채널로 예산 이동, 매출 증분 추정.
주의: 한계 ROAS는 체감(diminishing)하므로 추정은 상한선 가이드. 실집행은 점진적 테스트로."""
import argparse, csv, re
from pathlib import Path
from _pmutil import load_rows  # 빈 데이터 우아한 처리
def num(s):
    s=str(s or "").replace(",","").replace("₩","").replace("$","").replace("%","").strip()
    try: return float(s)
    except: return 0.0
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("csv")
    ap.add_argument("--shift", type=float, default=0.2, help="저효율에서 이동할 비율(기본 20%)")
    ap.add_argument("--by", default=None)
    a=ap.parse_args()
    rows=load_rows(a.csv)
    h=rows[0]
    bycol=a.by or list(h)[0]
    def find(p): return next((c for c in h if re.fullmatch(p,c,re.I)),None)
    sc,rc=find("spend|cost|비용|광고비"),find("revenue|매출|수익|sales")
    agg={}
    for r in rows:
        if re.search(r"total|합계|총계",(r.get(bycol) or ""),re.I): continue
        k=(r.get(bycol) or "").strip()
        agg.setdefault(k,[0,0])
        agg[k][0]+=num(r.get(sc)); agg[k][1]+=num(r.get(rc))
    items=[(k,sp,rv,(rv/sp if sp else 0)) for k,(sp,rv) in agg.items()]
    items.sort(key=lambda x:x[3], reverse=True)
    total_spend=sum(i[1] for i in items)
    best,worst=items[0],items[-1]
    move=worst[1]*a.shift
    # 상한 추정: 이동분이 best의 평균 ROAS로 전환된다고 가정
    gain=move*best[3]-move*worst[3]
    print(f"\n=== BUDGET REALLOCATION (총예산 {total_spend:,.0f} 유지) ===")
    print(f"{bycol.ljust(14)} {'spend':>14} {'revenue':>15} {'ROAS':>7}")
    for k,sp,rv,ro in items:
        print(f"{k.ljust(14)} {sp:>14,.0f} {rv:>15,.0f} {ro:>6.2f}x")
    print(f"\n제안: '{worst[0]}'(최저 {worst[3]:.2f}x)에서 {a.shift:.0%}(={move:,.0f}) →"
          f" '{best[0]}'(최고 {best[3]:.2f}x)로 이동")
    print(f"추정 매출 증분(상한): +{gain:,.0f}  · 주의: 한계 ROAS 체감 → 점진 테스트로 검증")
if __name__=="__main__": main()
