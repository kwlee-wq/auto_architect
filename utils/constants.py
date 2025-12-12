"""
AutoArchitect - 상수 및 스타일 정의 (v2.0 리팩토링)
모든 색상, 스타일, 설정 값을 한 곳에서 관리
"""

from typing import Dict, List, Any

# ==================== 색상 정의 ====================

COLOR_MAP: Dict[str, str] = {
    '하늘색': '#E3F2FD',
    '연두색': '#E8F5E9',
    '주황색': '#FFE0B2',
    '회색': '#E0E0E0',
    '연회색': '#F5F5F5',
    '흰색': '#FFFFFF',
    '노란색': '#FFF9C4',
    '분홍색': '#FCE4EC',
    '보라색': '#EDE7F6',
    '파란색': '#BBDEFB',
    '녹색': '#C8E6C9'
}

BORDER_COLOR_MAP: Dict[str, str] = {
    '진한파랑': '#1976D2',
    '진한녹색': '#388E3C',
    '진한주황': '#F57C00',
    '진한회색': '#616161',
    '진회색': '#666666',
    '회색': '#999999',
    '진한빨강': '#D32F2F',
    '진한보라': '#7B1FA2',
    '검정': '#000000'
}

# ==================== 컴포넌트 타입별 스타일 ====================

COMPONENT_STYLES: Dict[str, Dict[str, Any]] = {
    '단일박스': {
        'shape': 'rectangle',
        'style': 'rounded=0;whiteSpace=wrap;html=1;fillColor={fill};strokeColor={stroke};',
        'rounded': False
    },
    '클러스터': {
        'shape': 'rectangle',
        'style': 'rounded=0;whiteSpace=wrap;html=1;dashed=1;dashPattern=5 5;fillColor={fill};strokeColor={stroke};',
        'rounded': False,
        'dashed': True
    },
    '서비스': {
        'shape': 'rectangle',
        'style': 'rounded=1;whiteSpace=wrap;html=1;fillColor={fill};strokeColor={stroke};arcSize=10;',
        'rounded': True
    },
    '데이터베이스': {
        'shape': 'cylinder3',
        'style': 'shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;fillColor={fill};strokeColor={stroke};',
        'rounded': False
    },
    '저장소': {
        'shape': 'folder',
        'style': 'shape=folder;whiteSpace=wrap;html=1;fillColor={fill};strokeColor={stroke};',
        'rounded': False
    },
    '문서': {
        'shape': 'note',
        'style': 'shape=note;whiteSpace=wrap;html=1;fillColor={fill};strokeColor={stroke};',
        'rounded': False
    }
}

# ==================== 연결 타입별 스타일 ====================

CONNECTION_STYLES: Dict[str, Dict[str, str]] = {
    '데이터흐름': {
        'style': 'edgeStyle=orthogonalEdgeStyle;curved=1;orthogonalLoop=1;jettySize=auto;html=1;',
        'arrow': 'classic',
        'start_arrow': 'none'
    },
    '양방향': {
        'style': 'edgeStyle=orthogonalEdgeStyle;curved=1;orthogonalLoop=1;jettySize=auto;html=1;',
        'arrow': 'classic',
        'start_arrow': 'classic'
    },
    '스트림': {
        'style': 'edgeStyle=orthogonalEdgeStyle;curved=1;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=3;',
        'arrow': 'block',
        'start_arrow': 'none'
    },
    '배치': {
        'style': 'edgeStyle=orthogonalEdgeStyle;curved=1;orthogonalLoop=1;jettySize=auto;html=1;dashed=1;dashPattern=3 3;',
        'arrow': 'classic',
        'start_arrow': 'none'
    }
}

LINE_STYLES: Dict[str, str] = {
    '실선': '',
    '점선': 'dashed=1;dashPattern=3 3;',
    '굵은실선': 'strokeWidth=3;',
    '이중선': 'strokeWidth=1;'
}

# ==================== 텍스트 크기 ====================

TEXT_SIZES: Dict[str, int] = {
    '작음': 10,
    '중간': 12,
    '큼': 14,
    '아주큼': 16
}

# ==================== 레이아웃 기본값 ====================

DEFAULT_CANVAS_WIDTH = 1400
DEFAULT_CANVAS_HEIGHT = 900
DEFAULT_MARGIN_PERCENT = 15
DEFAULT_COMPONENT_MIN_WIDTH = 100
DEFAULT_COMPONENT_MIN_HEIGHT = 60
DEFAULT_LAYER_PADDING = 20

# 헤더 영역 설정
LAYER_HEADER_HEIGHT = 20
BOX_HEADER_HEIGHT = 25
HEADER_TOP_MARGIN = 3
HEADER_SIDE_MARGIN = 5

# ==================== 레이아웃 패턴 ====================

