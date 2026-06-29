"""일일 알림 다이제스트. 한 CSV에서 가드레일 위반·낭비·상위성과를 한 번에 요약(아침 점검용)."""
import argparse, csv, re
from pathlib import Path
from _pmutil import load_rows  # 빈 데이터 우아한 처리
def num(s):
    s=str(s or "").replace(",","").replace("₩","").replace("%","").strip()
    try: return float(s)
    except: return 0.0
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("csv"); ap.add_argument("--by",default=None)
    ap.add_argument("--target-roas",type=float,default=2.0); ap.add_argument("--target-cpa",type=float,default=None)
    ap.add_argument("--md",default=None)
    a=ap.parse_args()
    rows=load_rows(a.csv)
    by=a.by or list(rows[0])[0]
    def find(p): return next((c for c in rows[0] if re.fullmatch(p,c,re.I)),None)
    sc,cc,rc=find("spend|cost|비용|광고비"),find("conversions|conv|전환"),find("revenue|매출|수익")
    agg={}
    for r in rows:
        if re.search(r"total|합계|총계",(r.get(by) or ""),re.I): continue
        k=(r.get(by) or "").strip(); agg.setdefault(k,[0,0,0])
        agg[k][0]+=num(r.get(sc)); agg[k][1]+=num(r.get(cc)); agg[k][2]+=num(r.get(rc))
    ent=[(k,sp,cv,rv,(rv/sp if sp else 0),(sp/cv if cv else None)) for k,(sp,cv,rv) in agg.items()]
    breaches=[e for e in ent if e[4]<a.target_roas or (a.target_cpa and e[5] and e[5]>a.target_cpa)]
    waste=[e for e in ent if e[1] and e[4]<1.0]
    top=sorted(ent,key=lambda e:-e[4])[:3]
    L=[f"# 📋 일일 다이제스트 — `{Path(a.csv).name}`",""]
    L.append(f"**총지출** {sum(e[1] for e in ent):,.0f} · **총매출** {sum(e[3] for e in ent):,.0f} · "
             f"**블렌디드 ROAS** {(sum(e[3] for e in ent)/max(sum(e[1] for e in ent),1)):.2f}x")
    L+=["", f"## ⚠️ 가드레일 위반 (ROAS<{a.target_roas}" + (f", CPA>{a.target_cpa:,.0f}" if a.target_cpa else "") + f"): {len(breaches)}"]
    L+=[f"- {e[0]}: ROAS {e[4]:.2f}x, spend {e[1]:,.0f}" for e in breaches] or ["- 없음"]
    L+=["", f"## 💸 낭비(ROAS<1.0): {len(waste)} · 합 {sum(e[1] for e in waste):,.0f}"]
    L+=[f"- {e[0]}: ROAS {e[4]:.2f}x, spend {e[1]:,.0f}" for e in waste] or ["- 없음"]
    L+=["", "## 🏆 상위 성과(ROAS)"]
    L+=[f"- {e[0]}: ROAS {e[4]:.2f}x" for e in top]
    text="\n".join(L)
    if a.md: Path(a.md).write_text(text+"\n",encoding="utf-8"); print(f"[md] -> {a.md}")
    print("\n=== DAILY DIGEST ===\n"+text)
if __name__=="__main__": main()
