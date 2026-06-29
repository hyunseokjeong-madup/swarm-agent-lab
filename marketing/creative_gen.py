"""
Creative variation generator (소재 기획→생성 보조).
Produces a SYSTEMATIC angle x hook x format matrix of ad-creative concepts with naming
convention, headline/body/CTA templates, and a built-in QA reminder. Deterministic scaffold;
the marketer/agent fills the final copy. (See CREATIVE_PLAYBOOK.md.)

Usage:
  python creative_gen.py --product "겨울 패딩" --benefit "3일 무료배송" --audience "25-34 직장인" \
      --kpi ctr --n 6 --md out.md
"""
import argparse
from pathlib import Path

ANGLES = ["benefit", "problem-solution", "social-proof", "scarcity", "price", "novelty", "curiosity"]
HOOKS = {
    "number":   "{benefit} — 단 3일이면 끝.",
    "question": "아직도 {pain}로 고민하세요?",
    "reversal": "{product}, 비싸다고요? 다시 보세요.",
    "before_after": "{pain} → {benefit}, 이렇게 바뀝니다.",
    "social":   "벌써 N만 명이 {product}를 선택했어요.",
    "curiosity":"{product}의 숨은 한 가지, 끝까지 보세요.",
}
FORMATS = ["video_6s", "video_15s", "image", "carousel", "ugc"]
CTAS = {"ctr": "지금 확인", "cpa": "지금 구매", "roas": "최저가로 구매", "cpm": "더 알아보기", "cvr": "무료로 시작"}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--product", required=True)
    ap.add_argument("--benefit", default="특별 혜택")
    ap.add_argument("--audience", default="타깃 고객")
    ap.add_argument("--pain", default="선택 고민")
    ap.add_argument("--kpi", default="ctr", choices=list(CTAS))
    ap.add_argument("--campaign", default="CMP")
    ap.add_argument("--n", type=int, default=6)
    ap.add_argument("--md", default=None)
    a = ap.parse_args()

    hook_keys = list(HOOKS)
    concepts = []
    for i in range(a.n):
        angle = ANGLES[i % len(ANGLES)]
        hk = hook_keys[i % len(hook_keys)]
        fmt = FORMATS[i % len(FORMATS)]
        hook = HOOKS[hk].format(product=a.product, benefit=a.benefit, pain=a.pain)
        name = f"{a.campaign}_{angle}_{fmt}_{hk}_v{i+1:02d}"
        concepts.append({
            "name": name, "angle": angle, "hook_type": hk, "format": fmt, "hook": hook,
            "headline": f"[{a.product}] {a.benefit}",
            "body": f"{a.audience}을 위한 {a.product}. {a.benefit}. 지금 바로.",
            "cta": CTAS[a.kpi],
        })

    print(f"\n=== CREATIVE MATRIX — {a.product} (KPI={a.kpi}, {a.n} concepts) ===")
    for c in concepts:
        print(f"\n• {c['name']}  [angle={c['angle']} · hook={c['hook_type']} · {c['format']}]")
        print(f"  HOOK: {c['hook']}")
        print(f"  HEADLINE: {c['headline']}")
        print(f"  BODY: {c['body']}")
        print(f"  CTA: {c['cta']}")
    print("\nQA: 1변수만 바꿔 비교가능 / 규격·금칙어·클레임 근거 / 메시지매치(후크↔본문↔CTA↔LP) / 수치는 검산")

    if a.md:
        L = [f"# Creative Matrix — {a.product}", "",
             f"KPI: **{a.kpi}** · audience: {a.audience} · {a.n} concepts", "",
             "| name | angle | hook | format | headline | CTA |",
             "|---|---|---|---|---|---|"]
        for c in concepts:
            L.append(f"| `{c['name']}` | {c['angle']} | {c['hook']} | {c['format']} | {c['headline']} | {c['cta']} |")
        L += ["", "**QA**: 1변수 격리 · 규격/금칙어/클레임 근거 · 메시지매치 · 수치 검산(reconcile)."]
        Path(a.md).write_text("\n".join(L) + "\n", encoding="utf-8")
        print(f"\n[md] -> {a.md}")

if __name__ == "__main__":
    main()
