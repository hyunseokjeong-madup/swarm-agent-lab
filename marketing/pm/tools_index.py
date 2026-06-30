"""
도구 인덱스 생성기 — marketing/pm/*.py 의 모듈 도크스트링 첫 줄을 모아 TOOLS.md 자동 생성.
도구가 늘 때마다 실행하면 인덱스가 자동 최신화(발견성·정합성). 자기 자신도 포함.

Usage: python tools_index.py   (writes marketing/pm/TOOLS.md)
"""
import re, glob
from pathlib import Path
HERE=Path(__file__).parent
def first_doc_line(path):
    s=Path(path).read_text(encoding="utf-8")
    m=re.search(r'^\s*"""(.*?)"""', s, re.S|re.M)
    if not m: return ""
    for ln in m.group(1).strip().splitlines():
        if ln.strip(): return ln.strip()
    return ""
def main():
    files=sorted(glob.glob(str(HERE/"*.py")))
    rows=[]
    for f in files:
        name=Path(f).name
        # 언더스코어 헬퍼(_pmutil 등)와 생성기 자신은 'CLI 의사결정 도구'가 아님 → 제외.
        # (예전엔 `pass` 라 제외가 안 돼 _pmutil/자기자신이 도구 수에 잡혔다.)
        if name.startswith("_") or name == "tools_index.py":
            continue
        rows.append((name, first_doc_line(f)))
    out=["# marketing/pm — 도구 인덱스 (자동 생성)","",
         f"총 {len(rows)}개 도구. `python tools_index.py`로 갱신. 모든 계산은 코드 검산(수치 안 틀림).","",
         "| 도구 | 설명 |","|------|------|"]
    for name,doc in rows:
        out.append(f"| `{name}` | {doc} |")
    (HERE/"TOOLS.md").write_text("\n".join(out)+"\n",encoding="utf-8")
    print(f"TOOLS index: {len(rows)} tools -> marketing/pm/TOOLS.md")
if __name__=="__main__": main()
