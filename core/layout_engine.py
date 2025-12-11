"""
AutoArchitect - 레이아웃 엔진
컴포넌트 자동 배치 알고리즘
"""

from typing import Dict, List, Any
from utils.constants import (
    DEFAULT_CANVAS_WIDTH,
    DEFAULT_CANVAS_HEIGHT,
    DEFAULT_COMPONENT_MIN_WIDTH,
    DEFAULT_COMPONENT_MIN_HEIGHT
)


class LayoutEngine:
    """레이아웃 계산 엔진"""

    def __init__(self):
        self.positions = {}

    def calculate_positions(self, data: Dict[str, Any], pattern: str = '수평레이어스택') -> Dict[str, Dict]:
        """
        선택된 패턴으로 모든 컴포넌트 위치 계산

        Args:
            data: parse_to_dict()로 변환된 데이터
            pattern: 레이아웃 패턴

        Returns:
            {
                'layer_id': {'y': 0, 'height': 200},
                'component_id': {'x': 100, 'y': 50, 'width': 150, 'height': 80},
                ...
            }
        """
        self.positions = {}

        canvas_width = data['config'].get('캔버스너비', DEFAULT_CANVAS_WIDTH)
        canvas_height = data['config'].get('캔버스높이', DEFAULT_CANVAS_HEIGHT)
        margin_percent = data['config'].get('여백비율', 15) / 100

        if pattern == '수평레이어스택':
            return self._horizontal_layer_stack(data, canvas_width, canvas_height, margin_percent)
        elif pattern == '좌우분할':
            return self._left_right_split(data, canvas_width, canvas_height, margin_percent)
        elif pattern == '중앙허브형':
            return self._central_hub(data, canvas_width, canvas_height, margin_percent)
        elif pattern == '좌우파이프라인':
            return self._left_right_pipeline(data, canvas_width, canvas_height, margin_percent)
        else:
            # 기본값
            return self._horizontal_layer_stack(data, canvas_width, canvas_height, margin_percent)

    def _horizontal_layer_stack(self, data: Dict, canvas_width: int,
                                canvas_height: int, margin_percent: float) -> Dict:
        """
        수평 레이어 스택 패턴 - 박스 중첩 스타일
        첫 번째 이미지처럼 큰 박스 안에 작은 박스들을 배치
        """
        positions = {}

        # 캔버스를 레이어 개수로 수직 분할
        num_layers = len(data['layers'])
        layer_height = canvas_height / num_layers

        current_y = 0

        for layer_idx, layer in enumerate(data['layers']):
            # 레이어 자체는 배경으로만 사용
            positions[layer['id']] = {
                'y': current_y,
                'height': layer_height,
                'x': 0,
                'width': canvas_width
            }

            # 이 레이어의 컴포넌트들
            layer_components = [c for c in data['components'] if c['layer_id'] == layer['id']]

            if not layer_components:
                current_y += layer_height
                continue

            # 컴포넌트 크기 설정
            margin = 40
            gap = 20
            num_comps = len(layer_components)

            # 가로로 균등 분할
            available_width = canvas_width - (margin * 2)
            comp_width = (available_width - (gap * (num_comps - 1))) / num_comps

            # 컴포넌트 높이는 레이어 높이의 70%
            comp_height = layer_height * 0.7

            # 컴포넌트 배치
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

    def _left_right_split(self, data: Dict, canvas_width: int,
                          canvas_height: int, margin_percent: float) -> Dict:
        """
        좌우 분할 패턴
        좌측: 소스 시스템, 중앙: 처리 레이어, 우측: 타겟 시스템
        """
        # 간단 구현: 레이어를 3등분하여 가로로 배치
        positions = {}

        num_layers = len(data['layers'])
        section_width = canvas_width / num_layers

        for idx, layer in enumerate(data['layers']):
            x_offset = idx * section_width

            positions[layer['id']] = {
                'y': 0,
                'height': canvas_height
            }

            # 이 레이어의 컴포넌트들을 세로로 배치
            layer_components = [c for c in data['components'] if c['layer_id'] == layer['id']]

            if layer_components:
                comp_height = canvas_height / (len(layer_components) + 1)

                for comp_idx, comp in enumerate(layer_components):
                    positions[comp['id']] = {
                        'x': x_offset + section_width * 0.1,
                        'y': (comp_idx + 0.5) * comp_height,
                        'width': section_width * 0.8,
                        'height': comp_height * 0.7
                    }

        return positions

    def _central_hub(self, data: Dict, canvas_width: int,
                     canvas_height: int, margin_percent: float) -> Dict:
        """
        중앙 허브형 패턴
        중앙에 핵심 컴포넌트, 주변에 연결된 시스템들
        """
        positions = {}

        # 연결이 가장 많은 컴포넌트를 중앙에 배치
        if 'connections' in data and data['connections']:
            connection_counts = {}
            for conn in data['connections']:
                connection_counts[conn['from_id']] = connection_counts.get(conn['from_id'], 0) + 1
                connection_counts[conn['to_id']] = connection_counts.get(conn['to_id'], 0) + 1

            hub_id = max(connection_counts, key=connection_counts.get) if connection_counts else None
        else:
            hub_id = None

        # 레이어 정보 (기본 수평 스택으로)
        return self._horizontal_layer_stack(data, canvas_width, canvas_height, margin_percent)

    def _left_right_pipeline(self, data: Dict, canvas_width: int,
                             canvas_height: int, margin_percent: float) -> Dict:
        """
        좌우 파이프라인 패턴
        레이어를 시간/단계 순서대로 좌→우 배치
        """
        # 레이어를 세로로 구분하여 배치
        return self._left_right_split(data, canvas_width, canvas_height, margin_percent)

    def detect_crossings(self, positions: Dict, connections: List[Dict]) -> int:
        """
        연결선 교차 개수 추정 (간단한 휴리스틱)

        Args:
            positions: 컴포넌트 위치 정보
            connections: 연결 정보

        Returns:
            예상 교차 개수
        """
        # 간단한 구현: 모든 연결 쌍을 비교
        crossings = 0

        for i, conn1 in enumerate(connections):
            pos1_from = positions.get(conn1['from_id'])
            pos1_to = positions.get(conn1['to_id'])

            if not pos1_from or not pos1_to:
                continue

            for conn2 in connections[i+1:]:
                pos2_from = positions.get(conn2['from_id'])
                pos2_to = positions.get(conn2['to_id'])

                if not pos2_from or not pos2_to:
                    continue

                # 간단한 교차 검사 (선분이 교차하는지)
                if self._lines_intersect(
                        (pos1_from['x'], pos1_from['y']),
                        (pos1_to['x'], pos1_to['y']),
                        (pos2_from['x'], pos2_from['y']),
                        (pos2_to['x'], pos2_to['y'])
                ):
                    crossings += 1

        return crossings

    def _lines_intersect(self, p1, p2, p3, p4) -> bool:
        """
        두 선분이 교차하는지 확인 (간단한 버전)
        """
        def ccw(A, B, C):
            return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])

        return ccw(p1, p3, p4) != ccw(p2, p3, p4) and ccw(p1, p2, p3) != ccw(p1, p2, p4)