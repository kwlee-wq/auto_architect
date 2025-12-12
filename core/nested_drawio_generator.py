"""
AutoArchitect - Draw.io 생성기
- 레이어/박스 헤더 영역 확보
- app.py와 호환되는 클래스명 사용
"""

import xml.etree.ElementTree as ET
from typing import Dict, List, Any
from datetime import datetime
import uuid
import pandas as pd

# 색상 매핑
COLOR_MAP = {
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

BORDER_COLOR_MAP = {
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

LINE_STYLES = {
    '실선': '',
    '점선': 'dashed=1;dashPattern=3 3;',
    '굵은실선': 'strokeWidth=3;',
    '이중선': 'strokeWidth=1;'
}


class NestedDrawioGenerator:
    """Draw.io XML 생성기 - 헤더 영역 확보 버전"""

    LAYER_HEADER_HEIGHT = 20
    BOX_HEADER_HEIGHT = 25
    HEADER_TOP_MARGIN = 3
    HEADER_SIDE_MARGIN = 5

    def __init__(self):
        self.cell_id_counter = 2
        self.positions = {}
        self.cell_map = {}
        self.box_children = {}

    def generate_xml(self, data: Dict[str, Any], positions: Dict[str, Dict]) -> str:
        """전체 XML 생성"""
        self.positions = positions
        self.cell_id_counter = 2
        self.cell_map = {}

        self._calculate_children_count(data)

        canvas_width = data.get('config', {}).get('캔버스너비', 1200)
        canvas_height = data.get('config', {}).get('캔버스높이', 900)
        diagram_name = data.get('config', {}).get('다이어그램명', 'System Architecture')

        root = self._create_root_structure(diagram_name, canvas_width, canvas_height)
        graph_root = root.find('.//root')

        for layer in data.get('layers', []):
            self._create_layer_with_header(layer, graph_root)

        for box in data.get('boxes', []):
            self._create_box_with_header(box, graph_root)

        for comp in data.get('components', []):
            self._create_component(comp, graph_root)

        if 'connections' in data:
            self._create_connections(data['connections'], graph_root)

        xml_str = self._prettify_xml(root)
        return xml_str

    def _calculate_children_count(self, data: Dict[str, Any]):
        self.box_children = {}

        for box in data.get('boxes', []):
            parent_id = box.get('parent_id')
            if parent_id:
                self.box_children[parent_id] = self.box_children.get(parent_id, 0) + 1

        for comp in data.get('components', []):
            parent_id = comp.get('parent_id')
            if parent_id:
                self.box_children[parent_id] = self.box_children.get(parent_id, 0) + 1

    def _has_children(self, item_id: str) -> bool:
        return self.box_children.get(item_id, 0) > 0

    def _create_root_structure(self, diagram_name: str, width: int, height: int) -> ET.Element:
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

    def _create_layer_with_header(self, layer: Dict, parent: ET.Element):
        cell_id = str(self._get_next_id())
        self.cell_map[layer['id']] = cell_id

        pos = self.positions.get(layer['id'], {})
        x = pos.get('x', 0)
        y = pos.get('y', 0)
        width = pos.get('width', 1200)
        height = pos.get('height', 200)

        bg_color = self._get_color(layer.get('bg_color', '흰색'))
        layer_name = layer.get('name', '')

        style = (
            f"rounded=0;whiteSpace=wrap;html=1;"
            f"fillColor={bg_color};strokeColor=none;"
        )

        cell = ET.SubElement(parent, 'mxCell', {
            'id': cell_id,
            'value': '',
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

        header_cell_id = str(self._get_next_id())

        header_x = x + (width / 2) - 150
        header_y = y + self.HEADER_TOP_MARGIN
        header_width = 300
        header_height = self.LAYER_HEADER_HEIGHT

        header_style = (
            f"text;html=1;strokeColor=none;fillColor=none;"
            f"align=center;verticalAlign=middle;whiteSpace=wrap;rounded=0;"
            f"fontSize=12;fontStyle=1;"
        )

        header_cell = ET.SubElement(parent, 'mxCell', {
            'id': header_cell_id,
            'value': str(layer_name),
            'style': header_style,
            'parent': '1',
            'vertex': '1'
        })

        ET.SubElement(header_cell, 'mxGeometry', {
            'x': str(int(header_x)),
            'y': str(int(header_y)),
            'width': str(int(header_width)),
            'height': str(int(header_height)),
            'as': 'geometry'
        })

    def _create_box_with_header(self, box: Dict, parent: ET.Element):
        box_id = box['id']
        has_children = self._has_children(box_id)

        pos = self.positions.get(box_id, {})
        box_x = pos.get('x', 0)
        box_y = pos.get('y', 0)
        box_width = pos.get('width', 200)
        box_height = pos.get('height', 100)

        bg_color = self._get_color(box.get('bg_color', '연회색'))
        border_color = self._get_border_color(box.get('border_color', '회색'))
        font_size = box.get('font_size', 11)

        if pd.isna(font_size):
            font_size = 11

        box_name = box.get('name', '')
        if pd.isna(box_name):
            box_name = ''

        cell_id = str(self._get_next_id())
        self.cell_map[box_id] = cell_id

        style = (
            f"rounded=0;whiteSpace=wrap;html=1;"
            f"fillColor={bg_color};strokeColor={border_color};"
        )

        cell = ET.SubElement(parent, 'mxCell', {
            'id': cell_id,
            'value': '',
            'style': style,
            'parent': '1',
            'vertex': '1'
        })

        ET.SubElement(cell, 'mxGeometry', {
            'x': str(int(box_x)),
            'y': str(int(box_y)),
            'width': str(int(box_width)),
            'height': str(int(box_height)),
            'as': 'geometry'
        })

        header_cell_id = str(self._get_next_id())

        if has_children:
            header_x = box_x + self.HEADER_SIDE_MARGIN
            header_y = box_y + self.HEADER_TOP_MARGIN
            header_width = box_width - (self.HEADER_SIDE_MARGIN * 2)
            header_height = self.BOX_HEADER_HEIGHT
            header_style = (
                f"text;html=1;strokeColor=none;fillColor=none;"
                f"align=center;verticalAlign=middle;whiteSpace=wrap;rounded=0;"
                f"fontSize={int(font_size)};fontStyle=1;"
            )
        else:
            header_x = box_x
            header_y = box_y
            header_width = box_width
            header_height = box_height
            header_style = (
                f"text;html=1;strokeColor=none;fillColor=none;"
                f"align=center;verticalAlign=middle;whiteSpace=wrap;rounded=0;"
                f"fontSize={int(font_size)};fontStyle=1;"
            )

        header_cell = ET.SubElement(parent, 'mxCell', {
            'id': header_cell_id,
            'value': str(box_name),
            'style': header_style,
            'parent': '1',
            'vertex': '1'
        })

        ET.SubElement(header_cell, 'mxGeometry', {
            'x': str(int(header_x)),
            'y': str(int(header_y)),
            'width': str(int(header_width)),
            'height': str(int(header_height)),
            'as': 'geometry'
        })

    def _create_component(self, comp: Dict, parent: ET.Element):
        cell_id = str(self._get_next_id())
        self.cell_map[comp['id']] = cell_id

        pos = self.positions.get(comp['id'], {})
        x = pos.get('x', 0)
        y = pos.get('y', 0)
        width = pos.get('width', 100)
        height = pos.get('height', 60)

        font_size = comp.get('font_size', 10)
        if pd.isna(font_size):
            font_size = 10

        comp_type = comp.get('type', '단일박스')

        if comp_type == '데이터베이스':
            style = (
                f"shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;"
                f"fillColor=#FFFFFF;strokeColor=#666666;"
                f"fontSize={int(font_size)};fontStyle=0;align=center;verticalAlign=middle;"
            )
        elif comp_type == '서비스':
            style = (
                f"rounded=1;whiteSpace=wrap;html=1;arcSize=10;"
                f"fillColor=#FFFFFF;strokeColor=#666666;"
                f"fontSize={int(font_size)};fontStyle=0;align=center;verticalAlign=middle;"
            )
        else:
            style = (
                f"rounded=0;whiteSpace=wrap;html=1;"
                f"fillColor=#FFFFFF;strokeColor=#666666;"
                f"fontSize={int(font_size)};fontStyle=0;align=center;verticalAlign=middle;"
            )

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
        for conn in connections:
            from_cell_id = self.cell_map.get(conn.get('from_id'))
            to_cell_id = self.cell_map.get(conn.get('to_id'))

            if not from_cell_id or not to_cell_id:
                continue

            cell_id = str(self._get_next_id())

            conn_type = conn.get('type', '데이터흐름')
            conn_style = CONNECTION_STYLES.get(conn_type, CONNECTION_STYLES['데이터흐름'])
            style = conn_style['style']

            line_style = LINE_STYLES.get(conn.get('style', '실선'), '')
            if line_style:
                style += line_style

            style += f"endArrow={conn_style['arrow']};"
            if conn_style['start_arrow'] != 'none':
                style += f"startArrow={conn_style['start_arrow']};"

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
        if pd.isna(color_name):
            return '#FFFFFF'
        return COLOR_MAP.get(str(color_name), '#FFFFFF')

    def _get_border_color(self, color_name: str) -> str:
        if pd.isna(color_name):
            return '#999999'
        return BORDER_COLOR_MAP.get(str(color_name), '#999999')

    def _get_next_id(self) -> int:
        current = self.cell_id_counter
        self.cell_id_counter += 1
        return current

    def _prettify_xml(self, element: ET.Element) -> str:
        from xml.dom import minidom
        rough_string = ET.tostring(element, encoding='unicode')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")