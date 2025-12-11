"""
AutoArchitect - 검증 헬퍼 함수
"""

from typing import List, Set, Any
import pandas as pd


def check_duplicates(values: List[Any]) -> List[Any]:
    """
    리스트에서 중복된 값들을 찾아 반환

    Args:
        values: 검사할 값 리스트

    Returns:
        중복된 값들의 리스트
    """
    seen = set()
    duplicates = set()

    for value in values:
        if pd.notna(value):
            if value in seen:
                duplicates.add(value)
            else:
                seen.add(value)

    return list(duplicates)


def check_references(references: List[Any], valid_set: Set[Any]) -> List[Any]:
    """
    참조가 유효한지 검사

    Args:
        references: 검사할 참조 리스트
        valid_set: 유효한 값들의 집합

    Returns:
        유효하지 않은 참조들의 리스트
    """
    invalid = []

    for ref in references:
        if pd.notna(ref) and ref not in valid_set:
            invalid.append(ref)

    return invalid


def validate_numeric_range(value: Any, min_val: float, max_val: float) -> bool:
    """
    숫자가 범위 내에 있는지 검사

    Args:
        value: 검사할 값
        min_val: 최소값
        max_val: 최대값

    Returns:
        범위 내에 있으면 True
    """
    if pd.isna(value):
        return False

    try:
        num_value = float(value)
        return min_val <= num_value <= max_val
    except (ValueError, TypeError):
        return False


def validate_value_in_list(value: Any, valid_values: List[str]) -> bool:
    """
    값이 허용된 목록에 있는지 검사

    Args:
        value: 검사할 값
        valid_values: 허용된 값들의 리스트

    Returns:
        목록에 있으면 True
    """
    if pd.isna(value):
        return False

    return str(value) in valid_values


def parse_comma_separated(value: Any) -> List[str]:
    """
    쉼표로 구분된 문자열을 리스트로 변환

    Args:
        value: 쉼표로 구분된 문자열

    Returns:
        문자열 리스트 (공백 제거됨)
    """
    if pd.isna(value):
        return []

    return [item.strip() for item in str(value).split(',') if item.strip()]


def is_empty_value(value: Any) -> bool:
    """
    값이 비어있는지 확인 (None, NaN, 빈 문자열)

    Args:
        value: 검사할 값

    Returns:
        비어있으면 True
    """
    if pd.isna(value):
        return True

    if isinstance(value, str) and value.strip() == '':
        return True

    return False


def sanitize_string(value: Any, max_length: int = None) -> str:
    """
    문자열 정제 (공백 제거, 길이 제한)

    Args:
        value: 정제할 값
        max_length: 최대 길이 (None이면 제한 없음)

    Returns:
        정제된 문자열
    """
    if pd.isna(value):
        return ''

    result = str(value).strip()

    if max_length and len(result) > max_length:
        result = result[:max_length]

    return result


def validate_percentage_sum(values: List[float],
                            target: float = 100.0,
                            tolerance: float = 5.0) -> tuple:
    """
    퍼센트 값들의 합계가 목표에 가까운지 검사

    Args:
        values: 퍼센트 값 리스트
        target: 목표 합계 (기본 100%)
        tolerance: 허용 오차 (기본 ±5%)

    Returns:
        (is_valid, actual_sum)
    """
    actual_sum = sum(v for v in values if pd.notna(v))
    is_valid = (target - tolerance) <= actual_sum <= (target + tolerance)

    return is_valid, actual_sum


def format_error_location(sheet_name: str, row_num: int, column_name: str = None) -> str:
    """
    에러 위치를 사용자 친화적으로 포맷팅

    Args:
        sheet_name: 시트명
        row_num: 행 번호 (1-based)
        column_name: 컬럼명 (옵션)

    Returns:
        포맷된 위치 문자열
    """
    location = f"{sheet_name} 시트 {row_num}행"

    if column_name:
        location += f" {column_name} 컬럼"

    return location