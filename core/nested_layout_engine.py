"""
AutoArchitect - Layout Engine
행번호 기반 레이아웃 계산
"""

from typing import Dict, List, Any
import pandas as pd


class NestedLayoutEngine:
    """행번호 기반 레이아웃 엔진"""

    def __init__(self):
        self.canvas_width = 1400
        self.canvas_height = 900
        self.positions = {}

        # 레이아웃 설정
        self.LEFT_MARGIN = 5
        self.RIGHT_MARGIN = 5
        self.GAP = 2

    def calculate_positions(self, data: Dict[str, Any], pattern: str = None) -> Dict[str, Dict]:
        """모든 요소의 위치 계산"""
        self.positions = {}

        # 캔버스 크기
        if 'config' in data:
            self.canvas_width = data['config'].get('캔버스너비', self.canvas_width)
            self.canvas_height = data['config'].get('캔버스높이', self.canvas_height)

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
        parent_groups = {}
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
        parent_groups = {}
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
        # 부모 영역
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
        row_groups = {}
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

    def detect_crossings(self, positions: Dict, connections: List[Dict]) -> int:
        """연결선 교차 개수 추정"""
        return 0  # 간단히 0 반환