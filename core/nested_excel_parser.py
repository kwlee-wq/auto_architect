"""
AutoArchitect - 계층형(Nested) 엑셀 파서
BOXES 시트를 읽어 계층 구조 파싱
"""

import pandas as pd
from typing import Dict, List, Any
import io

from utils.constants import COLOR_MAP, BORDER_COLOR_MAP


class NestedExcelParser:
    """계층형 구조를 지원하는 엑셀 파서"""

    def __init__(self):
        self.errors = []
        self.warnings = []
        self.infos = []

    def read_excel(self, file_path) -> Dict[str, pd.DataFrame]:
        """엑셀 파일 읽기"""
        self.errors = []
        self.warnings = []
        self.infos = []

        try:
            # Streamlit UploadedFile 처리
            if hasattr(file_path, 'read'):
                # UploadedFile을 직접 pandas에 전달
                excel_file = pd.ExcelFile(file_path, engine='openpyxl')
            else:
                # 일반 파일 경로
                excel_file = pd.ExcelFile(file_path, engine='openpyxl')

            sheets = {}

            for sheet_name in excel_file.sheet_names:
                if sheet_name == 'GUIDE':
                    continue
                df = pd.read_excel(excel_file, sheet_name=sheet_name, engine='openpyxl')
                df = df.dropna(how='all')
                sheets[sheet_name] = df

            excel_file.close()

            # 필수 시트 확인
            required = ['CONFIG', 'LAYERS', 'BOXES', 'COMPONENTS']
            for sheet in required:
                if sheet not in sheets:
                    self.errors.append(f"{sheet} 시트가 없습니다.")

            return sheets

        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            self.errors.append(f"엑셀 파일 읽기 실패: {str(e)}\n{error_detail}")
            return {}

    def validate_data(self, sheets: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """데이터 검증"""
        if self.errors or not sheets:
            if not sheets and not self.errors:
                self.errors.append("엑셀 파일에서 시트를 찾을 수 없습니다.")
            return {
                'is_valid': False,
                'errors': self.errors,
                'warnings': self.warnings,
                'infos': self.infos
            }

        # BOXES 검증
        if 'BOXES' in sheets:
            self._validate_boxes(sheets['BOXES'])

        # COMPONENTS 검증
        if 'COMPONENTS' in sheets and 'BOXES' in sheets:
            self._validate_components(sheets['COMPONENTS'], sheets['BOXES'])

        return {
            'is_valid': len(self.errors) == 0,
            'errors': self.errors,
            'warnings': self.warnings,
            'infos': self.infos
        }

    def _validate_boxes(self, df: pd.DataFrame):
        """BOXES 검증"""
        # ID 중복 체크
        box_ids = df['박스ID'].dropna()
        duplicates = box_ids[box_ids.duplicated()].unique()
        for dup in duplicates:
            self.errors.append(f"박스ID 중복: {dup}")

        # 부모 참조 체크
        valid_ids = set(box_ids)
        valid_ids.add('L1')  # 레이어도 부모가 될 수 있음
        valid_ids.add('L2')

        for idx, row in df.iterrows():
            parent_id = row.get('부모ID')
            if pd.notna(parent_id) and parent_id not in valid_ids:
                self.errors.append(f"박스 {row['박스ID']}: 존재하지 않는 부모ID '{parent_id}'")

    def _validate_components(self, comp_df: pd.DataFrame, box_df: pd.DataFrame):
        """COMPONENTS 검증"""
        valid_parents = set(box_df['박스ID'].dropna())

        for idx, row in comp_df.iterrows():
            parent_id = row.get('부모ID')
            if pd.notna(parent_id) and parent_id not in valid_parents:
                self.errors.append(f"컴포넌트 {row['ID']}: 존재하지 않는 부모ID '{parent_id}'")

    def parse_to_dict(self, sheets: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """계층 구조를 Dict로 변환"""
        result = {
            'config': {},
            'layers': [],
            'boxes': [],
            'components': [],
            'connections': []
        }

        # CONFIG
        if 'CONFIG' in sheets:
            config_df = sheets['CONFIG']
            result['config'] = dict(zip(config_df['항목'], config_df['값']))

        # LAYERS
        if 'LAYERS' in sheets:
            layers_df = sheets['LAYERS']
            result['layers'] = [
                {
                    'id': row['레이어ID'],
                    'name': row['레이어명'],
                    'order': row['순서'],
                    'bg_color': row['배경색'],
                    'height_percent': row['높이%']
                }
                for _, row in layers_df.iterrows()
                if pd.notna(row['레이어ID'])
            ]

        # BOXES
        if 'BOXES' in sheets:
            boxes_df = sheets['BOXES']
            result['boxes'] = [
                {
                    'id': row['박스ID'],
                    'name': row['박스명'],
                    'parent_id': row['부모ID'],
                    'x_percent': row['X%'],
                    'y_percent': row['Y%'],
                    'width_percent': row['너비%'],
                    'height_percent': row['높이%'],
                    'bg_color': row.get('배경색', '흰색'),
                    'border_color': row.get('테두리색', '회색'),
                    'font_size': row.get('폰트크기', 11)
                }
                for _, row in boxes_df.iterrows()
                if pd.notna(row['박스ID'])
            ]

        # COMPONENTS
        if 'COMPONENTS' in sheets:
            comp_df = sheets['COMPONENTS']
            result['components'] = [
                {
                    'id': row['ID'],
                    'name': row['컴포넌트명'],
                    'parent_id': row['부모ID'],
                    'x_percent': row['X%'],
                    'y_percent': row['Y%'],
                    'width_percent': row['너비%'],
                    'height_percent': row['높이%'],
                    'font_size': row.get('폰트크기', 10),
                    'type': row.get('타입', '단일박스')
                }
                for _, row in comp_df.iterrows()
                if pd.notna(row['ID'])
            ]

        # CONNECTIONS
        if 'CONNECTIONS' in sheets:
            conn_df = sheets['CONNECTIONS']
            result['connections'] = [
                {
                    'from_id': row['출발ID'],
                    'to_id': row['도착ID'],
                    'type': row['연결타입'],
                    'label': row.get('라벨', ''),
                    'style': row.get('선스타일', '실선')
                }
                for _, row in conn_df.iterrows()
                if pd.notna(row['출발ID']) and pd.notna(row['도착ID'])
            ]

        return result