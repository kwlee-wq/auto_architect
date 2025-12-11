"""
AutoArchitect - 계층형 레이아웃 엔진
% 기반으로 절대 좌표 계산
"""

from typing import Dict, List, Any


class NestedLayoutEngine:
    """계층 구조를 지원하는 레이아웃 엔진"""

    def __init__(self):
        self.positions = {}
        self.canvas_width = 1200
        self.canvas_height = 900

    def calculate_positions(self, data: Dict[str, Any]) -> Dict[str, Dict]:
        """
        모든 요소의 절대 좌표 계산
        % 기반 → 픽셀 좌표 변환
        """
        self.positions = {}

        self.canvas_width = data['config'].get('캔버스너비', 1200)
        self.canvas_height = data['config'].get('캔버스높이', 900)

        # 1. 레이어 배치
        self._calculate_layer_positions(data['layers'])

        # 2. 박스 배치 (재귀적으로)
        self._calculate_box_positions(data['boxes'], data['layers'])

        # 3. 컴포넌트 배치
        self._calculate_component_positions(data['components'])

        return self.positions

    def _calculate_layer_positions(self, layers: List[Dict]):
        """레이어 절대 좌표 계산"""
        total_height = sum(layer['height_percent'] for layer in layers)
        current_y = 0

        for layer in sorted(layers, key=lambda l: l['order']):
            height = (layer['height_percent'] / total_height) * self.canvas_height

            self.positions[layer['id']] = {
                'x': 0,
                'y': current_y,
                'width': self.canvas_width,
                'height': height,
                'abs_x': 0,
                'abs_y': current_y,
                'abs_width': self.canvas_width,
                'abs_height': height
            }

            current_y += height

    def _calculate_box_positions(self, boxes: List[Dict], layers: List[Dict]):
        """박스 절대 좌표 계산 (재귀)"""
        # 부모별로 그룹화
        by_parent = {}
        for box in boxes:
            parent_id = box['parent_id']
            if parent_id not in by_parent:
                by_parent[parent_id] = []
            by_parent[parent_id].append(box)

        # 레이어 자식부터 계산
        for layer in layers:
            if layer['id'] in by_parent:
                for box in by_parent[layer['id']]:
                    self._calculate_box_recursive(box, by_parent, layer['id'])

    def _calculate_box_recursive(self, box: Dict, by_parent: Dict, parent_id: str):
        """재귀적으로 박스 위치 계산"""
        # 부모 위치 가져오기
        parent_pos = self.positions.get(parent_id)
        if not parent_pos:
            return

        # % → 픽셀 변환
        x = parent_pos['abs_x'] + (box['x_percent'] / 100) * parent_pos['abs_width']
        y = parent_pos['abs_y'] + (box['y_percent'] / 100) * parent_pos['abs_height']
        width = (box['width_percent'] / 100) * parent_pos['abs_width']
        height = (box['height_percent'] / 100) * parent_pos['abs_height']

        self.positions[box['id']] = {
            'x': x,
            'y': y,
            'width': width,
            'height': height,
            'abs_x': x,
            'abs_y': y,
            'abs_width': width,
            'abs_height': height,
            'parent_id': parent_id
        }

        # 자식 박스 계산
        if box['id'] in by_parent:
            for child_box in by_parent[box['id']]:
                self._calculate_box_recursive(child_box, by_parent, box['id'])

    def _calculate_component_positions(self, components: List[Dict]):
        """컴포넌트 절대 좌표 계산"""
        for comp in components:
            parent_id = comp['parent_id']
            parent_pos = self.positions.get(parent_id)

            if not parent_pos:
                continue

            # % → 픽셀 변환
            x = parent_pos['abs_x'] + (comp['x_percent'] / 100) * parent_pos['abs_width']
            y = parent_pos['abs_y'] + (comp['y_percent'] / 100) * parent_pos['abs_height']
            width = (comp['width_percent'] / 100) * parent_pos['abs_width']
            height = (comp['height_percent'] / 100) * parent_pos['abs_height']

            self.positions[comp['id']] = {
                'x': x,
                'y': y,
                'width': width,
                'height': height,
                'abs_x': x,
                'abs_y': y,
                'abs_width': width,
                'abs_height': height,
                'parent_id': parent_id
            }