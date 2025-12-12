"""
AutoArchitect - 통합 테스트
"""

import pytest
from pathlib import Path
import sys

# 프로젝트 루트를 path에 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.excel_parser import ExcelParser, NestedExcelParser, create_parser, detect_excel_type
from core.layout_engine import LayoutEngine, NestedLayoutEngine, create_layout_engine
from core.drawio_generator import DrawioGenerator, NestedDrawioGenerator, create_drawio_generator
from utils.constants import COLOR_MAP, COMPONENT_STYLES, get_color, get_border_color
from utils.validators import check_duplicates, validate_percentage_sum, parse_comma_separated


class TestConstants:
    """상수 테스트"""

    def test_color_map_has_required_colors(self):
        """필수 색상이 정의되어 있는지 확인"""
        required_colors = ['하늘색', '연두색', '주황색', '회색', '흰색']
        for color in required_colors:
            assert color in COLOR_MAP

    def test_component_styles_has_required_types(self):
        """필수 컴포넌트 타입이 정의되어 있는지 확인"""
        required_types = ['단일박스', '클러스터', '서비스', '데이터베이스']
        for comp_type in required_types:
            assert comp_type in COMPONENT_STYLES

    def test_get_color_returns_hex(self):
        """get_color가 HEX 코드를 반환하는지 확인"""
        color = get_color('하늘색')
        assert color.startswith('#')
        assert len(color) == 7

    def test_get_color_returns_default_for_invalid(self):
        """잘못된 색상명에 대해 기본값을 반환하는지 확인"""
        color = get_color('존재하지않는색상')
        assert color == '#FFFFFF'


class TestValidators:
    """검증 함수 테스트"""

    def test_check_duplicates_finds_duplicates(self):
        """중복 값을 찾는지 확인"""
        values = ['A', 'B', 'A', 'C', 'B']
        duplicates = check_duplicates(values)
        assert 'A' in duplicates
        assert 'B' in duplicates
        assert 'C' not in duplicates

    def test_check_duplicates_empty_list(self):
        """빈 리스트 처리 확인"""
        duplicates = check_duplicates([])
        assert duplicates == []

    def test_validate_percentage_sum_valid(self):
        """유효한 퍼센트 합계 확인"""
        is_valid, total = validate_percentage_sum([30, 30, 40])
        assert is_valid is True
        assert total == 100

    def test_validate_percentage_sum_with_tolerance(self):
        """허용 오차 내 퍼센트 합계 확인"""
        is_valid, total = validate_percentage_sum([30, 30, 38])  # 98%
        assert is_valid is True  # 5% 허용 오차

    def test_validate_percentage_sum_invalid(self):
        """유효하지 않은 퍼센트 합계 확인"""
        is_valid, total = validate_percentage_sum([30, 30, 20])  # 80%
        assert is_valid is False

    def test_parse_comma_separated(self):
        """쉼표 구분 문자열 파싱 확인"""
        result = parse_comma_separated('A, B, C')
        assert result == ['A', 'B', 'C']

    def test_parse_comma_separated_empty(self):
        """빈 값 처리 확인"""
        import pandas as pd
        result = parse_comma_separated(pd.NA)
        assert result == []


class TestExcelParser:
    """ExcelParser 테스트"""

    def test_parser_initialization(self):
        """파서 초기화 테스트"""
        parser = ExcelParser()
        assert parser.errors == []
        assert parser.warnings == []

    def test_create_parser_flat(self):
        """기본형 파서 생성 테스트"""
        sheets = {'CONFIG': None, 'LAYERS': None, 'COMPONENTS': None}
        parser = create_parser(sheets)
        assert isinstance(parser, ExcelParser)

    def test_create_parser_nested(self):
        """계층형 파서 생성 테스트"""
        sheets = {'CONFIG': None, 'LAYERS': None, 'BOXES': None}
        parser = create_parser(sheets)
        assert isinstance(parser, NestedExcelParser)


class TestNestedExcelParser:
    """NestedExcelParser 테스트"""

    def test_parser_initialization(self):
        """파서 초기화 테스트"""
        parser = NestedExcelParser()
        assert parser.errors == []
        assert parser.excel_version is None


