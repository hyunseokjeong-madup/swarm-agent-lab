"""
semantic_layer — 비즈니스 용어 → 표준 정의(컬럼/SQL식/safemath 공식) 매핑.

목적: 78개 도구가 "ROAS", "전환", "CPA", "신규회원" 같은 말을 제각각 해석해
표류(drift)하는 걸 막는다. 지표의 '정의'는 여기 한 곳에만 산다.
  - raw 컬럼 정의는 safemath._RAW_ALIASES 를 그대로 재사용(이중 정의 금지)
  - 파생지표 공식은 safemath.recompute_metrics 와 1:1 대응
  - SQL 식(sql)은 DuckDB/표준SQL 의 GROUP BY 집계용 표현

순수 stdlib. duckdb import 안 함.

  python marketing/semantic_layer.py            # 사전 덤프 + 자가검증
  python marketing/semantic_layer.py ROAS       # 단일 용어 resolve
"""
import sys

try:
    from . import safemath
except ImportError:  # 스크립트로 직접 실행될 때
    import safemath


# 합산 가능한 원시 지표의 표준 SQL 집계식.
# 컬럼명은 safemath._RAW_ALIASES 의 canonical 키(딕셔너리 키)를 쓴다.
_RAW_SQL = {
    "impressions": "SUM(impressions)",
    "clicks": "SUM(clicks)",
    "spend": "SUM(spend)",
    "conversions": "SUM(conversions)",
    "revenue": "SUM(revenue)",
}

# 파생지표: 비율은 '합산 후 나눗셈'(가중평균)이라야 맞다 — SUM(a)/SUM(b).
# 단순 AVG(ratio) 는 Simpson 함정이라 금지.
_DERIVED_SQL = {
    "ctr": "SUM(clicks) / NULLIF(SUM(impressions), 0)",
    "cpc": "SUM(spend) / NULLIF(SUM(clicks), 0)",
    "cpm": "SUM(spend) / NULLIF(SUM(impressions), 0) * 1000",
    "cpa": "SUM(spend) / NULLIF(SUM(conversions), 0)",
    "cvr": "SUM(conversions) / NULLIF(SUM(clicks), 0)",
    "roas": "SUM(revenue) / NULLIF(SUM(spend), 0)",
    "ecpm": "SUM(revenue) / NULLIF(SUM(impressions), 0) * 1000",
}


def _term(canonical, kind, sql, formula, aliases, desc):
    return {
        "canonical": canonical,   # 표준 지표 키 (safemath 와 동일)
        "kind": kind,             # "raw" | "derived"
        "sql": sql,               # GROUP BY 집계용 SQL 식
        "formula": formula,       # 사람이 읽는 공식
        "aliases": aliases,       # 매칭되는 비즈니스 용어(한/영/약어)
        "desc": desc,
    }


# 표준 용어집. 키는 canonical 지표명. aliases 에 비즈니스 표현을 모은다.
GLOSSARY = {
    "impressions": _term("impressions", "raw", _RAW_SQL["impressions"], "SUM(impressions)",
                         ["impressions", "impr", "imp", "노출", "노출수"], "광고 노출 합계"),
    "clicks": _term("clicks", "raw", _RAW_SQL["clicks"], "SUM(clicks)",
                    ["clicks", "click", "클릭", "클릭수"], "클릭 합계"),
    "spend": _term("spend", "raw", _RAW_SQL["spend"], "SUM(spend)",
                   ["spend", "cost", "비용", "광고비"], "광고비 합계"),
    "conversions": _term("conversions", "raw", _RAW_SQL["conversions"], "SUM(conversions)",
                         ["conversions", "conv", "conversion", "전환", "전환수",
                          "신규회원", "가입", "설치", "구매", "purchases", "installs"],
                         "전환(가입/설치/구매) 합계 — '신규회원'은 가입 전환으로 본다"),
    "revenue": _term("revenue", "raw", _RAW_SQL["revenue"], "SUM(revenue)",
                     ["revenue", "rev", "매출", "수익", "sales"], "매출 합계"),

    "ctr": _term("ctr", "derived", _DERIVED_SQL["ctr"], "clicks / impressions",
                 ["ctr", "클릭률", "클릭율"], "클릭률 = 클릭/노출"),
    "cpc": _term("cpc", "derived", _DERIVED_SQL["cpc"], "spend / clicks",
                 ["cpc", "클릭단가"], "클릭당 비용 = 비용/클릭"),
    "cpm": _term("cpm", "derived", _DERIVED_SQL["cpm"], "spend / impressions * 1000",
                 ["cpm", "천노출단가"], "1000노출당 비용"),
    "cpa": _term("cpa", "derived", _DERIVED_SQL["cpa"], "spend / conversions",
                 ["cpa", "cpi", "전환단가", "획득단가", "가입단가", "전환비용"],
                 "전환당 비용 = 비용/전환 (CPI=설치단가도 같은 식)"),
    "cvr": _term("cvr", "derived", _DERIVED_SQL["cvr"], "conversions / clicks",
                 ["cvr", "전환율", "전환률"], "전환율 = 전환/클릭"),
    "roas": _term("roas", "derived", _DERIVED_SQL["roas"], "revenue / spend",
                  ["roas", "광고수익률", "광고수익율", "매출대비"], "광고비 대비 매출 = 매출/비용"),
    "ecpm": _term("ecpm", "derived", _DERIVED_SQL["ecpm"], "revenue / impressions * 1000",
                  ["ecpm", "퍼블리셔ecpm"], "퍼블리셔 관점 1000노출당 매출"),
}


