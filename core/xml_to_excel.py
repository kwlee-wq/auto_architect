"""
AutoArchitect - XML to Excel 변환기
Draw.io XML을 엑셀 파일로 역변환
"""

import xml.etree.ElementTree as ET
import pandas as pd
import io
import re
from typing import Dict, List, Any, Optional
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment


# 색상 역매핑 (HEX → 한글)
HEX_TO_COLOR = {
    '#E3F2FD': '하늘색',
    '#E8F5E9': '연두색',
    '#FFE0B2': '주황색',
    '#E0E0E0': '회색',
    '#F5F5F5': '연회색',
    '#FFFFFF': '흰색',
    '#FFF9C4': '노란색',
    '#FCE4EC': '분홍색',
    '#EDE7F6': '보라색',
    '#BBDEFB': '파란색',
    '#C8E6C9': '녹색',
}

HEX_TO_BORDER = {
    '#1976D2': '진한파랑',
    '#388E3C': '진한녹색',
    '#F57C00': '진한주황',
    '#616161': '진한회색',
    '#666666': '진회색',
    '#999999': '회색',
    '#D32F2F': '진한빨강',
    '#7B1FA2': '진한보라',
    '#000000': '검정',
}


class XmlToExcelConverter:
    """Draw.io XML을 엑셀로 변환"""
    
    def __init__(self):
        self.cells = []
        self.id_to_cell = {}
        self.canvas_width = 1400
        self.canvas_height = 900
        self.diagram_name = 'diagram'
    
    def convert(self, xml_content: str) -> bytes:
        """
        XML을 엑셀 바이트로 변환
        
        Args:
            xml_content: Draw.io XML 문자열
        
        Returns:
            엑셀 파일 바이트
        """
        # XML 파싱
        self._parse_xml(xml_content)
        
        # 데이터 추출
        config_data = self._extract_config()
        layers_data, boxes_data = self._extract_layers_and_boxes()
        connections_data = self._extract_connections()
        
        # 엑셀 생성
        return self._create_excel(config_data, layers_data, boxes_data, connections_data)
    
    def _parse_xml(self, xml_content: str):
        """XML 파싱"""
        try:
            root = ET.fromstring(xml_content)
            
            # 다이어그램 이름
            diagram = root.find('.//diagram')
            if diagram is not None:
                self.diagram_name = diagram.get('name', 'diagram')
            
            # 캔버스 크기
            graph_model = root.find('.//mxGraphModel')
            if graph_model is not None:
                self.canvas_width = int(graph_model.get('pageWidth', 1400))
                self.canvas_height = int(graph_model.get('pageHeight', 900))
            
            # 모든 mxCell 수집
            graph_root = root.find('.//root')
            if graph_root is not None:
                for cell in graph_root.findall('mxCell'):
                    cell_id = cell.get('id', '')
                    if cell_id not in ['0', '1']:  # 기본 셀 제외
                        cell_data = self._parse_cell(cell)
                        self.cells.append(cell_data)
                        self.id_to_cell[cell_id] = cell_data
        
        except ET.ParseError as e:
            print(f"XML 파싱 오류: {e}")
    
    def _parse_cell(self, cell: ET.Element) -> Dict[str, Any]:
        """개별 셀 파싱"""
        cell_data = {
            'id': cell.get('id', ''),
            'value': cell.get('value', ''),
            'parent': cell.get('parent', '1'),
            'vertex': cell.get('vertex') == '1',
            'edge': cell.get('edge') == '1',
            'source': cell.get('source'),
            'target': cell.get('target'),
            'style': cell.get('style', ''),
        }
        
        # geometry 파싱
        geom = cell.find('mxGeometry')
        if geom is not None:
            cell_data['x'] = float(geom.get('x', 0))
            cell_data['y'] = float(geom.get('y', 0))
            cell_data['width'] = float(geom.get('width', 100))
            cell_data['height'] = float(geom.get('height', 50))
        else:
            cell_data['x'] = 0
            cell_data['y'] = 0
            cell_data['width'] = 100
            cell_data['height'] = 50
        
        # 스타일 파싱
        cell_data['bg_color'] = self._extract_color_from_style(cell_data['style'], 'fillColor')
        cell_data['border_color'] = self._extract_color_from_style(cell_data['style'], 'strokeColor')
        cell_data['font_size'] = self._extract_font_size(cell_data['style'])
        
        return cell_data
    
    def _extract_color_from_style(self, style: str, key: str) -> str:
        """스타일에서 색상 추출"""
        match = re.search(rf'{key}=([^;]+)', style)
        if match:
            hex_color = match.group(1).upper()
            if not hex_color.startswith('#'):
                hex_color = '#' + hex_color
            return HEX_TO_COLOR.get(hex_color, HEX_TO_BORDER.get(hex_color, '흰색'))
        return '흰색' if key == 'fillColor' else '회색'
    
    def _extract_font_size(self, style: str) -> int:
        """스타일에서 폰트 크기 추출"""
        match = re.search(r'fontSize=(\d+)', style)
        return int(match.group(1)) if match else 11
    
    def _extract_config(self) -> Dict[str, Any]:
        """CONFIG 데이터 추출"""
        return {
            '항목': ['다이어그램명', '캔버스너비', '캔버스높이'],
            '값': [self.diagram_name, self.canvas_width, self.canvas_height]
        }
    
    def _extract_layers_and_boxes(self) -> tuple:
        """레이어와 박스 분리 추출"""
        # parent='1'인 큰 요소들을 레이어로 간주
        # 나머지는 박스로 처리
        
        layers = []
        boxes = []
        
        # 1단계: 레이어 후보 식별 (parent='1'이고 너비가 큰 것)
        layer_candidates = []
        for cell in self.cells:
            if cell['vertex'] and cell['parent'] == '1':
                # 캔버스 너비의 80% 이상이면 레이어로 간주
                if cell['width'] >= self.canvas_width * 0.8:
                    layer_candidates.append(cell)
        
        # Y 좌표로 정렬
        layer_candidates.sort(key=lambda x: x['y'])
        
        # 레이어 데이터 생성
        total_height = sum(c['height'] for c in layer_candidates) or self.canvas_height
        
        for i, cell in enumerate(layer_candidates):
            layer_id = f"L{i+1}"
            height_percent = round((cell['height'] / total_height) * 100, 1)
            
            layers.append({
                'original_id': cell['id'],
                'layer_id': layer_id,
                'name': cell['value'] or f'Layer {i+1}',
                'order': i + 1,
                'bg_color': cell['bg_color'],
                'height_percent': height_percent,
                'y': cell['y'],
                'height': cell['height'],
            })
        
        # ID 매핑 (원본 → 새 ID)
        id_mapping = {layer['original_id']: layer['layer_id'] for layer in layers}
        
        # 2단계: 박스 추출 (레이어가 아닌 vertex)
        box_index = 1
        for cell in self.cells:
            if cell['vertex'] and cell['id'] not in id_mapping:
                # 부모 ID 변환
                parent_id = cell['parent']
                if parent_id in id_mapping:
                    parent_id = id_mapping[parent_id]
                elif parent_id == '1':
                    # 레이어 없이 직접 배치된 경우
                    parent_id = 'L1' if layers else None
                else:
                    # 다른 박스의 자식
                    # 이미 처리된 박스의 ID로 변환 필요
                    pass
                
                # 부모 레이어 찾기
                parent_layer = None
                for layer in layers:
                    if layer['layer_id'] == parent_id:
                        parent_layer = layer
                        break
                
                # Y% 계산
                if parent_layer:
                    y_percent = ((cell['y'] - parent_layer['y']) / parent_layer['height']) * 100
                    height_percent = (cell['height'] / parent_layer['height']) * 100
                else:
                    y_percent = (cell['y'] / self.canvas_height) * 100
                    height_percent = (cell['height'] / self.canvas_height) * 100
                
                box_id = f"B{box_index}"
                boxes.append({
                    'original_id': cell['id'],
                    'box_id': box_id,
                    'name': cell['value'] or f'Box {box_index}',
                    'parent_id': parent_id,
                    'row_number': 1,  # 기본값
                    'y_percent': round(y_percent, 1),
                    'height_percent': round(height_percent, 1),
                    'bg_color': cell['bg_color'],
                    'border_color': cell['border_color'],
                    'font_size': cell['font_size'],
                })
                
                id_mapping[cell['id']] = box_id
                box_index += 1
        
        # 행번호 계산 (같은 Y 좌표면 같은 행)
        self._calculate_row_numbers(boxes)
        
        # 부모 ID 최종 변환
        for box in boxes:
            if box['parent_id'] in id_mapping:
                box['parent_id'] = id_mapping[box['parent_id']]
        
        # ID 매핑 저장 (연결선용)
        self.id_mapping = id_mapping
        
        # 데이터프레임 형식으로 변환
        layers_data = {
            '레이어ID': [l['layer_id'] for l in layers],
            '레이어명': [l['name'] for l in layers],
            '순서': [l['order'] for l in layers],
            '배경색': [l['bg_color'] for l in layers],
            '높이%': [l['height_percent'] for l in layers],
        }
        
        boxes_data = {
            '박스ID': [b['box_id'] for b in boxes],
            '박스명': [b['name'] for b in boxes],
            '부모ID': [b['parent_id'] for b in boxes],
            '행번호': [b['row_number'] for b in boxes],
            'Y%': [b['y_percent'] for b in boxes],
            '높이%': [b['height_percent'] for b in boxes],
            '배경색': [b['bg_color'] for b in boxes],
            '테두리색': [b['border_color'] for b in boxes],
            '폰트크기': [b['font_size'] for b in boxes],
        }
        
        return layers_data, boxes_data
    
    def _calculate_row_numbers(self, boxes: List[Dict]):
        """박스들의 행번호 계산 (비슷한 Y 좌표끼리 그룹화)"""
        # 부모별로 그룹화
        by_parent = {}
        for box in boxes:
            parent = box['parent_id']
            if parent not in by_parent:
                by_parent[parent] = []
            by_parent[parent].append(box)
        
        # 각 그룹 내에서 Y 좌표 기반으로 행번호 할당
        for parent, group in by_parent.items():
            if not group:
                continue
            
            # Y%로 정렬
            sorted_boxes = sorted(group, key=lambda x: x['y_percent'])
            
            # 비슷한 Y% 끼리 같은 행
            current_row = 1
            prev_y = sorted_boxes[0]['y_percent']
            threshold = 5  # 5% 이내면 같은 행
            
            for box in sorted_boxes:
                if abs(box['y_percent'] - prev_y) > threshold:
                    current_row += 1
                box['row_number'] = current_row
                prev_y = box['y_percent']
    
    def _extract_connections(self) -> Dict[str, List]:
        """연결선 추출"""
        connections = {
            '출발ID': [],
            '도착ID': [],
            '연결타입': [],
            '라벨': [],
            '선스타일': [],
        }
        
        for cell in self.cells:
            if cell['edge']:
                source = cell.get('source')
                target = cell.get('target')
                
                if source and target:
                    # ID 변환
                    source_id = self.id_mapping.get(source, source)
                    target_id = self.id_mapping.get(target, target)
                    
                    # 연결 타입 추론
                    style = cell.get('style', '')
                    if 'strokeWidth=3' in style:
                        conn_type = '스트림'
                    elif 'dashed=1' in style:
                        conn_type = '배치'
                    else:
                        conn_type = '데이터흐름'
                    
                    # 선 스타일
                    if 'strokeWidth=3' in style:
                        line_style = '굵은실선'
                    elif 'dashed=1' in style:
                        line_style = '점선'
                    else:
                        line_style = '실선'
                    
                    connections['출발ID'].append(source_id)
                    connections['도착ID'].append(target_id)
                    connections['연결타입'].append(conn_type)
                    connections['라벨'].append(cell.get('value', ''))
                    connections['선스타일'].append(line_style)
        
        return connections
    
    def _create_excel(self, config_data: Dict, layers_data: Dict, 
                      boxes_data: Dict, connections_data: Dict) -> bytes:
        """엑셀 파일 생성"""
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # CONFIG 시트
            if config_data['항목']:
                df_config = pd.DataFrame(config_data)
                df_config.to_excel(writer, sheet_name='CONFIG', index=False)
            
            # LAYERS 시트
            if layers_data['레이어ID']:
                df_layers = pd.DataFrame(layers_data)
                df_layers.to_excel(writer, sheet_name='LAYERS', index=False)
            
            # BOXES 시트
            if boxes_data['박스ID']:
                df_boxes = pd.DataFrame(boxes_data)
                df_boxes.to_excel(writer, sheet_name='BOXES', index=False)
            
            # CONNECTIONS 시트
            if connections_data['출발ID']:
                df_connections = pd.DataFrame(connections_data)
                df_connections.to_excel(writer, sheet_name='CONNECTIONS', index=False)
        
        return output.getvalue()


def xml_to_excel(xml_content: str) -> bytes:
    """
    편의 함수: XML을 엑셀로 변환
    
    Args:
        xml_content: Draw.io XML 문자열
    
    Returns:
        엑셀 파일 바이트
    """
    converter = XmlToExcelConverter()
    return converter.convert(xml_content)
