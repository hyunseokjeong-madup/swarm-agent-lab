"""
HTML 대시보드 생성 — CSV를 받아 종합 카드 + 차원별 표(인라인 막대)를 단일 HTML로 출력.
수치는 원자료에서 재계산(가중). 의존성 없음(순수 HTML/CSS).

입력 CSV: <dimension>(첫 열), impressions, clicks, spend, conversions, revenue
Usage: python dashboard.py data.csv --by creative --out dash.html
"""
import argparse, csv, re, html
from pathlib import Path
from _pmutil import load_rows  # 빈 데이터 우아한 처리
from collections import defaultdict
RAWM=["impressions","clicks","spend","conversions","revenue"]
def num(s):
    s=str(s or "").replace(",","").replace("₩","").replace("$","").replace("%","").strip()
    try: return float(s)
    except: return 0.0
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("csv"); ap.add_argument("--by",default=None); ap.add_argument("--out",default="dashboard.html")
    a=ap.parse_args()
    rows=load_rows(a.csv)
    by=a.by or list(rows[0])[0]
    g=defaultdict(lambda:{m:0.0 for m in RAWM}); tot={m:0.0 for m in RAWM}
    for r in rows:
        if re.search(r"total|합계|총계",(r.get(by) or ""),re.I): continue
        k=(r.get(by) or "").strip()
        for m in RAWM:
            v=num(r.get(m)); g[k][m]+=v; tot[m]+=v
    roas=tot["revenue"]/tot["spend"] if tot["spend"] else 0
    ctr=tot["clicks"]/tot["impressions"] if tot["impressions"] else 0
    mx=max((v["spend"] for v in g.values()),default=1) or 1
    cards="".join(f'<div class=card><div class=k>{m}</div><div class=v>{tot[m]:,.0f}</div></div>' for m in RAWM)
    cards+=f'<div class=card><div class=k>CTR</div><div class=v>{ctr:.2%}</div></div><div class=card><div class=k>ROAS</div><div class=v>{roas:.2f}x</div></div>'
    rowshtml=""
    for k,v in sorted(g.items(),key=lambda x:-x[1]["spend"]):
        r2=v["revenue"]/v["spend"] if v["spend"] else 0
        bar=int(v["spend"]/mx*100)
        rowshtml+=f'<tr><td>{html.escape(k)}</td><td class=n>{v["spend"]:,.0f}<div class=bar><i style="width:{bar}%"></i></div></td><td class=n>{v["revenue"]:,.0f}</td><td class=n>{r2:.2f}x</td></tr>'
    doc=f"""<!doctype html><meta charset=utf-8><title>MADOBI Dashboard</title>
<style>body{{font-family:Segoe UI,system-ui,sans-serif;background:#0b1020;color:#e6ecff;margin:0;padding:24px}}
h1{{font-size:20px}} .cards{{display:flex;gap:12px;flex-wrap:wrap;margin:16px 0}}
.card{{background:#161d3a;border:1px solid #2a335c;border-radius:12px;padding:12px 16px;min-width:120px}}
.k{{color:#9fb0d9;font-size:12px}} .v{{font-size:20px;font-weight:700}}
table{{width:100%;border-collapse:collapse}} th,td{{padding:8px;border-bottom:1px solid #222a4d;text-align:left}}
.n{{text-align:right}} .bar{{height:4px;background:#222a4d;border-radius:2px;margin-top:4px}} .bar i{{display:block;height:4px;background:linear-gradient(90deg,#6ee7ff,#b072ff);border-radius:2px}}</style>
<h1>🧠 MADOBI — {html.escape(by)}별 대시보드</h1>
<div class=cards>{cards}</div>
<table><tr><th>{html.escape(by)}</th><th class=n>spend</th><th class=n>revenue</th><th class=n>ROAS</th></tr>{rowshtml}</table>
<p style="color:#9fb0d9;font-size:12px">* 수치는 원자료 재계산(가중). reconcile로 검산.</p>"""
    Path(a.out).write_text(doc,encoding="utf-8",newline="\n")
    print(f"=== DASHBOARD ===\nwrote {a.out} ({len(g)} rows, ROAS {roas:.2f}x)")
if __name__=="__main__": main()
