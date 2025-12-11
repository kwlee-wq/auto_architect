"""
AutoArchitect - DrawioGenerator 및 LayoutEngine 테스트
"""

import pytest
from pathlib import Path
from core.excel_parser import ExcelParser
from core.layout_engine import LayoutEngine
from core.drawio_generator import DrawioGenerator


class TestLayoutEngine:
    """LayoutEngine 테스트"""

    @pytest.fixture
    def sample_data(self):
        """샘플 데이터 로드"""
        parser = ExcelParser()
        sample_file = Path("templates/sample_data.xlsx")

        if not sample_file.exists():
            pytest.skip("샘플 파일이 없습니다")

        sheets = parser.read_excel(sample_file)
        data = parser.parse_to_dict(sheets)
        return data

    def test_horizontal_layer_stack(self, sample_data):
        """수평 레이어 스택 패턴 테스트"""
        engine = LayoutEngine()
        positions = engine.calculate_positions(sample_data, '수평레이어스택')

        # 모든 레이어에 대한 위치 정보가 있는지
        for layer in sample_data['layers']:
            assert layer['id'] in positions
            assert 'y' in positions[layer['id']]
            assert 'height' in positions[layer['id']]

        # 모든 컴포넌트에 대한 위치 정보가 있는지
        for comp in sample_data['components']:
            assert comp['id'] in positions
            assert 'x' in positions[comp['id']]
            assert 'y' in positions[comp['id']]
            assert 'width' in positions[comp['id']]
            assert 'height' in positions[comp['id']]

    def test_detect_crossings(self, sample_data):
        """연결선 교차 감지 테스트"""
        engine = LayoutEngine()
        positions = engine.calculate_positions(sample_data, '수평레이어스택')

        if sample_data.get('connections'):
            crossings = engine.detect_crossings(positions, sample_data['connections'])
            assert isinstance(crossings, int)
            assert crossings >= 0


class TestDrawioGenerator:
    """DrawioGenerator 테스트"""

    @pytest.fixture
    def sample_data_and_positions(self):
        """샘플 데이터 및 위치 정보"""
        parser = ExcelParser()
        sample_file = Path("templates/sample_data.xlsx")

        if not sample_file.exists():
            pytest.skip("샘플 파일이 없습니다")

        sheets = parser.read_excel(sample_file)
        data = parser.parse_to_dict(sheets)

        engine = LayoutEngine()
        positions = engine.calculate_positions(data, '수평레이어스택')

        return data, positions

    def test_generate_xml(self, sample_data_and_positions):
        """XML 생성 테스트"""
        data, positions = sample_data_and_positions

        generator = DrawioGenerator()
        xml_content = generator.generate_xml(data, positions)

        # XML 기본 검증
        assert '<?xml version' in xml_content
        assert '<mxfile' in xml_content
        assert '<diagram' in xml_content
        assert '<mxGraphModel' in xml_content
        assert '</mxfile>' in xml_content

    def test_xml_has_layers(self, sample_data_and_positions):
        """XML에 레이어가 포함되었는지 테스트"""
        data, positions = sample_data_and_positions

        generator = DrawioGenerator()
        xml_content = generator.generate_xml(data, positions)

        # 레이어명이 XML에 포함되었는지 (XML 이스케이프 고려)
        import xml.etree.ElementTree as ET
        root = ET.fromstring(xml_content)

        # XML에서 모든 value 속성 추출
        all_values = [elem.get('value', '') for elem in root.iter() if elem.get('value')]

        # 각 레이어명이 value 중 하나에 포함되어 있는지 확인
        for layer in data['layers']:
            assert any(layer['name'] in value for value in all_values), \
                f"레이어 '{layer['name']}'이(가) XML에 없습니다"

    def test_xml_has_components(self, sample_data_and_positions):
        """XML에 컴포넌트가 포함되었는지 테스트"""
        data, positions = sample_data_and_positions

        generator = DrawioGenerator()
        xml_content = generator.generate_xml(data, positions)

        # 컴포넌트명이 XML에 포함되었는지 (XML 이스케이프 고려)
        import xml.etree.ElementTree as ET
        root = ET.fromstring(xml_content)

        # XML에서 모든 value 속성 추출
        all_values = [elem.get('value', '') for elem in root.iter() if elem.get('value')]

        # 각 컴포넌트명이 value 중 하나에 포함되어 있는지 확인
        for comp in data['components']:
            assert any(comp['name'] in value for value in all_values), \
                f"컴포넌트 '{comp['name']}'이(가) XML에 없습니다"

    def test_xml_file_creation(self, sample_data_and_positions, tmp_path):
        """XML 파일 생성 및 저장 테스트"""
        data, positions = sample_data_and_positions

        generator = DrawioGenerator()
        xml_content = generator.generate_xml(data, positions)

        # 임시 파일로 저장
        output_file = tmp_path / "test_diagram.drawio"
        output_file.write_text(xml_content, encoding='utf-8')

        # 파일이 생성되었는지
        assert output_file.exists()

        # 파일 내용 검증
        content = output_file.read_text(encoding='utf-8')
        assert '<mxfile' in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])