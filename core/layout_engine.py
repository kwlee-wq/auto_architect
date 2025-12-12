"""
AutoArchitect - Layout Engine (v2.0 리팩토링)
- LayoutEngine: 기본형 레이아웃 (수평스택, 좌우분할 등)
- NestedLayoutEngine: 계층형 레이아웃 (행번호 기반)
"""

from typing import Dict, List, Any
from abc import ABC, abstractmethod
import pandas as pd

from utils.constants import (
    DEFAULT_CANVAS_WIDTH,
    DEFAULT_CANVAS_HEIGHT,
    DEFAULT_COMPONENT_MIN_WIDTH,
    DEFAULT_COMPONENT_MIN_HEIGHT
)


class BaseLayoutEngine(ABC):
    """레이아웃 엔진 기본 클래스"""

    def __init__(self):
        self.positions: Dict[str, Dict] = {}
        self.canvas_width = DEFAULT_CANVAS_WIDTH
        self.canvas_height = DEFAULT_CANVAS_HEIGHT

    @abstractmethod
    def calculate_positions(self, data: Dict[str, Any], pattern: str = None) -> Dict[str, Dict]:
        """위치 계산 (서브클래스에서 구현)"""
        pass

    def detect_crossings(self, positions: Dict, connections: List[Dict]) -> int:
        """연결선 교차 개수 추정"""
        crossings = 0

        for i, conn1 in enumerate(connections):
            pos1_from = positions.get(conn1.get('from_id'))
            pos1_to = positions.get(conn1.get('to_id'))

            if not pos1_from or not pos1_to:
                continue

            for conn2 in connections[i+1:]:
                pos2_from = positions.get(conn2.get('from_id'))
                pos2_to = positions.get(conn2.get('to_id'))

                if not pos2_from or not pos2_to:
                    continue

                if self._lines_intersect(
                        (pos1_from.get('x', 0), pos1_from.get('y', 0)),
                        (pos1_to.get('x', 0), pos1_to.get('y', 0)),
                        (pos2_from.get('x', 0), pos2_from.get('y', 0)),
                        (pos2_to.get('x', 0), pos2_to.get('y', 0))
                ):
                    crossings += 1

        return crossings

    def _lines_intersect(self, p1, p2, p3, p4) -> bool:
        """두 선분이 교차하는지 확인"""
        def ccw(A, B, C):
            return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])

        return ccw(p1, p3, p4) != ccw(p2, p3, p4) and ccw(p1, p2, p3) != ccw(p1, p2, p4)


