"""
AutoArchitect - Excel Parser (완전판 v6.0)
v5.0 (X%, 너비% 기반) + v6.0 (행번호 기반) 모두 지원
모든 메서드 포함: read_excel, validate_data, parse_to_dict
"""

import pandas as pd
from typing import Dict, Any, List
import io


class NestedExcelParser:
    """v5.0과 v6.0 엑셀 구조 모두 지원하는 Parser (완전판)"""

    def __init__(self):
        self.excel_version = None  # 'v5' 또는 'v6'
        self.errors = []
        self.warnings = []
        self.infos = []

    def read_excel(self, file) -> Dict[str, pd.DataFrame]:
        """엑셀 파일을 읽어 시트별 DataFrame 반환"""
        sheets = {}

        # 초기화
        self.errors = []
        self.warnings = []
        self.infos = []

        try:
            # 파일 타입 확인
            if hasattr(file, 'read'):
                # UploadedFile 객체 (Streamlit)
                file_content = io.BytesIO(file.read())
                file.seek(0)  # 파일 포인터 리셋
                excel_file = pd.ExcelFile(file_content)
            else:
                # 파일 경로
                excel_file = pd.ExcelFile(file)

            # 모든 시트 읽기
            for sheet_name in excel_file.sheet_names:
                # GUIDE 시트는 제외
                if sheet_name == 'GUIDE':
                    continue

                df = pd.read_excel(excel_file, sheet_name=sheet_name)

                # 빈 행 제거 (모든 컬럼이 NaN인 행)
                df = df.dropna(how='all')

                sheets[sheet_name] = df

            return sheets

        except Exception as e:
            self.errors.append(f"엑셀 파일 읽기 실패: {str(e)}")
            return {}

    def validate_data(self, sheets: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """데이터 검증"""
        # 초기화 (read_excel에서 이미 했지만 안전하게)
        if not hasattr(self, 'errors'):
            self.errors = []
        if not hasattr(self, 'warnings'):
            self.warnings = []
        if not hasattr(self, 'infos'):
            self.infos = []

        # read_excel에서 에러 발생한 경우
        if self.errors:
            return {
                'is_valid': False,
                'errors': self.errors,
                'warnings': self.warnings,
                'infos': self.infos
            }

        # 빈 sheets인 경우
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

        # 버전 감지
        self._detect_version(sheets)

        # 버전 정보 추가
        if self.excel_version == 'v6':
            self.infos.append("✅ v6.0 엑셀 형식 (행 기반 자동 레이아웃)")
        else:
            self.infos.append("✅ v5.0 엑셀 형식 (X%, 너비% 기반)")

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
                    self.errors.append(f"BOXES 시트에 '{col}' 컬럼이 없습니다.")

            if len(self.errors) == 0:
                self.infos.append(f"📦 박스 개수: {len(df)}개")

        # LAYERS 시트 검증
        if 'LAYERS' in sheets:
            df = sheets['LAYERS']
            required_cols = ['레이어ID', '레이어명', '순서', '배경색', '높이%']
            for col in required_cols:
                if col not in df.columns:
                    self.errors.append(f"LAYERS 시트에 '{col}' 컬럼이 없습니다.")

            if len(self.errors) == 0:
                self.infos.append(f"🗂️ 레이어 개수: {len(df)}개")

        # COMPONENTS 시트 확인 (선택사항)
        if 'COMPONENTS' in sheets:
            df = sheets['COMPONENTS']
            self.infos.append(f"📋 컴포넌트 개수: {len(df)}개")

        # CONNECTIONS 시트 확인 (선택사항)
        if 'CONNECTIONS' in sheets:
            df = sheets['CONNECTIONS']
            self.infos.append(f"🔗 연결 개수: {len(df)}개")

        return {
            'is_valid': len(self.errors) == 0,
            'errors': self.errors,
            'warnings': self.warnings,
            'infos': self.infos
        }

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

    def parse_to_dict(self, sheets: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """엑셀 시트를 딕셔너리로 변환 (v5/v6 자동 감지)"""

        # 버전 자동 감지 (아직 안했으면)
        if self.excel_version is None:
            self._detect_version(sheets)

        result = {
            'config': {},
            'layers': [],
            'boxes': [],
            'components': [],
            'connections': [],
            'groups': []
        }

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

        # CONNECTIONS 파싱
        if 'CONNECTIONS' in sheets:
            result['connections'] = self._parse_connections(sheets['CONNECTIONS'])

        # GROUPS 파싱 (있으면)
        if 'GROUPS' in sheets:
            result['groups'] = self._parse_groups(sheets['GROUPS'])

        return result

    def _parse_config(self, df: pd.DataFrame) -> Dict[str, Any]:
        """CONFIG 시트 파싱"""
        config = {}
        for _, row in df.iterrows():
            key = row['항목']
            value = row['값']
            if pd.notna(key):
                config[key] = value
        return config

    def _parse_layers(self, df: pd.DataFrame) -> List[Dict]:
        """LAYERS 시트 파싱"""
        layers = []
        for _, row in df.iterrows():
            if pd.isna(row.get('레이어ID')):
                continue

            layer = {
                'id': row['레이어ID'],
                'name': row['레이어명'],
                'order': row.get('순서', 1),
                'bg_color': row.get('배경색', '흰색'),
                'height_percent': row['높이%']
            }
            layers.append(layer)
        return layers

    def _parse_boxes(self, df: pd.DataFrame) -> List[Dict]:
        """BOXES 시트 파싱 (v5/v6 자동 처리)"""
        boxes = []

        for _, row in df.iterrows():
            if pd.isna(row.get('박스ID')):
                continue

            box = {
                'id': row['박스ID'],
                'name': row['박스명'],
                'parent_id': row['부모ID'],
                'y_percent': row['Y%'],
                'height_percent': row['높이%'],
                'bg_color': row.get('배경색', '흰색'),
                'border_color': row.get('테두리색', '회색'),
                'font_size': row.get('폰트크기', 11)
            }

            # 버전별 추가 필드
            if self.excel_version == 'v6':
                # v6.0: 행번호 사용
                box['row_number'] = row.get('행번호', 1)
                # x_percent, width_percent는 Layout Engine에서 자동 계산
            else:
                # v5.0: X%, 너비% 직접 사용
                box['x_percent'] = row.get('X%', 0)
                box['width_percent'] = row.get('너비%', 100)

            boxes.append(box)

        return boxes

    def _parse_components(self, df: pd.DataFrame) -> List[Dict]:
        """COMPONENTS 시트 파싱 (v5/v6 자동 처리)"""
        components = []

        for _, row in df.iterrows():
            if pd.isna(row.get('ID')):
                continue

            comp = {
                'id': row['ID'],
                'name': row['컴포넌트명'],
                'parent_id': row['부모ID'],
                'y_percent': row['Y%'],
                'height_percent': row['높이%'],
                'font_size': row.get('폰트크기', 10),
                'type': row.get('타입', '단일박스')
            }

            # 버전별 추가 필드
            if self.excel_version == 'v6':
                # v6.0: 행번호 사용
                comp['row_number'] = row.get('행번호', 1)
            else:
                # v5.0: X%, 너비% 직접 사용
                comp['x_percent'] = row.get('X%', 0)
                comp['width_percent'] = row.get('너비%', 100)

            components.append(comp)

        return components

    def _parse_connections(self, df: pd.DataFrame) -> List[Dict]:
        """CONNECTIONS 시트 파싱"""
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

    def _parse_groups(self, df: pd.DataFrame) -> List[Dict]:
        """GROUPS 시트 파싱"""
        groups = []

        for _, row in df.iterrows():
            if pd.isna(row.get('그룹ID')):
                continue

            group = {
                'id': row['그룹ID'],
                'name': row.get('그룹명', ''),
                'component_ids': str(row.get('포함컴포넌트(IDs)', '')).split(','),
                'border_style': row.get('테두리스타일', '검정실선'),
                'bg_opacity': row.get('배경투명도', '5%')
            }
            groups.append(group)

        return groups