class TestLayoutEngine:
    """LayoutEngine 테스트"""

    def test_layout_engine_initialization(self):
        """레이아웃 엔진 초기화 테스트"""
        engine = LayoutEngine()
        assert engine.positions == {}

    def test_horizontal_layer_stack(self):
        """수평 레이어 스택 레이아웃 테스트"""
        engine = LayoutEngine()
        data = {
            'config': {'캔버스너비': 1200, '캔버스높이': 800, '여백비율': 15},
            'layers': [
                {'id': 'L1', 'name': 'Layer 1', 'height_percent': 50},
                {'id': 'L2', 'name': 'Layer 2', 'height_percent': 50}
            ],
            'components': [
                {'id': 'C1', 'name': 'Comp 1', 'layer_id': 'L1'},
                {'id': 'C2', 'name': 'Comp 2', 'layer_id': 'L2'}
            ]
        }
        positions = engine.calculate_positions(data, '수평레이어스택')

        assert 'L1' in positions
        assert 'L2' in positions
        assert 'C1' in positions
        assert 'C2' in positions

    def test_create_layout_engine_flat(self):
        """기본형 레이아웃 엔진 생성 테스트"""
        engine = create_layout_engine(is_nested=False)
        assert isinstance(engine, LayoutEngine)

    def test_create_layout_engine_nested(self):
        """계층형 레이아웃 엔진 생성 테스트"""
        engine = create_layout_engine(is_nested=True)
        assert isinstance(engine, NestedLayoutEngine)


class TestNestedLayoutEngine:
    """NestedLayoutEngine 테스트"""

    def test_nested_layout_engine_initialization(self):
        """계층형 레이아웃 엔진 초기화 테스트"""
        engine = NestedLayoutEngine()
        assert engine.LEFT_MARGIN == 5
        assert engine.RIGHT_MARGIN == 5
        assert engine.GAP == 2

    def test_calculate_layer_positions(self):
        """레이어 위치 계산 테스트"""
        engine = NestedLayoutEngine()
        data = {
            'config': {'캔버스너비': 1400, '캔버스높이': 900},
            'layers': [
                {'id': 'L1', 'height_percent': 20},
                {'id': 'L2', 'height_percent': 80}
            ],
            'boxes': [],
            'components': []
        }
        positions = engine.calculate_positions(data)

        assert 'L1' in positions
        assert 'L2' in positions
        assert positions['L1']['height'] == 180  # 900 * 0.2
        assert positions['L2']['height'] == 720  # 900 * 0.8


class TestDrawioGenerator:
    """DrawioGenerator 테스트"""

    def test_generator_initialization(self):
        """생성기 초기화 테스트"""
        generator = DrawioGenerator()
        assert generator.cell_id_counter == 2
        assert generator.positions == {}

    def test_generate_xml_basic(self):
        """기본 XML 생성 테스트"""
        generator = DrawioGenerator()
        data = {
            'config': {'다이어그램명': 'Test', '캔버스너비': 800, '캔버스높이': 600},
            'layers': [{'id': 'L1', 'name': 'Layer 1', 'bg_color': '하늘색'}],
            'components': [],
            'connections': []
        }
        positions = {'L1': {'x': 0, 'y': 0, 'width': 800, 'height': 600}}

        xml = generator.generate_xml(data, positions)

        assert '<?xml version' in xml
        assert '<mxfile' in xml
        assert 'Test' in xml

    def test_create_drawio_generator_flat(self):
        """기본형 생성기 생성 테스트"""
        generator = create_drawio_generator(is_nested=False)
        assert isinstance(generator, DrawioGenerator)

    def test_create_drawio_generator_nested(self):
        """계층형 생성기 생성 테스트"""
        generator = create_drawio_generator(is_nested=True)
        assert isinstance(generator, NestedDrawioGenerator)