class LayoutEngine(BaseLayoutEngine):
    """기본형 레이아웃 엔진 (LAYERS/COMPONENTS 기반)"""

    def calculate_positions(self, data: Dict[str, Any], pattern: str = '수평레이어스택') -> Dict[str, Dict]:
        """
        선택된 패턴으로 모든 컴포넌트 위치 계산

        Args:
            data: parse_to_dict()로 변환된 데이터
            pattern: 레이아웃 패턴

        Returns:
            위치 정보 딕셔너리
        """
        self.positions = {}

        self.canvas_width = data.get('config', {}).get('캔버스너비', DEFAULT_CANVAS_WIDTH)
        self.canvas_height = data.get('config', {}).get('캔버스높이', DEFAULT_CANVAS_HEIGHT)
        margin_percent = data.get('config', {}).get('여백비율', 15) / 100

        if pattern == '수평레이어스택':
            return self._horizontal_layer_stack(data, margin_percent)
        elif pattern == '좌우분할':
            return self._left_right_split(data, margin_percent)
        elif pattern == '중앙허브형':
            return self._central_hub(data, margin_percent)
        elif pattern == '좌우파이프라인':
            return self._left_right_pipeline(data, margin_percent)
        else:
            return self._horizontal_layer_stack(data, margin_percent)

    def _horizontal_layer_stack(self, data: Dict, margin_percent: float) -> Dict:
        """수평 레이어 스택 패턴"""
        positions = {}

        num_layers = len(data.get('layers', []))
        if num_layers == 0:
            return positions

        layer_height = self.canvas_height / num_layers
        current_y = 0

        for layer in data.get('layers', []):
            positions[layer['id']] = {
                'x': 0,
                'y': current_y,
                'width': self.canvas_width,
                'height': layer_height
            }

            # 이 레이어의 컴포넌트들
            layer_components = [
                c for c in data.get('components', [])
                if c.get('layer_id') == layer['id']
            ]

            if layer_components:
                margin = 40
                gap = 20
                num_comps = len(layer_components)

                available_width = self.canvas_width - (margin * 2)
                comp_width = (available_width - (gap * (num_comps - 1))) / num_comps
                comp_height = layer_height * 0.7

                start_x = margin
                comp_y = current_y + (layer_height - comp_height) / 2

                for idx, comp in enumerate(layer_components):
                    comp_x = start_x + idx * (comp_width + gap)
                    positions[comp['id']] = {
                        'x': comp_x,
                        'y': comp_y,
                        'width': comp_width,
                        'height': comp_height
                    }

            current_y += layer_height

        return positions

    def _left_right_split(self, data: Dict, margin_percent: float) -> Dict:
        """좌우 분할 패턴"""
        positions = {}

        num_layers = len(data.get('layers', []))
        if num_layers == 0:
            return positions

        section_width = self.canvas_width / num_layers

        for idx, layer in enumerate(data.get('layers', [])):
            x_offset = idx * section_width

            positions[layer['id']] = {
                'x': x_offset,
                'y': 0,
                'width': section_width,
                'height': self.canvas_height
            }

            layer_components = [
                c for c in data.get('components', [])
                if c.get('layer_id') == layer['id']
            ]

            if layer_components:
                comp_height = self.canvas_height / (len(layer_components) + 1)

                for comp_idx, comp in enumerate(layer_components):
                    positions[comp['id']] = {
                        'x': x_offset + section_width * 0.1,
                        'y': (comp_idx + 0.5) * comp_height,
                        'width': section_width * 0.8,
                        'height': comp_height * 0.7
                    }

        return positions

    def _central_hub(self, data: Dict, margin_percent: float) -> Dict:
        """중앙 허브형 패턴"""
        # 기본적으로 수평 스택으로 처리
        return self._horizontal_layer_stack(data, margin_percent)

    def _left_right_pipeline(self, data: Dict, margin_percent: float) -> Dict:
        """좌우 파이프라인 패턴"""
        return self._left_right_split(data, margin_percent)


