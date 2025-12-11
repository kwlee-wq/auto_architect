"""
AutoArchitect - Draw.io XML 생성기
"""

import xml.etree.ElementTree as ET
from typing import Dict, List, Any, Tuple
from datetime import datetime
import uuid

from utils.constants import (
    COLOR_MAP,
    BORDER_COLOR_MAP,
    COMPONENT_STYLES,
    CONNECTION_STYLES,
    LINE_STYLES,
    TEXT_SIZES,
    DEFAULT_CANVAS_WIDTH,
    DEFAULT_CANVAS_HEIGHT
)


class DrawioGenerator:
    """Draw.io XML 파일 생성기"""

    def __init__(self):
        self.cell_id_counter = 2  # 0, 1은 예약
        self.positions = {}  # {component_id: {'x': ..., 'y': ..., 'width': ..., 'height': ...}}

    def generate_xml(self, data: Dict[str, Any], positions: Dict[str, Dict]) -> str:
        """
        전체 Draw.io XML 생성

        Args:
            data: parse_to_dict()로 변환된 데이터
            positions: 레이아웃 엔진에서 계산된 위치 정보

        Returns:
            Draw.io XML 문자열
        """
        self.positions = positions
        self.cell_id_counter = 2

        # 캔버스 크기
        canvas_width = data['config'].get('캔버스너비', DEFAULT_CANVAS_WIDTH)
        canvas_height = data['config'].get('캔버스높이', DEFAULT_CANVAS_HEIGHT)
        diagram_name = data['config'].get('다이어그램명', 'System Architecture')

        # XML 루트 생성
        root = self._create_root_structure(diagram_name, canvas_width, canvas_height)

        # mxGraphModel > root 가져오기
        graph_root = root.find('.//root')

        # 레이어 생성
        layer_cells = {}
        for layer in data['layers']:
            layer_cell = self._create_layer(layer, canvas_width, graph_root)
            layer_cells[layer['id']] = layer_cell

        # 컴포넌트 생성
        component_cells = {}
        for component in data['components']:
            # 해당 레이어의 parent cell ID 찾기
            parent_cell = layer_cells.get(component['layer_id'])
            parent_id = parent_cell.get('id') if parent_cell else '1'

            comp_cell = self._create_component(component, parent_id, graph_root)
            component_cells[component['id']] = comp_cell

        # 서브 컴포넌트 생성
        if 'sub_components' in data:
            self._create_sub_components(
                data['sub_components'],
                component_cells,
                graph_root
            )

        # 연결선 생성
        if 'connections' in data:
            self._create_connections(
                data['connections'],
                component_cells,
                graph_root
            )

        # 그룹 생성 (옵션) - 일단 비활성화 (레이아웃 문제)
        # if 'groups' in data:
        #     self._create_groups(
        #         data['groups'],
        #         component_cells,
        #         graph_root
        #     )

        # XML을 문자열로 변환
        xml_str = self._prettify_xml(root)
        return xml_str

    def _create_root_structure(self, diagram_name: str, width: int, height: int) -> ET.Element:
        """XML 기본 구조 생성"""
        # mxfile
        mxfile = ET.Element('mxfile', {
            'host': 'app.diagrams.net',
            'modified': datetime.now().isoformat(),
            'agent': 'AutoArchitect',
            'version': '1.0',
            'type': 'device'
        })

        # diagram
        diagram = ET.SubElement(mxfile, 'diagram', {
            'name': diagram_name,
            'id': str(uuid.uuid4())
        })

        # mxGraphModel
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

        # root
        root = ET.SubElement(graph_model, 'root')

        # 기본 cell 2개 (필수)
        ET.SubElement(root, 'mxCell', {'id': '0'})
        ET.SubElement(root, 'mxCell', {'id': '1', 'parent': '0'})

        return mxfile

    def _create_layer(self, layer: Dict, canvas_width: int, parent: ET.Element) -> Dict:
        """레이어를 일반 박스로 생성 (Swimlane 대신)"""
        cell_id = str(self._get_next_id())

        # 위치 정보 가져오기
        layer_pos = self.positions.get(layer['id'], {})
        x = layer_pos.get('x', 0)
        y = layer_pos.get('y', 0)
        width = layer_pos.get('width', canvas_width)
        height = layer_pos.get('height', 200)

        # 배경색, 테두리색
        bg_color = COLOR_MAP.get(layer['bg_color'], '#FFFFFF')
        border_color = BORDER_COLOR_MAP.get(layer['border_color'], '#000000')

        # 일반 박스 스타일 (Swimlane 대신)
        style = (
            f"rounded=0;whiteSpace=wrap;html=1;"
            f"fillColor={bg_color};strokeColor={border_color};"
            f"fontSize=12;fontStyle=1;align=center;verticalAlign=top;"
            f"spacingTop=10;"
        )

        # mxCell 생성
        cell = ET.SubElement(parent, 'mxCell', {
            'id': cell_id,
            'value': layer['name'],
            'style': style,
            'parent': '1',
            'vertex': '1'
        })

        # geometry
        ET.SubElement(cell, 'mxGeometry', {
            'x': str(int(x)),
            'y': str(int(y)),
            'width': str(int(width)),
            'height': str(int(height)),
            'as': 'geometry'
        })

        return {'id': cell_id, 'layer_data': layer}

    def _create_component(self, component: Dict, parent_id: str, parent: ET.Element) -> Dict:
        """컴포넌트 생성 - 레이어의 자식으로"""
        cell_id = str(self._get_next_id())

        # 위치 정보
        comp_pos = self.positions.get(component['id'], {})
        x = comp_pos.get('x', 100)
        y = comp_pos.get('y', 50)
        width = comp_pos.get('width', 180)
        height = comp_pos.get('height', 80)

        # 컴포넌트 타입별 스타일
        comp_style_template = COMPONENT_STYLES.get(component['type'], COMPONENT_STYLES['단일박스'])

        # 스타일 문자열 생성
        style = comp_style_template['style']

        # 배경색 설정 (흰색 배경)
        style = style.replace('{fill}', '#FFFFFF')
        style = style.replace('{stroke}', '#666666')

        # 텍스트 설정
        style += 'fontSize=11;fontStyle=1;align=center;verticalAlign=middle;'

        # mxCell 생성 - parent를 '1'로 (레이어 위에 배치)
        cell = ET.SubElement(parent, 'mxCell', {
            'id': cell_id,
            'value': component['name'],
            'style': style,
            'parent': '1',  # 레이어가 아닌 루트에 배치
            'vertex': '1'
        })

        # geometry - 절대 좌표 사용
        ET.SubElement(cell, 'mxGeometry', {
            'x': str(int(x)),
            'y': str(int(y)),
            'width': str(int(width)),
            'height': str(int(height)),
            'as': 'geometry'
        })

        return {'id': cell_id, 'component_data': component}

    def _create_sub_components(self, sub_components: List[Dict],
                               component_cells: Dict, parent: ET.Element):
        """서브 컴포넌트 생성 - 부모 컴포넌트 내부에 배치"""
        # 부모별로 그룹화
        by_parent = {}
        for sub in sub_components:
            parent_id = sub['parent_id']
            if parent_id not in by_parent:
                by_parent[parent_id] = []
            by_parent[parent_id].append(sub)

        # 각 부모별로 서브 컴포넌트 배치
        for parent_id, subs in by_parent.items():
            parent_cell = component_cells.get(parent_id)
            if not parent_cell:
                continue

            parent_cell_id = parent_cell['id']

            # 부모 컴포넌트의 위치 정보
            parent_pos = self.positions.get(parent_id, {})
            parent_width = parent_pos.get('width', 180)
            parent_height = parent_pos.get('height', 80)

            num_subs = len(subs)

            # 서브 컴포넌트 크기
            sub_width = 65
            sub_height = 28
            gap_x = 8
            gap_y = 8

            # 한 줄에 몇 개씩 배치할지 계산
            max_cols = int((parent_width - 20) / (sub_width + gap_x))
            cols = min(max_cols, num_subs) if max_cols > 0 else 1
            rows = (num_subs + cols - 1) // cols

            # 전체 그리드 크기
            grid_width = cols * sub_width + (cols - 1) * gap_x
            grid_height = rows * sub_height + (rows - 1) * gap_y

            # 시작 위치 (중앙 정렬, 위쪽 여백)
            start_x = (parent_width - grid_width) / 2
            start_y = 25  # 타이틀 공간

            for idx, sub in enumerate(sorted(subs, key=lambda s: s['order'])):
                row = idx // cols
                col = idx % cols

                cell_id = str(self._get_next_id())

                # 상대 위치 계산
                rel_x = start_x + col * (sub_width + gap_x)
                rel_y = start_y + row * (sub_height + gap_y)

                # 스타일 - 더 작은 폰트
                style = (
                    'rounded=0;whiteSpace=wrap;html=1;'
                    'fillColor=#E8F5E9;strokeColor=#4CAF50;'
                    'fontSize=10;fontStyle=0;'
                )

                # mxCell 생성
                cell = ET.SubElement(parent, 'mxCell', {
                    'id': cell_id,
                    'value': sub['name'],
                    'style': style,
                    'parent': parent_cell_id,
                    'vertex': '1'
                })

                # geometry - 부모 기준 상대 좌표
                ET.SubElement(cell, 'mxGeometry', {
                    'x': str(int(rel_x)),
                    'y': str(int(rel_y)),
                    'width': str(int(sub_width)),
                    'height': str(int(sub_height)),
                    'as': 'geometry'
                })

    def _create_connections(self, connections: List[Dict],
                            component_cells: Dict, parent: ET.Element):
        """연결선 생성"""
        for conn in connections:
            from_cell = component_cells.get(conn['from_id'])
            to_cell = component_cells.get(conn['to_id'])

            if not from_cell or not to_cell:
                continue

            cell_id = str(self._get_next_id())

            # 연결 타입별 스타일
            conn_style_data = CONNECTION_STYLES.get(conn['type'], CONNECTION_STYLES['데이터흐름'])
            style = conn_style_data['style']

            # 선 스타일 추가
            line_style = LINE_STYLES.get(conn.get('style', '실선'), '')
            if line_style:
                style += line_style

            # 화살표 설정
            style += f"endArrow={conn_style_data['arrow']};"
            if conn_style_data['start_arrow'] != 'none':
                style += f"startArrow={conn_style_data['start_arrow']};"

            # mxCell 생성
            cell = ET.SubElement(parent, 'mxCell', {
                'id': cell_id,
                'value': conn.get('label', ''),
                'style': style,
                'parent': '1',
                'edge': '1',
                'source': from_cell['id'],
                'target': to_cell['id']
            })

            # geometry
            ET.SubElement(cell, 'mxGeometry', {
                'relative': '1',
                'as': 'geometry'
            })

    def _create_groups(self, groups: List[Dict],
                       component_cells: Dict, parent: ET.Element):
        """그룹 영역 생성 (점선 테두리)"""
        for group in groups:
            # 포함된 컴포넌트들의 위치로 경계 박스 계산
            comp_positions = []
            for comp_id in group['component_ids']:
                if comp_id in self.positions:
                    comp_positions.append(self.positions[comp_id])

            if not comp_positions:
                continue

            # 경계 박스 계산
            min_x = min(pos['x'] for pos in comp_positions) - 20
            min_y = min(pos['y'] for pos in comp_positions) - 40
            max_x = max(pos['x'] + pos['width'] for pos in comp_positions) + 20
            max_y = max(pos['y'] + pos['height'] for pos in comp_positions) + 20

            width = max_x - min_x
            height = max_y - min_y

            cell_id = str(self._get_next_id())

            # 그룹 스타일 (반투명 배경, 점선 테두리)
            opacity = group.get('bg_opacity', '5%').replace('%', '')
            style = (
                f"rounded=0;whiteSpace=wrap;html=1;dashed=1;dashPattern=5 5;"
                f"fillColor=#FFFFFF;fillOpacity={opacity};strokeColor=#FF0000;"
                f"fontStyle=1;fontSize=11;"
            )

            # mxCell 생성
            cell = ET.SubElement(parent, 'mxCell', {
                'id': cell_id,
                'value': group['name'],
                'style': style,
                'parent': '1',
                'vertex': '1'
            })

            # geometry
            ET.SubElement(cell, 'mxGeometry', {
                'x': str(int(min_x)),
                'y': str(int(min_y)),
                'width': str(int(width)),
                'height': str(int(height)),
                'as': 'geometry'
            })

    def _get_next_id(self) -> int:
        """다음 Cell ID 반환"""
        current = self.cell_id_counter
        self.cell_id_counter += 1
        return current

    def _prettify_xml(self, element: ET.Element) -> str:
        """XML을 보기 좋게 포맷팅"""
        from xml.dom import minidom

        rough_string = ET.tostring(element, encoding='unicode')
        reparsed = minidom.parseString(rough_string)

        # 선언문 포함하여 반환
        return reparsed.toprettyxml(indent="  ")