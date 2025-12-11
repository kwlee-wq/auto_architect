"""
AutoArchitect - 계층형 Draw.io XML 생성기
"""

import xml.etree.ElementTree as ET
from typing import Dict, List, Any
from datetime import datetime
import uuid
import pandas as pd

from utils.constants import (
    COLOR_MAP,
    BORDER_COLOR_MAP,
    CONNECTION_STYLES,
    LINE_STYLES
)


class NestedDrawioGenerator:
    """계층 구조를 지원하는 Draw.io 생성기"""

    def __init__(self):
        self.cell_id_counter = 2
        self.positions = {}
        self.cell_map = {}  # ID -> cell_id 매핑

    def generate_xml(self, data: Dict[str, Any], positions: Dict[str, Dict]) -> str:
        """전체 XML 생성"""
        self.positions = positions
        self.cell_id_counter = 2
        self.cell_map = {}

        canvas_width = data['config'].get('캔버스너비', 1200)
        canvas_height = data['config'].get('캔버스높이', 900)
        diagram_name = data['config'].get('다이어그램명', 'System Architecture')

        # XML 루트
        root = self._create_root_structure(diagram_name, canvas_width, canvas_height)
        graph_root = root.find('.//root')

        # 레이어 생성 (배경용)
        for layer in data['layers']:
            self._create_layer(layer, graph_root)

        # 박스 생성
        for box in data['boxes']:
            self._create_box(box, graph_root)

        # 컴포넌트 생성
        for comp in data['components']:
            self._create_component(comp, graph_root)

        # 연결선 생성
        if 'connections' in data:
            self._create_connections(data['connections'], graph_root)

        # XML 문자열 변환
        xml_str = self._prettify_xml(root)
        return xml_str

    def _create_root_structure(self, diagram_name: str, width: int, height: int) -> ET.Element:
        """XML 기본 구조"""
        mxfile = ET.Element('mxfile', {
            'host': 'app.diagrams.net',
            'modified': datetime.now().isoformat(),
            'agent': 'AutoArchitect',
            'version': '1.0',
            'type': 'device'
        })

        diagram = ET.SubElement(mxfile, 'diagram', {
            'name': diagram_name,
            'id': str(uuid.uuid4())
        })

        graph_model = ET.SubElement(diagram, 'mxGraphModel', {
            'dx': '1422',
            'dy': '794',
            'grid': '1',
            'gridSize': '10',
            'guides': '1',
            'tooltips': '1',
            'connect': '1',
            'arrows': '1',
            'fold': '1',
            'page': '1',
            'pageScale': '1',
            'pageWidth': str(width),
            'pageHeight': str(height),
            'math': '0',
            'shadow': '0'
        })

        root = ET.SubElement(graph_model, 'root')
        ET.SubElement(root, 'mxCell', {'id': '0'})
        ET.SubElement(root, 'mxCell', {'id': '1', 'parent': '0'})

        return mxfile

    def _create_layer(self, layer: Dict, parent: ET.Element):
        """레이어 생성 (배경)"""
        cell_id = str(self._get_next_id())
        self.cell_map[layer['id']] = cell_id

        pos = self.positions.get(layer['id'], {})
        x = pos.get('x', 0)
        y = pos.get('y', 0)
        width = pos.get('width', 1200)
        height = pos.get('height', 200)

        bg_color = self._get_color(layer['bg_color'])

        style = (
            f"rounded=0;whiteSpace=wrap;html=1;"
            f"fillColor={bg_color};strokeColor=none;"
            f"fontSize=12;fontStyle=1;align=center;verticalAlign=top;"
            f"spacingTop=8;"
        )

        cell = ET.SubElement(parent, 'mxCell', {
            'id': cell_id,
            'value': layer['name'],
            'style': style,
            'parent': '1',
            'vertex': '1'
        })

        ET.SubElement(cell, 'mxGeometry', {
            'x': str(int(x)),
            'y': str(int(y)),
            'width': str(int(width)),
            'height': str(int(height)),
            'as': 'geometry'
        })

    def _create_box(self, box: Dict, parent: ET.Element):
        """박스 생성"""
        cell_id = str(self._get_next_id())
        self.cell_map[box['id']] = cell_id

        pos = self.positions.get(box['id'], {})
        x = pos.get('x', 0)
        y = pos.get('y', 0)
        width = pos.get('width', 200)
        height = pos.get('height', 100)

        bg_color = self._get_color(box.get('bg_color', '연회색'))
        border_color = self._get_border_color(box.get('border_color', '회색'))
        font_size = box.get('font_size', 11)

        # NaN 체크 및 기본값 처리
        if pd.isna(font_size):
            font_size = 11

        style = (
            f"rounded=0;whiteSpace=wrap;html=1;"
            f"fillColor={bg_color};strokeColor={border_color};"
            f"fontSize={int(font_size)};fontStyle=1;align=center;verticalAlign=top;"
            f"spacingTop=8;"
        )

        # 박스명도 NaN 체크
        box_name = box.get('name', '')
        if pd.isna(box_name):
            box_name = ''

        cell = ET.SubElement(parent, 'mxCell', {
            'id': cell_id,
            'value': str(box_name),
            'style': style,
            'parent': '1',
            'vertex': '1'
        })

        ET.SubElement(cell, 'mxGeometry', {
            'x': str(int(x)),
            'y': str(int(y)),
            'width': str(int(width)),
            'height': str(int(height)),
            'as': 'geometry'
        })

    def _create_component(self, comp: Dict, parent: ET.Element):
        """컴포넌트 생성"""
        cell_id = str(self._get_next_id())
        self.cell_map[comp['id']] = cell_id

        pos = self.positions.get(comp['id'], {})
        x = pos.get('x', 0)
        y = pos.get('y', 0)
        width = pos.get('width', 100)
        height = pos.get('height', 60)

        font_size = comp.get('font_size', 10)

        # NaN 체크
        if pd.isna(font_size):
            font_size = 10

        # 타입에 따른 스타일
        if comp.get('type') == '단일박스':
            style = (
                f"rounded=0;whiteSpace=wrap;html=1;"
                f"fillColor=#FFFFFF;strokeColor=#666666;"
                f"fontSize={int(font_size)};fontStyle=0;align=center;verticalAlign=middle;"
            )
        else:
            style = (
                f"rounded=0;whiteSpace=wrap;html=1;"
                f"fillColor=#F5F5F5;strokeColor=#999999;"
                f"fontSize={int(font_size)};fontStyle=0;align=center;verticalAlign=middle;"
            )

        # 컴포넌트명 NaN 체크
        comp_name = comp.get('name', '')
        if pd.isna(comp_name):
            comp_name = ''

        cell = ET.SubElement(parent, 'mxCell', {
            'id': cell_id,
            'value': str(comp_name),
            'style': style,
            'parent': '1',
            'vertex': '1'
        })

        ET.SubElement(cell, 'mxGeometry', {
            'x': str(int(x)),
            'y': str(int(y)),
            'width': str(int(width)),
            'height': str(int(height)),
            'as': 'geometry'
        })

    def _create_connections(self, connections: List[Dict], parent: ET.Element):
        """연결선 생성"""
        for conn in connections:
            from_cell_id = self.cell_map.get(conn['from_id'])
            to_cell_id = self.cell_map.get(conn['to_id'])

            if not from_cell_id or not to_cell_id:
                continue

            cell_id = str(self._get_next_id())

            conn_style = CONNECTION_STYLES.get(conn['type'], CONNECTION_STYLES['데이터흐름'])
            style = conn_style['style']

            line_style = LINE_STYLES.get(conn.get('style', '실선'), '')
            if line_style:
                style += line_style

            style += f"endArrow={conn_style['arrow']};"
            if conn_style['start_arrow'] != 'none':
                style += f"startArrow={conn_style['start_arrow']};"

            # 라벨 NaN 체크
            label = conn.get('label', '')
            if pd.isna(label):
                label = ''

            cell = ET.SubElement(parent, 'mxCell', {
                'id': cell_id,
                'value': str(label),
                'style': style,
                'parent': '1',
                'edge': '1',
                'source': from_cell_id,
                'target': to_cell_id
            })

            ET.SubElement(cell, 'mxGeometry', {
                'relative': '1',
                'as': 'geometry'
            })

    def _get_color(self, color_name: str) -> str:
        """색상명 → Hex"""
        special_colors = {
            '회색': '#E0E0E0',
            '연회색': '#F5F5F5',
            '흰색': '#FFFFFF'
        }
        if color_name in special_colors:
            return special_colors[color_name]
        return COLOR_MAP.get(color_name, '#FFFFFF')

    def _get_border_color(self, color_name: str) -> str:
        """테두리 색상"""
        special_colors = {
            '회색': '#999999',
            '진회색': '#666666',
            '검정': '#000000'
        }
        if color_name in special_colors:
            return special_colors[color_name]
        return BORDER_COLOR_MAP.get(color_name, '#000000')

    def _get_next_id(self) -> int:
        """다음 ID"""
        current = self.cell_id_counter
        self.cell_id_counter += 1
        return current

    def _prettify_xml(self, element: ET.Element) -> str:
        """XML 포맷팅"""
        from xml.dom import minidom
        rough_string = ET.tostring(element, encoding='unicode')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")