class NestedLayoutEngine(BaseLayoutEngine):
    """계층형 레이아웃 엔진 (행번호 기반)"""

    def __init__(self):
        super().__init__()
        self.LEFT_MARGIN = 5
        self.RIGHT_MARGIN = 5
        self.GAP = 2

    def calculate_positions(self, data: Dict[str, Any], pattern: str = None) -> Dict[str, Dict]:
        """
        계층형 데이터의 위치 계산

        Args:
            data: parse_to_dict()로 변환된 데이터
            pattern: 미사용 (계층형은 자동 레이아웃)

        Returns:
            위치 정보 딕셔너리
        """
        self.positions = {}

        # 캔버스 크기
        config = data.get('config', {})
        self.canvas_width = config.get('캔버스너비', DEFAULT_CANVAS_WIDTH)
        self.canvas_height = config.get('캔버스높이', DEFAULT_CANVAS_HEIGHT)

        # 1. 레이어 위치 계산
        self._calculate_layer_positions(data.get('layers', []))

        # 2. 박스 위치 계산
        self._calculate_box_positions(data.get('boxes', []))

        # 3. 컴포넌트 위치 계산
        self._calculate_component_positions(data.get('components', []))

        return self.positions

    def _calculate_layer_positions(self, layers: List[Dict]):
        """레이어 위치 계산"""
        current_y = 0

        for layer in layers:
            layer_id = layer['id']
            height_percent = layer.get('height_percent', 100 / max(len(layers), 1))

            height_px = self.canvas_height * (height_percent / 100)

            self.positions[layer_id] = {
                'x': 0,
                'y': current_y,
                'width': self.canvas_width,
                'height': height_px
            }

            current_y += height_px

    def _calculate_box_positions(self, boxes: List[Dict]):
        """박스 위치 계산 - 행번호 기반"""
        # 부모별로 그룹화
        parent_groups: Dict[str, List[Dict]] = {}
        for box in boxes:
            parent_id = box.get('parent_id')
            if parent_id not in parent_groups:
                parent_groups[parent_id] = []
            parent_groups[parent_id].append(box)

        # 각 그룹 내에서 행 기반 배치
        for parent_id, children in parent_groups.items():
            self._layout_items_by_row(children, parent_id)

    def _calculate_component_positions(self, components: List[Dict]):
        """컴포넌트 위치 계산"""
        # 부모별로 그룹화
        parent_groups: Dict[str, List[Dict]] = {}
        for comp in components:
            parent_id = comp.get('parent_id')
            if parent_id not in parent_groups:
                parent_groups[parent_id] = []
            parent_groups[parent_id].append(comp)

        # 각 그룹 내에서 행 기반 배치
        for parent_id, children in parent_groups.items():
            self._layout_items_by_row(children, parent_id)

    def _layout_items_by_row(self, items: List[Dict], parent_id: str):
        """행 기반 배치"""
        # 부모 영역 가져오기
        if parent_id and parent_id in self.positions:
            parent_pos = self.positions[parent_id]
        else:
            parent_pos = {
                'x': 0,
                'y': 0,
                'width': self.canvas_width,
                'height': self.canvas_height
            }

        # 행번호별로 그룹화
        row_groups: Dict[int, List[Dict]] = {}
        for item in items:
            row_num = item.get('row_number', 1)
            if pd.isna(row_num):
                row_num = 1
            row_num = int(row_num)
            if row_num not in row_groups:
                row_groups[row_num] = []
            row_groups[row_num].append(item)

        # 각 행별로 균등 배치
        for row_num, row_items in row_groups.items():
            self._layout_single_row(row_items, parent_pos)

    def _layout_single_row(self, items: List[Dict], parent_pos: Dict):
        """한 행의 아이템들을 균등 배치"""
        count = len(items)
        if count == 0:
            return

        # 사용 가능한 너비 계산
        available_width = 100 - self.LEFT_MARGIN - self.RIGHT_MARGIN
        total_gap = self.GAP * (count - 1) if count > 1 else 0
        item_width = (available_width - total_gap) / count

        # 각 아이템 배치
        for i, item in enumerate(items):
            # X% 계산
            x_percent = self.LEFT_MARGIN + (item_width + self.GAP) * i

            # Y%, 높이% 가져오기
            y_percent = item.get('y_percent', 0)
            if pd.isna(y_percent):
                y_percent = 0
            height_percent = item.get('height_percent', 100)
            if pd.isna(height_percent):
                height_percent = 100

            # 픽셀 계산
            x_px = parent_pos['x'] + (parent_pos['width'] * (x_percent / 100))
            y_px = parent_pos['y'] + (parent_pos['height'] * (y_percent / 100))
            width_px = parent_pos['width'] * (item_width / 100)
            height_px = parent_pos['height'] * (height_percent / 100)

            # 저장
            item_id = item['id']
            self.positions[item_id] = {
                'x': x_px,
                'y': y_px,
                'width': width_px,
                'height': height_px
            }


def create_layout_engine(is_nested: bool = False) -> BaseLayoutEngine:
    """적절한 레이아웃 엔진 반환"""
    if is_nested:
        return NestedLayoutEngine()
    return LayoutEngine()
