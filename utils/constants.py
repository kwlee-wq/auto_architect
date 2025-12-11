"""
AutoArchitect - 상수 및 스타일 정의
"""

# ==================== 색상 정의 ====================

COLOR_MAP = {
    '하늘색': '#E3F2FD',
    '연두색': '#E8F5E9',
    '주황색': '#FFE0B2',
    '회색': '#F5F5F5',
    '흰색': '#FFFFFF',
    '노란색': '#FFF9C4',
    '분홍색': '#FCE4EC',
    '보라색': '#EDE7F6',
    '파란색': '#BBDEFB',
    '녹색': '#C8E6C9'
}

BORDER_COLOR_MAP = {
    '진한파랑': '#1976D2',
    '진한녹색': '#388E3C',
    '진한주황': '#F57C00',
    '진한회색': '#616161',
    '진한빨강': '#D32F2F',
    '진한보라': '#7B1FA2',
    '검정': '#000000'
}

# ==================== 컴포넌트 타입별 스타일 ====================

COMPONENT_STYLES = {
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

CONNECTION_STYLES = {
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

# ==================== 선 스타일 ====================

LINE_STYLES = {
    '실선': '',
    '점선': 'dashed=1;dashPattern=3 3;',
    '굵은실선': 'strokeWidth=3;',
    '이중선': 'strokeWidth=1;'
}

# ==================== 텍스트 크기 ====================

TEXT_SIZES = {
    '작음': 10,
    '중간': 12,
    '큼': 14,
    '아주큼': 16
}

# ==================== 레이아웃 기본값 ====================

DEFAULT_CANVAS_WIDTH = 1200
DEFAULT_CANVAS_HEIGHT = 800
DEFAULT_MARGIN_PERCENT = 15
DEFAULT_COMPONENT_MIN_WIDTH = 100
DEFAULT_COMPONENT_MIN_HEIGHT = 60
DEFAULT_LAYER_PADDING = 20

# ==================== 레이아웃 패턴 ====================

LAYOUT_PATTERNS = [
    '수평레이어스택',
    '좌우분할',
    '중앙허브형',
    '좌우파이프라인'
]

# ==================== 엑셀 시트 이름 ====================

EXCEL_SHEETS = {
    'CONFIG': 'CONFIG',
    'LAYERS': 'LAYERS',
    'COMPONENTS': 'COMPONENTS',
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
    'SUB_COMPONENTS': ['부모ID', '서브컴포넌트명', '순서'],
    'CONNECTIONS': ['출발ID', '도착ID', '연결타입'],
    'GROUPS': ['그룹ID', '그룹명', '포함컴포넌트(IDs)']
}

# ==================== 검증 규칙 ====================

VALIDATION_RULES = {
    'max_layers': 10,
    'max_components': 50,
    'max_connections': 100,
    'max_sub_components_per_parent': 10,
    'width_range': (1, 5),
    'height_percent_tolerance': 5,  # ±5%
    'max_component_name_length': 50
}

# ==================== Draw.io XML 템플릿 ====================

DRAWIO_XML_HEADER = '''<?xml version="1.0" encoding="UTF-8"?>
<mxfile host="app.diagrams.net" modified="{modified}" agent="AutoArchitect" version="1.0" type="device">
  <diagram name="{diagram_name}" id="{diagram_id}">
    <mxGraphModel dx="1422" dy="794" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="{page_width}" pageHeight="{page_height}" math="0" shadow="0">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
'''

DRAWIO_XML_FOOTER = '''      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
'''

# ==================== 아이콘 매핑 (향후 확장용) ====================

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

# ==================== 에러 메시지 ====================

ERROR_MESSAGES = {
    'missing_sheet': '{sheet_name} 시트가 없습니다.',
    'missing_column': '{sheet_name} 시트에 {column_name} 컬럼이 없습니다.',
    'duplicate_id': '{id_type} ID가 중복되었습니다: {id_value}',
    'invalid_reference': '{ref_type}에서 참조하는 ID({id_value})가 존재하지 않습니다.',
    'invalid_value': '{column_name}의 값({value})이 유효하지 않습니다. 허용값: {allowed}',
    'height_sum_error': '레이어 높이% 합계가 {sum}%입니다. 100%에 가까워야 합니다 (±{tolerance}% 허용)',
    'empty_required': '{sheet_name}의 {column_name}은(는) 필수 항목입니다.'
}

WARNING_MESSAGES = {
    'too_many_components': '컴포넌트가 {count}개로 많습니다. {max}개 이하 권장',
    'too_many_connections': '연결이 {count}개로 많습니다. 가독성이 떨어질 수 있습니다.',
    'self_connection': '컴포넌트 {id}가 자기 자신과 연결되어 있습니다.',
    'crossing_expected': '연결선 교차가 {count}개 예상됩니다. Draw.io에서 조정이 필요할 수 있습니다.'
}