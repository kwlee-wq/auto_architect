"""
AutoArchitect - Draw.io XML Generator (v2.0 리팩토링)
- DrawioGenerator: 기본형 (LAYERS/COMPONENTS)
- NestedDrawioGenerator: 계층형 (LAYERS/BOXES/COMPONENTS)
"""

import xml.etree.ElementTree as ET
from typing import Dict, List, Any
from datetime import datetime
from abc import ABC, abstractmethod
import uuid
import pandas as pd

from utils.constants import (
    COLOR_MAP,
    BORDER_COLOR_MAP,
    COMPONENT_STYLES,
    CONNECTION_STYLES,
    LINE_STYLES,
    TEXT_SIZES,
    DEFAULT_CANVAS_WIDTH,
    DEFAULT_CANVAS_HEIGHT,
    LAYER_HEADER_HEIGHT,
    BOX_HEADER_HEIGHT,
    HEADER_TOP_MARGIN,
    HEADER_SIDE_MARGIN,
    get_color,
    get_border_color,
    get_connection_style,
    get_line_style
)


class BaseDrawioGenerator(ABC):
    """Draw.io XML 생성기 기본 클래스"""

    def __init__(self):
        self.cell_id_counter = 2  # 0, 1은 예약
        self.positions: Dict[str, Dict] = {}
        self.cell_map: Dict[str, str] = {}  # component_id -> cell_id 매핑

    def _get_next_id(self) -> int:
        """다음 Cell ID 반환"""
        current = self.cell_id_counter
        self.cell_id_counter += 1
        return current

    def _create_root_structure(self, diagram_name: str, width: int, height: int) -> ET.Element:
        """XML 기본 구조 생성"""
        mxfile = ET.Element('mxfile', {
            'host': 'app.diagrams.net',
            'modified': datetime.now().isoformat(),
            'agent': 'AutoArchitect',
            'version': '2.0',
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

    def _create_connections(self, connections: List[Dict], parent: ET.Element):
        """연결선 생성"""
        for conn in connections:
            from_cell_id = self.cell_map.get(conn.get('from_id'))
            to_cell_id = self.cell_map.get(conn.get('to_id'))

            if not from_cell_id or not to_cell_id:
                continue

            cell_id = str(self._get_next_id())

            # 연결 타입 스타일
            conn_type = conn.get('type', '데이터흐름')
            conn_style = get_connection_style(conn_type)
            style = conn_style['style']

            # 선 스타일 추가
            line_style = get_line_style(conn.get('style', '실선'))
            if line_style:
                style += line_style

            # 화살표 설정
            style += f"endArrow={conn_style['arrow']};"
            if conn_style['start_arrow'] != 'none':
                style += f"startArrow={conn_style['start_arrow']};"

            # 라벨
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

    def _prettify_xml(self, element: ET.Element) -> str:
        """XML을 보기 좋게 포맷팅"""
        from xml.dom import minidom
        rough_string = ET.tostring(element, encoding='unicode')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")

    @abstractmethod
    def generate_xml(self, data: Dict[str, Any], positions: Dict[str, Dict]) -> str:
        """XML 생성 (서브클래스에서 구현)"""
        pass


class DrawioGenerator(BaseDrawioGenerator):
    """기본형 Draw.io XML 생성기"""

    def generate_xml(self, data: Dict[str, Any], positions: Dict[str, Dict]) -> str:
        """전체 Draw.io XML 생성"""
        self.positions = positions
        self.cell_id_counter = 2
        self.cell_map = {}

        # 캔버스 크기
        canvas_width = data.get('config', {}).get('캔버스너비', DEFAULT_CANVAS_WIDTH)
        canvas_height = data.get('config', {}).get('캔버스높이', DEFAULT_CANVAS_HEIGHT)
        diagram_name = data.get('config', {}).get('다이어그램명', 'System Architecture')

        # XML 루트 생성
        root = self._create_root_structure(diagram_name, canvas_width, canvas_height)
        graph_root = root.find('.//root')

        # 레이어 생성
        layer_cells = {}
        for layer in data.get('layers', []):
            layer_cell = self._create_layer(layer, canvas_width, graph_root)
            layer_cells[layer['id']] = layer_cell

        # 컴포넌트 생성
        for component in data.get('components', []):
            parent_cell = layer_cells.get(component.get('layer_id'))
            parent_id = parent_cell.get('id') if parent_cell else '1'
            self._create_component(component, parent_id, graph_root)

        # 서브 컴포넌트 생성
        if data.get('sub_components'):
            self._create_sub_components(data['sub_components'], graph_root)

        # 연결선 생성
        if data.get('connections'):
            self._create_connections(data['connections'], graph_root)

        return self._prettify_xml(root)

    def _create_layer(self, layer: Dict, canvas_width: int, parent: ET.Element) -> Dict:
        """레이어 생성"""
        cell_id = str(self._get_next_id())

        pos = self.positions.get(layer['id'], {})
        x = pos.get('x', 0)
        y = pos.get('y', 0)
        width = pos.get('width', canvas_width)
        height = pos.get('height', 200)

        bg_color = get_color(layer.get('bg_color', '흰색'))
        border_color = get_border_color(layer.get('border_color', '검정'))

        style = (
            f"rounded=0;whiteSpace=wrap;html=1;"
            f"fillColor={bg_color};strokeColor={border_color};"
            f"fontSize=12;fontStyle=1;align=center;verticalAlign=top;"
            f"spacingTop=10;"
        )

        cell = ET.SubElement(parent, 'mxCell', {
            'id': cell_id,
            'value': layer.get('name', ''),
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

        self.cell_map[layer['id']] = cell_id
        return {'id': cell_id, 'layer_data': layer}

    def _create_component(self, component: Dict, parent_id: str, parent: ET.Element):
        """컴포넌트 생성"""
        cell_id = str(self._get_next_id())

        pos = self.positions.get(component['id'], {})
        x = pos.get('x', 100)
        y = pos.get('y', 50)
        width = pos.get('width', 180)
        height = pos.get('height', 80)

        # 컴포넌트 타입별 스타일
        comp_type = component.get('type', '단일박스')
        comp_style_data = COMPONENT_STYLES.get(comp_type, COMPONENT_STYLES['단일박스'])
        style = comp_style_data['style']

        # 색상 설정
        style = style.replace('{fill}', '#FFFFFF')
        style = style.replace('{stroke}', '#666666')
        style += 'fontSize=11;fontStyle=1;align=center;verticalAlign=middle;'

        cell = ET.SubElement(parent, 'mxCell', {
            'id': cell_id,
            'value': component.get('name', ''),
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

        self.cell_map[component['id']] = cell_id

    def _create_sub_components(self, sub_components: List[Dict], parent: ET.Element):
        """서브 컴포넌트 생성"""
        # 부모별로 그룹화
        by_parent: Dict[str, List[Dict]] = {}
        for sub in sub_components:
            parent_id = sub.get('parent_id')
            if parent_id not in by_parent:
                by_parent[parent_id] = []
            by_parent[parent_id].append(sub)

        for parent_id, subs in by_parent.items():
            parent_cell_id = self.cell_map.get(parent_id)
            if not parent_cell_id:
                continue

            parent_pos = self.positions.get(parent_id, {})
            parent_width = parent_pos.get('width', 180)
            parent_height = parent_pos.get('height', 80)

            # 서브 컴포넌트 크기
            sub_width = 65
            sub_height = 28
            gap_x = 8
            gap_y = 8

            num_subs = len(subs)
            max_cols = int((parent_width - 20) / (sub_width + gap_x))
            cols = min(max_cols, num_subs) if max_cols > 0 else 1
            rows = (num_subs + cols - 1) // cols

            grid_width = cols * sub_width + (cols - 1) * gap_x
            start_x = (parent_width - grid_width) / 2
            start_y = 25

            for idx, sub in enumerate(sorted(subs, key=lambda s: s.get('order', 0))):
                row = idx // cols
                col = idx % cols

                cell_id = str(self._get_next_id())

                rel_x = start_x + col * (sub_width + gap_x)
                rel_y = start_y + row * (sub_height + gap_y)

                style = (
                    'rounded=0;whiteSpace=wrap;html=1;'
                    'fillColor=#E8F5E9;strokeColor=#4CAF50;'
                    'fontSize=10;fontStyle=0;'
                )

                cell = ET.SubElement(parent, 'mxCell', {
                    'id': cell_id,
                    'value': sub.get('name', ''),
                    'style': style,
                    'parent': parent_cell_id,
                    'vertex': '1'
                })

                ET.SubElement(cell, 'mxGeometry', {
                    'x': str(int(rel_x)),
                    'y': str(int(rel_y)),
                    'width': str(int(sub_width)),
                    'height': str(int(sub_height)),
                    'as': 'geometry'
                })


class NestedDrawioGenerator(BaseDrawioGenerator):
    """계층형 Draw.io XML 생성기 (헤더 영역 확보)"""

    def __init__(self):
        super().__init__()
        self.box_children: Dict[str, int] = {}

    def generate_xml(self, data: Dict[str, Any], positions: Dict[str, Dict]) -> str:
        """전체 XML 생성"""
        self.positions = positions
        self.cell_id_counter = 2
        self.cell_map = {}

        # 자식 요소 개수 계산
        self._calculate_children_count(data)

        # 캔버스 크기
        canvas_width = data.get('config', {}).get('캔버스너비', DEFAULT_CANVAS_WIDTH)
        canvas_height = data.get('config', {}).get('캔버스높이', DEFAULT_CANVAS_HEIGHT)
        diagram_name = data.get('config', {}).get('다이어그램명', 'System Architecture')

        # XML 루트 생성
        root = self._create_root_structure(diagram_name, canvas_width, canvas_height)
        graph_root = root.find('.//root')

        # 레이어 생성 (헤더 분리)
        for layer in data.get('layers', []):
            self._create_layer_with_header(layer, graph_root)

        # 박스 생성 (헤더 분리)
        for box in data.get('boxes', []):
            self._create_box_with_header(box, graph_root)

        # 컴포넌트 생성
        for comp in data.get('components', []):
            self._create_component(comp, graph_root)

        # 연결선 생성
        if data.get('connections'):
            self._create_connections(data['connections'], graph_root)

        return self._prettify_xml(root)

    def _calculate_children_count(self, data: Dict[str, Any]):
        """각 요소의 자식 개수 계산"""
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
        """자식 요소가 있는지 확인"""
        return self.box_children.get(item_id, 0) > 0

    def _create_layer_with_header(self, layer: Dict, parent: ET.Element):
        """레이어 생성 (배경 + 헤더 텍스트 분리)"""
        cell_id = str(self._get_next_id())
        self.cell_map[layer['id']] = cell_id

        pos = self.positions.get(layer['id'], {})
        x = pos.get('x', 0)
        y = pos.get('y', 0)
        width = pos.get('width', 1200)
        height = pos.get('height', 200)

        bg_color = get_color(layer.get('bg_color', '흰색'))
        layer_name = layer.get('name', '')

        # 배경 셀 (텍스트 없음)
        style = f"rounded=0;whiteSpace=wrap;html=1;fillColor={bg_color};strokeColor=none;"

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

        # 헤더 텍스트 셀
        header_cell_id = str(self._get_next_id())
        header_x = x + (width / 2) - 150
        header_y = y + HEADER_TOP_MARGIN
        header_width = 300
        header_height = LAYER_HEADER_HEIGHT

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
        """박스 생성 (배경 + 헤더 텍스트 분리)"""
        box_id = box['id']
        has_children = self._has_children(box_id)

        pos = self.positions.get(box_id, {})
        box_x = pos.get('x', 0)
        box_y = pos.get('y', 0)
        box_width = pos.get('width', 200)
        box_height = pos.get('height', 100)

        bg_color = get_color(box.get('bg_color', '연회색'))
        border_color = get_border_color(box.get('border_color', '회색'))
        font_size = box.get('font_size', 11)
        if pd.isna(font_size):
            font_size = 11

        box_name = box.get('name', '')
        if pd.isna(box_name):
            box_name = ''

        cell_id = str(self._get_next_id())
        self.cell_map[box_id] = cell_id

        # 배경 셀
        style = f"rounded=0;whiteSpace=wrap;html=1;fillColor={bg_color};strokeColor={border_color};"

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

        # 헤더/텍스트 셀
        header_cell_id = str(self._get_next_id())

        if has_children:
            # 자식이 있으면 상단 헤더 영역에 텍스트
            header_x = box_x + HEADER_SIDE_MARGIN
            header_y = box_y + HEADER_TOP_MARGIN
            header_width = box_width - (HEADER_SIDE_MARGIN * 2)
            header_height = BOX_HEADER_HEIGHT
        else:
            # 자식이 없으면 중앙에 텍스트
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
        """컴포넌트 생성"""
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

        # 타입별 스타일
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


def create_drawio_generator(is_nested: bool = False) -> BaseDrawioGenerator:
    """적절한 Draw.io 생성기 반환"""
    if is_nested:
        return NestedDrawioGenerator()
    return DrawioGenerator()