# alias(소문자/공백제거) → canonical 역색인. 한글은 그대로 둔다.
def _norm(s):
    return str(s).strip().lower().replace(" ", "").replace("_", "").replace("-", "")


_INDEX = {}
for _canon, _spec in GLOSSARY.items():
    for _a in _spec["aliases"]:
        _INDEX[_norm(_a)] = _canon


def resolve(term):
    """비즈니스 용어 → 표준 정의 dict. 모르는 용어는 KeyError.

    예: resolve("ROAS")  resolve("전환")  resolve("신규회원")  resolve("클릭률")
    """
    key = _norm(term)
    if key in _INDEX:
        return GLOSSARY[_INDEX[key]]
    raise KeyError(
        f"unknown business term: {term!r}. "
        f"known canonical metrics: {sorted(GLOSSARY)}"
    )


def canonical(term):
    """용어 → canonical 지표명 문자열만."""
    return resolve(term)["canonical"]


def sql_for(term):
    """용어 → GROUP BY 집계용 SQL 식."""
    return resolve(term)["sql"]


def known_terms():
    """매칭 가능한 모든 비즈니스 용어(원본 표기) 목록."""
    out = []
    for spec in GLOSSARY.values():
        out.extend(spec["aliases"])
    return sorted(set(out))


def _selftest():
    # 같은 지표는 어떤 alias 로 불러도 같은 canonical 로 모인다(drift 방지 증명)
    assert canonical("ROAS") == "roas"
    assert canonical("광고수익률") == "roas"
    assert canonical("전환") == "conversions"
    assert canonical("신규회원") == "conversions"   # 비즈니스 합의: 가입=전환
    assert canonical("가입단가") == "cpa"
    assert canonical("CPI") == "cpa"
    assert canonical("클릭률") == "ctr"
    # raw 컬럼 정의가 safemath 와 어긋나지 않는지 — canonical 키가 safemath alias 키와 일치
    for k in ("impressions", "clicks", "spend", "conversions", "revenue"):
        assert k in safemath._RAW_ALIASES, k
    # 파생 SQL 키가 safemath.recompute_metrics 출력 키와 일치하는지
    sample = {"impressions": 50000, "clicks": 2500, "spend": 1250000,
              "conversions": 100, "revenue": 3000000}
    for mk in safemath.recompute_metrics(sample):
        assert mk in GLOSSARY, f"{mk} 가 GLOSSARY 에 없음 — 표류 위험"
    # 모르는 용어는 KeyError
    try:
        resolve("바나나")
        raise AssertionError("unknown term should raise")
    except KeyError:
        pass
    return True


if __name__ == "__main__":
    if len(sys.argv) > 1:
        term = sys.argv[1]
        spec = resolve(term)
        print(f"=== resolve({term!r}) ===")
        print(f"  canonical : {spec['canonical']}")
        print(f"  kind      : {spec['kind']}")
        print(f"  sql       : {spec['sql']}")
        print(f"  formula   : {spec['formula']}")
        print(f"  desc      : {spec['desc']}")
        print(f"  aliases   : {', '.join(spec['aliases'])}")
    else:
        _selftest()
        print("=== SEMANTIC LAYER — 표준 용어집 ===")
        print(f"{'canonical':<13}{'kind':<9}{'sql'}")
        for canon, spec in GLOSSARY.items():
            print(f"{canon:<13}{spec['kind']:<9}{spec['sql']}")
        print(f"\nsemantic_layer self-test: PASS  "
              f"({len(GLOSSARY)} metrics, {len(known_terms())} terms)")
