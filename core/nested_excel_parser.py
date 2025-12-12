"""
AutoArchitect - Excel Parser
행번호 기반 엑셀 파싱
"""

import pandas as pd
from typing import Dict, Any, List
import io


class NestedExcelParser:
    """행번호 기반 엑셀 파서"""

    def __init__(self):
        self.errors = []
        self.warnings = []
        self.infos = []

    def read_excel(self, file) -> Dict[str, pd.DataFrame]:
        """엑셀 파일 읽기"""
        sheets = {}

        self.errors = []
        self.warnings = []
        self.infos = []

        try:
            if hasattr(file, 'read'):
                file_content = io.BytesIO(file.read())
                file.seek(0)
                excel_file = pd.ExcelFile(file_content)
            else:
                excel_file = pd.ExcelFile(file)

            for sheet_name in excel_file.sheet_names:
                if sheet_name == 'GUIDE':
                    continue

                df = pd.read_excel(excel_file, sheet_name=sheet_name)
                df = df.dropna(how='all')
                sheets[sheet_name] = df

            return sheets

        except Exception as e:
            self.errors.append(f"엑셀 파일 읽기 실패: {str(e)}")
            return {}

    def validate_data(self, sheets: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """데이터 검증"""
        if self.errors:
            return {
                'is_valid': False,
                'errors': self.errors,
                'warnings': self.warnings,
                'infos': self.infos
            }

        if not sheets:
            self.errors.append("엑셀 파일에서 시트를 찾을 수 없습니다.")
            return {
                'is_valid': False,
                'errors': self.errors,
                'warnings': self.warnings,
                'infos': self.infos
            }

        # 필수 시트 확인
        required_sheets = ['CONFIG', 'LAYERS', 'BOXES']
        for sheet in required_sheets:
            if sheet not in sheets:
                self.errors.append(f"필수 시트 '{sheet}'가 없습니다.")

        if self.errors:
            return {
                'is_valid': False,
                'errors': self.errors,
                'warnings': self.warnings,
                'infos': self.infos
            }

        # 정보 메시지
        self.infos.append("✅ 계층형 엑셀 형식 (행번호 기반)")

        if 'BOXES' in sheets:
            self.infos.append(f"📦 박스 개수: {len(sheets['BOXES'])}개")

        if 'LAYERS' in sheets:
            self.infos.append(f"🗂️ 레이어 개수: {len(sheets['LAYERS'])}개")

        if 'COMPONENTS' in sheets:
            self.infos.append(f"📋 컴포넌트 개수: {len(sheets['COMPONENTS'])}개")

        if 'CONNECTIONS' in sheets:
            self.infos.append(f"🔗 연결 개수: {len(sheets['CONNECTIONS'])}개")

        return {
            'is_valid': len(self.errors) == 0,
            'errors': self.errors,
            'warnings': self.warnings,
            'infos': self.infos
        }

    def parse_to_dict(self, sheets: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """엑셀을 딕셔너리로 변환"""
        result = {
            'config': {},
            'layers': [],
            'boxes': [],
            'components': [],
            'connections': [],
            'groups': []
        }

        # CONFIG
        if 'CONFIG' in sheets:
            result['config'] = self._parse_config(sheets['CONFIG'])

        # LAYERS
        if 'LAYERS' in sheets:
            result['layers'] = self._parse_layers(sheets['LAYERS'])

        # BOXES
        if 'BOXES' in sheets:
            result['boxes'] = self._parse_boxes(sheets['BOXES'])

        # COMPONENTS
        if 'COMPONENTS' in sheets:
            result['components'] = self._parse_components(sheets['COMPONENTS'])

        # CONNECTIONS
        if 'CONNECTIONS' in sheets:
            result['connections'] = self._parse_connections(sheets['CONNECTIONS'])

        return result

    def _parse_config(self, df: pd.DataFrame) -> Dict[str, Any]:
        config = {}
        for _, row in df.iterrows():
            key = row.get('항목')
            value = row.get('값')
            if pd.notna(key):
                config[key] = value
        return config

    def _parse_layers(self, df: pd.DataFrame) -> List[Dict]:
        layers = []
        for _, row in df.iterrows():
            if pd.isna(row.get('레이어ID')):
                continue

            layer = {
                'id': row['레이어ID'],
                'name': row.get('레이어명', ''),
                'order': row.get('순서', 1),
                'bg_color': row.get('배경색', '흰색'),
                'height_percent': row.get('높이%', 50)
            }
            layers.append(layer)
        return layers

    def _parse_boxes(self, df: pd.DataFrame) -> List[Dict]:
        boxes = []
        for _, row in df.iterrows():
            if pd.isna(row.get('박스ID')):
                continue

            box = {
                'id': row['박스ID'],
                'name': row.get('박스명', ''),
                'parent_id': row.get('부모ID'),
                'row_number': row.get('행번호', 1),
                'y_percent': row.get('Y%', 0),
                'height_percent': row.get('높이%', 100),
                'bg_color': row.get('배경색', '흰색'),
                'border_color': row.get('테두리색', '회색'),
                'font_size': row.get('폰트크기', 11)
            }
            boxes.append(box)
        return boxes

    def _parse_components(self, df: pd.DataFrame) -> List[Dict]:
        components = []
        for _, row in df.iterrows():
            if pd.isna(row.get('ID')):
                continue

            comp = {
                'id': row['ID'],
                'name': row.get('컴포넌트명', ''),
                'parent_id': row.get('부모ID'),
                'row_number': row.get('행번호', 1),
                'y_percent': row.get('Y%', 0),
                'height_percent': row.get('높이%', 100),
                'font_size': row.get('폰트크기', 10),
                'type': row.get('타입', '단일박스')
            }
            components.append(comp)
        return components

    def _parse_connections(self, df: pd.DataFrame) -> List[Dict]:
        connections = []
        for _, row in df.iterrows():
            if pd.isna(row.get('출발ID')) or pd.isna(row.get('도착ID')):
                continue

            conn = {
                'from_id': row['출발ID'],
                'to_id': row['도착ID'],
                'type': row.get('연결타입', '데이터흐름'),
                'label': row.get('라벨', ''),
                'style': row.get('선스타일', '실선')
            }
            connections.append(conn)
        return connections