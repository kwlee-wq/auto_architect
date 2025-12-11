"""
AutoArchitect - 통합 Layout Engine
v5.0 (X%, 너비% 기반) + v6.0 (행번호 기반) 모두 지원
"""

from typing import Dict, List, Any
import pandas as pd


class UnifiedLayoutEngine:
    """v5.0과 v6.0 레이아웃 모두 지원하는 통합 엔진"""

    def __init__(self, canvas_width: int, canvas_height: int, excel_version: str = 'v5'):
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        self.excel_version = excel_version
        self.positions = {}

        # v6.0 레이아웃 설정
        self.LEFT_MARGIN = 5
        self.RIGHT_MARGIN = 5
        self.GAP = 2

    def calculate_all_positions(self, data: Dict[str, Any]) -> Dict[str, Dict]:
        """모든 요소의 위치 계산 (버전 자동 감지)"""
        self.positions = {}

        # 버전 자동 감지 (data에서)
        if 'boxes' in data and len(data['boxes']) > 0:
            first_box = data['boxes'][0]
            if 'row_number' in first_box:
                self.excel_version = 'v6'
            else:
                self.excel_version = 'v5'

        print(f"🔧 Layout Engine: {self.excel_version} 모드")

        # 1. 레이어 위치 계산
        self._calculate_layer_positions(data['layers'])

        # 2. 박스 위치 계산 (버전별)
        if self.excel_version == 'v6':
            self._calculate_boxes_v6(data['boxes'])
        else:
            self._calculate_boxes_v5(data['boxes'])

        # 3. 컴포넌트 위치 계산 (버전별)
        if self.excel_version == 'v6':
            self._calculate_components_v6(data['components'])
        else:
            self._calculate_components_v5(data['components'])

        return self.positions

    def _calculate_layer_positions(self, layers: List[Dict]):
        """레이어 위치 계산 (공통)"""
        current_y = 0

        for layer in layers:
            layer_id = layer['id']
            height_percent = layer['height_percent']

            height_px = self.canvas_height * (height_percent / 100)

            self.positions[layer_id] = {
                'x': 0,
                'y': current_y,
                'width': self.canvas_width,
                'height': height_px
            }

            current_y += height_px

    # ==================== v5.0 방식 ====================

    def _calculate_boxes_v5(self, boxes: List[Dict]):
        """v5.0: X%, 너비% 직접 사용"""
        for box in boxes:
            parent_id = box.get('parent_id')

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

            # 절대 위치 계산
            x_px = parent_pos['x'] + (parent_pos['width'] * (box['x_percent'] / 100))
            y_px = parent_pos['y'] + (parent_pos['height'] * (box['y_percent'] / 100))
            width_px = parent_pos['width'] * (box['width_percent'] / 100)
            height_px = parent_pos['height'] * (box['height_percent'] / 100)

            self.positions[box['id']] = {
                'x': x_px,
                'y': y_px,
                'width': width_px,
                'height': height_px
            }

    def _calculate_components_v5(self, components: List[Dict]):
        """v5.0: X%, 너비% 직접 사용"""
        for comp in components:
            parent_id = comp.get('parent_id')

            # 부모 영역
            if parent_id and parent_id in self.positions:
                parent_pos = self.positions[parent_id]
            else:
                continue

            # 절대 위치 계산
            x_px = parent_pos['x'] + (parent_pos['width'] * (comp['x_percent'] / 100))
            y_px = parent_pos['y'] + (parent_pos['height'] * (comp['y_percent'] / 100))
            width_px = parent_pos['width'] * (comp['width_percent'] / 100)
            height_px = parent_pos['height'] * (comp['height_percent'] / 100)

            self.positions[comp['id']] = {
                'x': x_px,
                'y': y_px,
                'width': width_px,
                'height': height_px
            }

    # ==================== v6.0 방식 ====================

    def _calculate_boxes_v6(self, boxes: List[Dict]):
        """v6.0: 행 기반 자동 배치"""
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

    def _calculate_components_v6(self, components: List[Dict]):
        """v6.0: 행 기반 자동 배치"""
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
        """행 기반 자동 배치 (v6.0)"""
        # 부모 영역
        if parent_id in self.positions:
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
            if row_num not in row_groups:
                row_groups[row_num] = []
            row_groups[row_num].append(item)

        # 각 행별로 균등 배치
        for row_num, row_items in row_groups.items():
            self._layout_single_row(row_items, parent_pos)

    def _layout_single_row(self, items: List[Dict], parent_pos: Dict):
        """한 행의 아이템들을 균등 배치 (v6.0)"""
        count = len(items)

        # 사용 가능한 너비 계산
        available_width = 100 - self.LEFT_MARGIN - self.RIGHT_MARGIN
        total_gap = self.GAP * (count - 1) if count > 1 else 0
        item_width = (available_width - total_gap) / count if count > 0 else 0

        # 각 아이템 배치
        for i, item in enumerate(items):
            # X% 계산
            x_percent = self.LEFT_MARGIN + (item_width + self.GAP) * i

            # Y%, 높이% 가져오기
            y_percent = item.get('y_percent', 0)
            height_percent = item.get('height_percent', 100)

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