"""
pm 도구 공통 유틸 — 빈 데이터 우아한 처리(IndexError 방지).

배경: 78개 pm 도구 중 다수가 `rows=list(csv.DictReader(...))` 직후 rows[0] 등 첫 행을 가정해,
빈/헤더만 있는 CSV(필터로 0행이 된 export 등)에 IndexError 로 크래시했다. 마케터가 빈 데이터를
던져도 traceback 대신 "데이터 없음" 한 줄로 우아하게 끝나야 한다("숫자 안 틀린다"의 신뢰).

순수 stdlib. 정상 데이터엔 투명(rows 그대로 반환) → 95/95 테스트 영향 0.
"""
import csv
import sys
from pathlib import Path


def load_rows(csv_path, empty_msg="데이터 없음 — 입력 CSV에 데이터 행이 없습니다.", exit_on_empty=True):
    """CSV를 DictReader 로 읽어 rows 리스트 반환. 비어있으면 메시지 출력 후 종료(exit 0).

    정상 데이터면 rows 를 그대로 반환하므로 기존 도구 로직은 변경 없이 동작한다.
    exit_on_empty=False 면 빈 경우 [] 를 반환(호출부가 직접 처리)."""
    rows = list(csv.DictReader(Path(csv_path).read_text(encoding="utf-8").splitlines()))
    if not rows:
        if exit_on_empty:
            print(empty_msg)
            sys.exit(0)
        return []
    return rows
