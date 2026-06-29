"""
코호트 리텐션 HTML 히트맵 — 코호트×기간 잔존율을 색조 셀로 시각화. 잔존율 계산 정확.

입력 CSV: cohort, period, active_users
Usage: python cohort_heatmap.py cohorts.csv --out heatmap.html
"""
import argparse, csv, html
from pathlib import Path
from _pmutil import load_rows  # 빈 데이터 우아한 처리
from collections import defaultdict
def num(s):
    s=str(s or "").replace(",","").strip()
    try: return float(s)
    except: return 0.0
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("csv"); ap.add_argument("--out",default="cohort_heatmap.html")
    a=ap.parse_args()
    rows=load_rows(a.csv)
    h={c.lower():c for c in rows[0]}
    cc=h.get("cohort") or list(rows[0])[0]; pc=h.get("period"); uc=h.get("active_users") or h.get("users")
    data=defaultdict(dict)
    for r in rows: data[r[cc].strip()][int(num(r.get(pc)))]=num(r.get(uc))
    periods=sorted({p for co in data for p in data[co]})
    def color(x):  # 0..1 -> red→green
        r=int(255*(1-x)); g=int(180*x)+40; return f"rgb({r},{g},60)"
    cells=""
    for co in sorted(data):
        base=data[co].get(0,0)
        cells+=f"<tr><td class=h>{html.escape(co)}</td>"
        for p in periods:
            if p in data[co] and base:
                ret=data[co][p]/base
                cells+=f'<td style="background:{color(ret)}">{ret*100:.0f}%</td>'
            else: cells+='<td class=e></td>'
        cells+="</tr>"
    hdr="".join(f"<th>P{p}</th>" for p in periods)
    doc=f"""<!doctype html><meta charset=utf-8><title>Cohort Heatmap</title>
<style>body{{font-family:Segoe UI,system-ui,sans-serif;background:#0b1020;color:#e6ecff;padding:24px}}
table{{border-collapse:collapse}} td,th{{padding:8px 12px;text-align:center;font-size:13px}}
.h{{text-align:left;color:#9fb0d9}} td{{color:#0b1020;font-weight:700}} .e{{background:#161d3a}}</style>
<h1>🧠 MADOBI — 코호트 리텐션 히트맵</h1>
<table><tr><th>cohort</th>{hdr}</tr>{cells}</table>
<p style="color:#9fb0d9;font-size:12px">* 잔존율 = period N 활성 / period 0 활성(원자료 계산).</p>"""
    Path(a.out).write_text(doc,encoding="utf-8")
    print(f"=== COHORT HEATMAP ===\nwrote {a.out} ({len(data)} cohorts × {len(periods)} periods)")
if __name__=="__main__": main()