LAYOUT_PATTERNS: List[str] = [
    '수평레이어스택',
    '좌우분할',
    '중앙허브형',
    '좌우파이프라인',
    '계층형'
]

# ==================== 엑셀 시트 이름 ====================

EXCEL_SHEETS = {
    'CONFIG': 'CONFIG',
    'LAYERS': 'LAYERS',
    'COMPONENTS': 'COMPONENTS',
    'BOXES': 'BOXES',
    'SUB_COMPONENTS': 'SUB_COMPONENTS',
    'CONNECTIONS': 'CONNECTIONS',
    'GROUPS': 'GROUPS',
    'GUIDE': 'GUIDE'
}

# ==================== 필수 컬럼 ====================

REQUIRED_COLUMNS = {
    'CONFIG': ['항목', '값'],
    'LAYERS': ['레이어ID', '레이어명', '높이%', '배경색'],
    'COMPONENTS': ['ID', '컴포넌트명', '레이어ID', '타입', '너비'],
    'BOXES': ['박스ID', '박스명', '부모ID', 'Y%', '높이%'],
    'SUB_COMPONENTS': ['부모ID', '서브컴포넌트명', '순서'],
    'CONNECTIONS': ['출발ID', '도착ID', '연결타입'],
    'GROUPS': ['그룹ID', '그룹명', '포함컴포넌트(IDs)']
}

# ==================== 검증 규칙 ====================

VALIDATION_RULES = {
    'max_layers': 10,
    'max_components': 50,
    'max_boxes': 100,
    'max_connections': 100,
    'max_sub_components_per_parent': 10,
    'width_range': (1, 5),
    'height_percent_tolerance': 5,
    'max_component_name_length': 50
}

# ==================== 에러 메시지 ====================

ERROR_MESSAGES = {
    'missing_sheet': "'{sheet_name}' 시트가 없습니다.",
    'missing_column': "'{sheet_name}' 시트에 '{column_name}' 컬럼이 없습니다.",
    'duplicate_id': "{id_type} ID가 중복되었습니다: {id_value}",
    'invalid_reference': "{ref_type}에서 참조하는 ID({id_value})가 존재하지 않습니다.",
    'invalid_value': "{column_name}의 값({value})이 유효하지 않습니다. 허용값: {allowed}",
    'height_sum_error': "레이어 높이% 합계가 {sum}%입니다. 100%에 가까워야 합니다 (±{tolerance}% 허용)",
    'empty_required': "'{sheet_name}'의 '{column_name}'은(는) 필수 항목입니다.",
    'file_read_error': "엑셀 파일 읽기 실패: {error}",
    'no_sheets_found': "엑셀 파일에서 시트를 찾을 수 없습니다."
}

WARNING_MESSAGES = {
    'too_many_components': "컴포넌트가 {count}개로 많습니다. {max}개 이하 권장",
    'too_many_boxes': "박스가 {count}개로 많습니다. {max}개 이하 권장",
    'too_many_connections': "연결이 {count}개로 많습니다. 가독성이 떨어질 수 있습니다.",
    'self_connection': "컴포넌트 {id}가 자기 자신과 연결되어 있습니다.",
    'crossing_expected': "연결선 교차가 {count}개 예상됩니다. Draw.io에서 조정이 필요할 수 있습니다."
}

# ==================== 아이콘 매핑 ====================

ICON_MAP = {
    'portal': '🌐',
    'hadoop': '🐘',
    'kafka': '📨',
    'spark': '⚡',
    'kubernetes': '☸️',
    'database': '🗄️',
    'storage': '💾',
    'api': '🔌',
    'web': '🌍',
    'mobile': '📱',
    'server': '🖥️',
    'cloud': '☁️',
    'network': '🌐',
    'security': '🔒',
    'monitor': '📊'
}


# ==================== 유틸리티 함수 ====================

def get_color(color_name: str, default: str = '#FFFFFF') -> str:
    """색상명을 HEX 코드로 변환"""
    import pandas as pd
    if pd.isna(color_name):
        return default
    return COLOR_MAP.get(str(color_name), default)


def get_border_color(color_name: str, default: str = '#999999') -> str:
    """테두리 색상명을 HEX 코드로 변환"""
    import pandas as pd
    if pd.isna(color_name):
        return default
    return BORDER_COLOR_MAP.get(str(color_name), default)


def get_component_style(comp_type: str) -> Dict[str, Any]:
    """컴포넌트 타입에 맞는 스타일 반환"""
    return COMPONENT_STYLES.get(comp_type, COMPONENT_STYLES['단일박스'])


def get_connection_style(conn_type: str) -> Dict[str, str]:
    """연결 타입에 맞는 스타일 반환"""
    return CONNECTION_STYLES.get(conn_type, CONNECTION_STYLES['데이터흐름'])


def get_line_style(style_name: str) -> str:
    """선 스타일 반환"""
    return LINE_STYLES.get(style_name, '')