class TestNestedDrawioGenerator:
    """NestedDrawioGenerator 테스트"""

    def test_generator_initialization(self):
        """생성기 초기화 테스트"""
        generator = NestedDrawioGenerator()
        assert generator.box_children == {}

    def test_generate_xml_with_boxes(self):
        """박스가 포함된 XML 생성 테스트"""
        generator = NestedDrawioGenerator()
        data = {
            'config': {'다이어그램명': 'Nested Test', '캔버스너비': 1200, '캔버스높이': 800},
            'layers': [{'id': 'L1', 'name': 'Layer 1', 'bg_color': '연회색'}],
            'boxes': [{'id': 'B1', 'name': 'Box 1', 'parent_id': 'L1', 'bg_color': '흰색', 'border_color': '회색'}],
            'components': [],
            'connections': []
        }
        positions = {
            'L1': {'x': 0, 'y': 0, 'width': 1200, 'height': 800},
            'B1': {'x': 50, 'y': 50, 'width': 200, 'height': 100}
        }

        xml = generator.generate_xml(data, positions)

        assert '<?xml version' in xml
        assert 'Nested Test' in xml


class TestIntegration:
    """통합 테스트"""

    @pytest.fixture
    def sample_flat_data(self):
        """기본형 샘플 데이터"""
        return {
            'config': {
                '다이어그램명': '테스트 다이어그램',
                '캔버스너비': 1200,
                '캔버스높이': 800,
                '여백비율': 15
            },
            'layers': [
                {'id': 'L1', 'name': 'Application Layer', 'height_percent': 30, 'bg_color': '하늘색'},
                {'id': 'L2', 'name': 'Data Layer', 'height_percent': 70, 'bg_color': '연두색'}
            ],
            'components': [
                {'id': 'C1', 'name': 'Web Server', 'layer_id': 'L1', 'type': '서비스', 'width': 2},
                {'id': 'C2', 'name': 'Database', 'layer_id': 'L2', 'type': '데이터베이스', 'width': 3}
            ],
            'sub_components': [],
            'connections': [
                {'from_id': 'C1', 'to_id': 'C2', 'type': '데이터흐름', 'label': 'Query'}
            ],
            'groups': []
        }

    @pytest.fixture
    def sample_nested_data(self):
        """계층형 샘플 데이터"""
        return {
            'config': {
                '다이어그램명': '계층형 테스트',
                '캔버스너비': 1400,
                '캔버스높이': 900
            },
            'layers': [
                {'id': 'L1', 'name': 'Service Layer', 'height_percent': 20, 'bg_color': '연회색'},
                {'id': 'L2', 'name': 'Application Layer', 'height_percent': 80, 'bg_color': '흰색'}
            ],
            'boxes': [
                {'id': 'B1', 'name': 'Box 1', 'parent_id': 'L2', 'row_number': 1, 'y_percent': 10, 'height_percent': 80, 'bg_color': '하늘색', 'border_color': '회색', 'font_size': 11},
                {'id': 'B2', 'name': 'Box 2', 'parent_id': 'L2', 'row_number': 1, 'y_percent': 10, 'height_percent': 80, 'bg_color': '연두색', 'border_color': '회색', 'font_size': 11}
            ],
            'components': [],
            'connections': []
        }

    def test_flat_workflow(self, sample_flat_data):
        """기본형 전체 워크플로우 테스트"""
        # 레이아웃 계산
        layout_engine = LayoutEngine()
        positions = layout_engine.calculate_positions(sample_flat_data, '수평레이어스택')

        assert len(positions) > 0

        # XML 생성
        generator = DrawioGenerator()
        xml = generator.generate_xml(sample_flat_data, positions)

        assert '<mxfile' in xml
        assert 'Web Server' in xml
        assert 'Database' in xml

    def test_nested_workflow(self, sample_nested_data):
        """계층형 전체 워크플로우 테스트"""
        # 레이아웃 계산
        layout_engine = NestedLayoutEngine()
        positions = layout_engine.calculate_positions(sample_nested_data)

        assert 'L1' in positions
        assert 'L2' in positions
        assert 'B1' in positions
        assert 'B2' in positions

        # XML 생성
        generator = NestedDrawioGenerator()
        xml = generator.generate_xml(sample_nested_data, positions)

        assert '<mxfile' in xml
        assert '계층형 테스트' in xml


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
