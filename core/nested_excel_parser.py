"""
AutoArchitect - Excel Parser (완전판)
v5.0 (X%, 너비% 기반) + v6.0 (행번호 기반) 모두 지원
"""

import pandas as pd
from typing import Dict, Any, List
import io


class NestedExcelParser:
    """v5.0과 v6.0 엑셀 구조 모두 지원하는 Parser (완전판)"""

    def __init__(self):
        self.excel_version = None  # 'v5' 또는 'v6'

    def read_excel(self, file) -> Dict[str, pd.DataFrame]:
        """엑셀 파일을 읽어 시트별 DataFrame 반환"""
        sheets = {}

        # 파일 타입 확인
        if hasattr(file, 'read'):
            # UploadedFile 객체
            excel_file = pd.ExcelFile(file)
        else:
            # 파일 경로
            excel_file = pd.ExcelFile(file)

        # 모든 시트 읽기
        for sheet_name in excel_file.sheet_names:
            sheets[sheet_name] = pd.read_excel(excel_file, sheet_name=sheet_name)

        return sheets

    def validate_data(self, sheets: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """데이터 검증"""
        errors = []
        warnings = []
        infos = []  # 정보성 메시지

        # 필수 시트 확인
        required_sheets = ['CONFIG', 'LAYERS', 'BOXES']
        for sheet in required_sheets:
            if sheet not in sheets:
                errors.append(f"필수 시트 '{sheet}'가 없습니다.")

        if errors:
            return {
                'is_valid': False,
                'errors': errors,
                'warnings': warnings,
                'infos': infos
            }

        # 버전 감지
        self._detect_version(sheets)

        # 버전 정보 추가
        if self.excel_version == 'v6':
            infos.append("✅ v6.0 엑셀 형식 (행 기반 자동 레이아웃)")
        else:
            infos.append("✅ v5.0 엑셀 형식 (X%, 너비% 기반)")

        # BOXES 시트 검증
        if 'BOXES' in sheets:
            df = sheets['BOXES']

            # v6.0 필수 컬럼
            if self.excel_version == 'v6':
                required_cols = ['박스ID', '박스명', '부모ID', '행번호', 'Y%', '높이%']
            else:
                # v5.0 필수 컬럼
                required_cols = ['박스ID', '박스명', '부모ID', 'X%', 'Y%', '너비%', '높이%']

            for col in required_cols:
                if col not in df.columns:
                    errors.append(f"BOXES 시트에 '{col}' 컬럼이 없습니다.")

            if len(errors) == 0:
                infos.append(f"📦 박스 개수: {len(df)}개")

        # LAYERS 시트 검증
        if 'LAYERS' in sheets:
            df = sheets['LAYERS']
            required_cols = ['레이어ID', '레이어명', '순서', '배경색', '높이%']
            for col in required_cols:
                if col not in df.columns:
                    errors.append(f"LAYERS 시트에 '{col}' 컬럼이 없습니다.")

            if len(errors) == 0:
                infos.append(f"🗂️ 레이어 개수: {len(df)}개")

        # COMPONENTS 시트 확인 (선택사항)
        if 'COMPONENTS' in sheets:
            df = sheets['COMPONENTS']
            infos.append(f"📋 컴포넌트 개수: {len(df)}개")

        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'infos': infos
        }

    def parse_to_dict(self, sheets: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """엑셀 시트를 딕셔너리로 변환 (v5/v6 자동 감지)"""

        # 버전 자동 감지
        self._detect_version(sheets)

        result = {}

        # CONFIG 파싱
        if 'CONFIG' in sheets:
            result['config'] = self._parse_config(sheets['CONFIG'])

        # LAYERS 파싱
        if 'LAYERS' in sheets:
            result['layers'] = self._parse_layers(sheets['LAYERS'])

        # BOXES 파싱 (버전별 처리)
        if 'BOXES' in sheets:
            result['boxes'] = self._parse_boxes(sheets['BOXES'])

        # COMPONENTS 파싱 (버전별 처리)
        if 'COMPONENTS' in sheets:
            result['components'] = self._parse_components(sheets['COMPONENTS'])
        else:
            result['components'] = []  # COMPONENTS가 없을 수도 있음

        # CONNECTIONS 파싱
        if 'CONNECTIONS' in sheets:
            result['connections'] = self._parse_connections(sheets['CONNECTIONS'])
        else:
            result['connections'] = []  # CONNECTIONS가 없을 수도 있음

        return result

    def _detect_version(self, sheets: Dict[str, pd.DataFrame]):
        """엑셀 버전 자동 감지"""
        if 'BOXES' in sheets:
            df = sheets['BOXES']
            # v6.0은 '행번호' 컬럼이 있고 'X%'가 없음
            if '행번호' in df.columns and 'X%' not in df.columns:
                self.excel_version = 'v6'
                print("📋 v6.0 엑셀 형식 감지 (행 기반)")
            else:
                self.excel_version = 'v5'
                print("📋 v5.0 엑셀 형식 감지 (X%, 너비% 기반)")

    def _parse_config(self, df: pd.DataFrame) -> Dict[str, Any]:
        """CONFIG 시트 파싱"""
        config = {}
        for _, row in df.iterrows():
            key = row['항목']
            value = row['값']
            config[key] = value
        return config

    def _parse_layers(self, df: pd.DataFrame) -> List[Dict]:
        """LAYERS 시트 파싱"""
        layers = []
        for _, row in df.iterrows():
            layer = {
                'id': row['레이어ID'],
                'name': row['레이어명'],
                'order': row['순서'],
                'bg_color': row['배경색'],
                'height_percent': row['높이%']
            }
            layers.append(layer)
        return layers

    def _parse_boxes(self, df: pd.DataFrame) -> List[Dict]:
        """BOXES 시트 파싱 (v5/v6 자동 처리)"""
        boxes = []

        for _, row in df.iterrows():
            box = {
                'id': row['박스ID'],
                'name': row['박스명'],
                'parent_id': row['부모ID'],
                'y_percent': row['Y%'],
                'height_percent': row['높이%'],
                'bg_color': row['배경색'],
                'border_color': row['테두리색'],
                'font_size': row['폰트크기']
            }

            # 버전별 추가 필드
            if self.excel_version == 'v6':
                # v6.0: 행번호 사용
                box['row_number'] = row['행번호']
                # x_percent, width_percent는 나중에 계산
            else:
                # v5.0: X%, 너비% 직접 사용
                box['x_percent'] = row['X%']
                box['width_percent'] = row['너비%']

            boxes.append(box)

        return boxes

    def _parse_components(self, df: pd.DataFrame) -> List[Dict]:
        """COMPONENTS 시트 파싱 (v5/v6 자동 처리)"""
        components = []

        for _, row in df.iterrows():
            comp = {
                'id': row['ID'],
                'name': row['컴포넌트명'],
                'parent_id': row['부모ID'],
                'y_percent': row['Y%'],
                'height_percent': row['높이%'],
                'font_size': row['폰트크기'],
                'type': row['타입']
            }

            # 버전별 추가 필드
            if self.excel_version == 'v6':
                # v6.0: 행번호 사용
                comp['row_number'] = row['행번호']
                # x_percent, width_percent는 나중에 계산
            else:
                # v5.0: X%, 너비% 직접 사용
                comp['x_percent'] = row['X%']
                comp['width_percent'] = row['너비%']

            components.append(comp)

        return components

    def _parse_connections(self, df: pd.DataFrame) -> List[Dict]:
        """CONNECTIONS 시트 파싱"""
        connections = []

        for _, row in df.iterrows():
            conn = {
                'from_id': row['출발ID'],
                'to_id': row['도착ID'],
                'type': row['연결타입'],
                'label': row['라벨'],
                'style': row['선스타일']
            }
            connections.append(conn)

        return connections