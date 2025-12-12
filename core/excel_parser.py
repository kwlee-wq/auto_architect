"""
AutoArchitect - Excel Parser (v2.0 리팩토링)
- ExcelParser: 기본형 (LAYERS/COMPONENTS 기반)
- NestedExcelParser: 계층형 (LAYERS/BOXES/COMPONENTS 기반)
"""

import pandas as pd
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
import io

from utils.constants import (
    EXCEL_SHEETS,
    REQUIRED_COLUMNS,
    VALIDATION_RULES,
    ERROR_MESSAGES,
    WARNING_MESSAGES,
    COLOR_MAP,
    BORDER_COLOR_MAP,
    COMPONENT_STYLES,
    CONNECTION_STYLES,
    LAYOUT_PATTERNS
)


class BaseExcelParser(ABC):
    """엑셀 파서 기본 클래스"""

    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.infos: List[str] = []

    def _reset_messages(self):
        """메시지 초기화"""
        self.errors = []
        self.warnings = []
        self.infos = []

    def read_excel(self, file) -> Dict[str, pd.DataFrame]:
        """엑셀 파일을 읽어 시트별 DataFrame 반환"""
        self._reset_messages()
        sheets = {}

        try:
            # 파일 타입 처리
            if hasattr(file, 'read'):
                file_content = io.BytesIO(file.read())
                file.seek(0)
                excel_file = pd.ExcelFile(file_content)
            else:
                excel_file = pd.ExcelFile(file)

            # 모든 시트 읽기
            for sheet_name in excel_file.sheet_names:
                if sheet_name == EXCEL_SHEETS['GUIDE']:
                    continue

                df = pd.read_excel(excel_file, sheet_name=sheet_name)
                df = df.dropna(how='all')
                sheets[sheet_name] = df

            return sheets

        except Exception as e:
            self.errors.append(ERROR_MESSAGES['file_read_error'].format(error=str(e)))
            return {}

    def _get_validation_result(self) -> Dict[str, Any]:
        """검증 결과 반환"""
        return {
            'is_valid': len(self.errors) == 0,
            'errors': self.errors,
            'warnings': self.warnings,
            'infos': self.infos
        }

    def _parse_config(self, df: pd.DataFrame) -> Dict[str, Any]:
        """CONFIG 시트 파싱"""
        config = {}
        for _, row in df.iterrows():
            key = row.get('항목')
            value = row.get('값')
            if pd.notna(key):
                config[key] = value
        return config

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
                'component_ids': [
                    cid.strip()
                    for cid in str(row.get('포함컴포넌트(IDs)', '')).split(',')
                    if cid.strip()
                ],
                'border_style': row.get('테두리스타일', '검정실선'),
                'bg_opacity': row.get('배경투명도', '5%')
            }
            groups.append(group)
        return groups

    @abstractmethod
    def validate_data(self, sheets: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """데이터 검증 (서브클래스에서 구현)"""
        pass

    @abstractmethod
    def parse_to_dict(self, sheets: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """딕셔너리로 변환 (서브클래스에서 구현)"""
        pass


class ExcelParser(BaseExcelParser):
    """기본형 엑셀 파서 (LAYERS/COMPONENTS 기반)"""

    def validate_data(self, sheets: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """기본형 데이터 검증"""
        if self.errors:
            return self._get_validation_result()

        if not sheets:
            self.errors.append(ERROR_MESSAGES['no_sheets_found'])
            return self._get_validation_result()

        # 필수 시트 확인
        required = ['CONFIG', 'LAYERS', 'COMPONENTS']
        for sheet in required:
            if sheet not in sheets:
                self.errors.append(ERROR_MESSAGES['missing_sheet'].format(sheet_name=sheet))

        if self.errors:
            return self._get_validation_result()

        # 정보 메시지
        self.infos.append("✅ 기본형 엑셀 형식 (LAYERS/COMPONENTS)")

        # LAYERS 검증
        self._validate_layers(sheets.get('LAYERS'))

        # COMPONENTS 검증
        self._validate_components(sheets.get('COMPONENTS'), sheets.get('LAYERS'))

        # SUB_COMPONENTS 검증
        if 'SUB_COMPONENTS' in sheets:
            self._validate_sub_components(sheets['SUB_COMPONENTS'], sheets.get('COMPONENTS'))

        # CONNECTIONS 검증
        if 'CONNECTIONS' in sheets:
            self._validate_connections(sheets['CONNECTIONS'], sheets.get('COMPONENTS'))

        # 개수 정보
        self.infos.append(f"🗂️ 레이어: {len(sheets['LAYERS'])}개")
        self.infos.append(f"📦 컴포넌트: {len(sheets['COMPONENTS'])}개")
        if 'CONNECTIONS' in sheets:
            self.infos.append(f"🔗 연결: {len(sheets['CONNECTIONS'])}개")

        return self._get_validation_result()

    def _validate_layers(self, df: pd.DataFrame):
        """LAYERS 시트 검증"""
        if df is None:
            return

        # 필수 컬럼 확인
        for col in REQUIRED_COLUMNS['LAYERS']:
            if col not in df.columns:
                self.errors.append(
                    ERROR_MESSAGES['missing_column'].format(
                        sheet_name='LAYERS', column_name=col
                    )
                )

        # ID 중복 확인
        layer_ids = df['레이어ID'].dropna()
        duplicates = layer_ids[layer_ids.duplicated()].unique()
        for dup in duplicates:
            self.errors.append(
                ERROR_MESSAGES['duplicate_id'].format(id_type='레이어', id_value=dup)
            )

        # 높이% 합계 확인
        heights = df['높이%'].dropna()
        total = heights.sum()
        tolerance = VALIDATION_RULES['height_percent_tolerance']
        if not (100 - tolerance <= total <= 100 + tolerance):
            self.warnings.append(
                ERROR_MESSAGES['height_sum_error'].format(sum=total, tolerance=tolerance)
            )

        # 색상 유효성
        for idx, row in df.iterrows():
            bg_color = row.get('배경색')
            if pd.notna(bg_color) and bg_color not in COLOR_MAP:
                self.errors.append(
                    ERROR_MESSAGES['invalid_value'].format(
                        column_name=f'배경색 (행 {idx + 2})',
                        value=bg_color,
                        allowed=', '.join(COLOR_MAP.keys())
                    )
                )

    def _validate_components(self, df: pd.DataFrame, layers_df: pd.DataFrame):
        """COMPONENTS 시트 검증"""
        if df is None:
            return

        # 필수 컬럼 확인
        for col in REQUIRED_COLUMNS['COMPONENTS']:
            if col not in df.columns:
                self.errors.append(
                    ERROR_MESSAGES['missing_column'].format(
                        sheet_name='COMPONENTS', column_name=col
                    )
                )

        # ID 중복 확인
        comp_ids = df['ID'].dropna()
        duplicates = comp_ids[comp_ids.duplicated()].unique()
        for dup in duplicates:
            self.errors.append(
                ERROR_MESSAGES['duplicate_id'].format(id_type='컴포넌트', id_value=dup)
            )

        # 레이어ID 참조 확인
        if layers_df is not None:
            valid_layer_ids = set(layers_df['레이어ID'].dropna())
            for idx, row in df.iterrows():
                layer_id = row.get('레이어ID')
                if pd.notna(layer_id) and layer_id not in valid_layer_ids:
                    self.errors.append(
                        ERROR_MESSAGES['invalid_reference'].format(
                            ref_type=f"컴포넌트 {row['ID']}",
                            id_value=layer_id
                        )
                    )

        # 타입 유효성
        valid_types = list(COMPONENT_STYLES.keys())
        for idx, row in df.iterrows():
            comp_type = row.get('타입')
            if pd.notna(comp_type) and comp_type not in valid_types:
                self.errors.append(
                    ERROR_MESSAGES['invalid_value'].format(
                        column_name=f'타입 (행 {idx + 2})',
                        value=comp_type,
                        allowed=', '.join(valid_types)
                    )
                )

        # 개수 경고
        if len(df) > VALIDATION_RULES['max_components']:
            self.warnings.append(
                WARNING_MESSAGES['too_many_components'].format(
                    count=len(df),
                    max=VALIDATION_RULES['max_components']
                )
            )

    def _validate_sub_components(self, df: pd.DataFrame, components_df: pd.DataFrame):
        """SUB_COMPONENTS 시트 검증"""
        if df is None or components_df is None:
            return

        valid_comp_ids = set(components_df['ID'].dropna())

        for idx, row in df.iterrows():
            parent_id = row.get('부모ID')
            if pd.notna(parent_id) and parent_id not in valid_comp_ids:
                self.errors.append(
                    ERROR_MESSAGES['invalid_reference'].format(
                        ref_type='서브컴포넌트',
                        id_value=parent_id
                    )
                )

    def _validate_connections(self, df: pd.DataFrame, components_df: pd.DataFrame):
        """CONNECTIONS 시트 검증"""
        if df is None or components_df is None:
            return

        valid_comp_ids = set(components_df['ID'].dropna())

        for idx, row in df.iterrows():
            from_id = row.get('출발ID')
            to_id = row.get('도착ID')

            if pd.notna(from_id) and from_id not in valid_comp_ids:
                self.errors.append(
                    ERROR_MESSAGES['invalid_reference'].format(
                        ref_type='연결 출발',
                        id_value=from_id
                    )
                )

            if pd.notna(to_id) and to_id not in valid_comp_ids:
                self.errors.append(
                    ERROR_MESSAGES['invalid_reference'].format(
                        ref_type='연결 도착',
                        id_value=to_id
                    )
                )

            # 자기 연결 경고
            if pd.notna(from_id) and pd.notna(to_id) and from_id == to_id:
                self.warnings.append(
                    WARNING_MESSAGES['self_connection'].format(id=from_id)
                )

        # 연결 타입 유효성
        valid_conn_types = list(CONNECTION_STYLES.keys())
        for idx, row in df.iterrows():
            conn_type = row.get('연결타입')
            if pd.notna(conn_type) and conn_type not in valid_conn_types:
                self.errors.append(
                    ERROR_MESSAGES['invalid_value'].format(
                        column_name=f'연결타입 (행 {idx + 2})',
                        value=conn_type,
                        allowed=', '.join(valid_conn_types)
                    )
                )

    def parse_to_dict(self, sheets: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """기본형 데이터를 딕셔너리로 변환"""
        result = {
            'config': {},
            'layers': [],
            'components': [],
            'sub_components': [],
            'connections': [],
            'groups': []
        }

        # CONFIG
        if 'CONFIG' in sheets:
            result['config'] = self._parse_config(sheets['CONFIG'])

        # LAYERS
        if 'LAYERS' in sheets:
            result['layers'] = self._parse_layers_data(sheets['LAYERS'])

        # COMPONENTS
        if 'COMPONENTS' in sheets:
            result['components'] = self._parse_components_data(sheets['COMPONENTS'])

        # SUB_COMPONENTS
        if 'SUB_COMPONENTS' in sheets:
            result['sub_components'] = self._parse_sub_components_data(sheets['SUB_COMPONENTS'])

        # CONNECTIONS
        if 'CONNECTIONS' in sheets:
            result['connections'] = self._parse_connections(sheets['CONNECTIONS'])

        # GROUPS
        if 'GROUPS' in sheets:
            result['groups'] = self._parse_groups(sheets['GROUPS'])

        return result

    def _parse_layers_data(self, df: pd.DataFrame) -> List[Dict]:
        """LAYERS 데이터 파싱"""
        layers = []
        for _, row in df.iterrows():
            if pd.isna(row.get('레이어ID')):
                continue

            layer = {
                'id': row['레이어ID'],
                'name': row['레이어명'],
                'height_percent': row['높이%'],
                'bg_color': row['배경색'],
                'border_color': row.get('테두리색', '검정')
            }
            layers.append(layer)
        return layers

    def _parse_components_data(self, df: pd.DataFrame) -> List[Dict]:
        """COMPONENTS 데이터 파싱"""
        components = []
        for _, row in df.iterrows():
            if pd.isna(row.get('ID')):
                continue

            comp = {
                'id': row['ID'],
                'name': row['컴포넌트명'],
                'layer_id': row['레이어ID'],
                'type': row['타입'],
                'width': row['너비'],
                'icon': row.get('아이콘'),
                'text_size': row.get('텍스트크기', '중간')
            }
            components.append(comp)
        return components

    def _parse_sub_components_data(self, df: pd.DataFrame) -> List[Dict]:
        """SUB_COMPONENTS 데이터 파싱"""
        sub_components = []
        for _, row in df.iterrows():
            if pd.isna(row.get('부모ID')):
                continue

            sub = {
                'parent_id': row['부모ID'],
                'name': row['서브컴포넌트명'],
                'order': row['순서']
            }
            sub_components.append(sub)
        return sub_components


class NestedExcelParser(BaseExcelParser):
    """계층형 엑셀 파서 (LAYERS/BOXES/COMPONENTS 기반)"""

    def __init__(self):
        super().__init__()
        self.excel_version: Optional[str] = None  # 'v5' 또는 'v6'

    def _detect_version(self, sheets: Dict[str, pd.DataFrame]):
        """엑셀 버전 자동 감지 (v5: X%/너비% 기반, v6: 행번호 기반)"""
        if 'BOXES' in sheets:
            df = sheets['BOXES']
            if '행번호' in df.columns and 'X%' not in df.columns:
                self.excel_version = 'v6'
            else:
                self.excel_version = 'v5'

    def validate_data(self, sheets: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """계층형 데이터 검증"""
        if self.errors:
            return self._get_validation_result()

        if not sheets:
            self.errors.append(ERROR_MESSAGES['no_sheets_found'])
            return self._get_validation_result()

        # 필수 시트 확인
        required = ['CONFIG', 'LAYERS', 'BOXES']
        for sheet in required:
            if sheet not in sheets:
                self.errors.append(ERROR_MESSAGES['missing_sheet'].format(sheet_name=sheet))

        if self.errors:
            return self._get_validation_result()

        # 버전 감지
        self._detect_version(sheets)

        # 정보 메시지
        if self.excel_version == 'v6':
            self.infos.append("✅ v6.0 계층형 엑셀 형식 (행번호 기반 자동 레이아웃)")
        else:
            self.infos.append("✅ v5.0 계층형 엑셀 형식 (X%, 너비% 기반)")

        # LAYERS 검증
        self._validate_layers(sheets.get('LAYERS'))

        # BOXES 검증
        self._validate_boxes(sheets.get('BOXES'))

        # COMPONENTS 검증 (선택사항)
        if 'COMPONENTS' in sheets:
            self._validate_nested_components(sheets['COMPONENTS'])

        # CONNECTIONS 검증 (선택사항)
        if 'CONNECTIONS' in sheets:
            self._validate_nested_connections(sheets['CONNECTIONS'], sheets)

        # 개수 정보
        self.infos.append(f"🗂️ 레이어: {len(sheets['LAYERS'])}개")
        self.infos.append(f"📦 박스: {len(sheets['BOXES'])}개")
        if 'COMPONENTS' in sheets:
            self.infos.append(f"📋 컴포넌트: {len(sheets['COMPONENTS'])}개")
        if 'CONNECTIONS' in sheets:
            self.infos.append(f"🔗 연결: {len(sheets['CONNECTIONS'])}개")

        return self._get_validation_result()

    def _validate_layers(self, df: pd.DataFrame):
        """LAYERS 시트 검증"""
        if df is None:
            return

        required_cols = ['레이어ID', '레이어명', '순서', '배경색', '높이%']
        for col in required_cols:
            if col not in df.columns:
                self.errors.append(
                    ERROR_MESSAGES['missing_column'].format(
                        sheet_name='LAYERS', column_name=col
                    )
                )

    def _validate_boxes(self, df: pd.DataFrame):
        """BOXES 시트 검증"""
        if df is None:
            return

        # v6.0 필수 컬럼
        if self.excel_version == 'v6':
            required_cols = ['박스ID', '박스명', '부모ID', '행번호', 'Y%', '높이%']
        else:
            required_cols = ['박스ID', '박스명', '부모ID', 'X%', 'Y%', '너비%', '높이%']

        for col in required_cols:
            if col not in df.columns:
                self.errors.append(
                    ERROR_MESSAGES['missing_column'].format(
                        sheet_name='BOXES', column_name=col
                    )
                )

        # 개수 경고
        if len(df) > VALIDATION_RULES['max_boxes']:
            self.warnings.append(
                WARNING_MESSAGES['too_many_boxes'].format(
                    count=len(df),
                    max=VALIDATION_RULES['max_boxes']
                )
            )

    def _validate_nested_components(self, df: pd.DataFrame):
        """계층형 COMPONENTS 시트 검증"""
        if df is None:
            return

        required_cols = ['ID', '컴포넌트명', '부모ID']
        for col in required_cols:
            if col not in df.columns:
                self.errors.append(
                    ERROR_MESSAGES['missing_column'].format(
                        sheet_name='COMPONENTS', column_name=col
                    )
                )

    def _validate_nested_connections(self, df: pd.DataFrame, sheets: Dict[str, pd.DataFrame]):
        """계층형 CONNECTIONS 시트 검증"""
        if df is None:
            return

        # 모든 유효한 ID 수집 (박스 + 컴포넌트)
        valid_ids = set()
        if 'BOXES' in sheets:
            valid_ids.update(sheets['BOXES']['박스ID'].dropna())
        if 'COMPONENTS' in sheets:
            valid_ids.update(sheets['COMPONENTS']['ID'].dropna())

        for idx, row in df.iterrows():
            from_id = row.get('출발ID')
            to_id = row.get('도착ID')

            if pd.notna(from_id) and from_id not in valid_ids:
                self.warnings.append(f"연결 출발ID '{from_id}'가 존재하지 않습니다.")
            if pd.notna(to_id) and to_id not in valid_ids:
                self.warnings.append(f"연결 도착ID '{to_id}'가 존재하지 않습니다.")

    def parse_to_dict(self, sheets: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """계층형 데이터를 딕셔너리로 변환"""
        # 버전 감지
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

        # CONFIG
        if 'CONFIG' in sheets:
            result['config'] = self._parse_config(sheets['CONFIG'])

        # LAYERS
        if 'LAYERS' in sheets:
            result['layers'] = self._parse_nested_layers(sheets['LAYERS'])

        # BOXES
        if 'BOXES' in sheets:
            result['boxes'] = self._parse_boxes_data(sheets['BOXES'])

        # COMPONENTS
        if 'COMPONENTS' in sheets:
            result['components'] = self._parse_nested_components_data(sheets['COMPONENTS'])

        # CONNECTIONS
        if 'CONNECTIONS' in sheets:
            result['connections'] = self._parse_connections(sheets['CONNECTIONS'])

        # GROUPS
        if 'GROUPS' in sheets:
            result['groups'] = self._parse_groups(sheets['GROUPS'])

        return result

    def _parse_nested_layers(self, df: pd.DataFrame) -> List[Dict]:
        """계층형 LAYERS 데이터 파싱"""
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

    def _parse_boxes_data(self, df: pd.DataFrame) -> List[Dict]:
        """BOXES 데이터 파싱 (v5/v6 자동 처리)"""
        boxes = []
        for _, row in df.iterrows():
            if pd.isna(row.get('박스ID')):
                continue

            box = {
                'id': row['박스ID'],
                'name': row.get('박스명', ''),
                'parent_id': row.get('부모ID'),
                'y_percent': row.get('Y%', 0),
                'height_percent': row.get('높이%', 100),
                'bg_color': row.get('배경색', '흰색'),
                'border_color': row.get('테두리색', '회색'),
                'font_size': row.get('폰트크기', 11)
            }

            # 버전별 추가 필드
            if self.excel_version == 'v6':
                box['row_number'] = row.get('행번호', 1)
            else:
                box['x_percent'] = row.get('X%', 0)
                box['width_percent'] = row.get('너비%', 100)

            boxes.append(box)
        return boxes

    def _parse_nested_components_data(self, df: pd.DataFrame) -> List[Dict]:
        """계층형 COMPONENTS 데이터 파싱"""
        components = []
        for _, row in df.iterrows():
            if pd.isna(row.get('ID')):
                continue

            comp = {
                'id': row['ID'],
                'name': row.get('컴포넌트명', ''),
                'parent_id': row.get('부모ID'),
                'y_percent': row.get('Y%', 0),
                'height_percent': row.get('높이%', 100),
                'font_size': row.get('폰트크기', 10),
                'type': row.get('타입', '단일박스')
            }

            # 버전별 추가 필드
            if self.excel_version == 'v6':
                comp['row_number'] = row.get('행번호', 1)
            else:
                comp['x_percent'] = row.get('X%', 0)
                comp['width_percent'] = row.get('너비%', 100)

            components.append(comp)
        return components


def create_parser(sheets: Dict[str, pd.DataFrame]) -> BaseExcelParser:
    """시트 구조에 따라 적절한 파서 반환"""
    if 'BOXES' in sheets:
        return NestedExcelParser()
    else:
        return ExcelParser()


def detect_excel_type(file) -> str:
    """엑셀 파일 타입 감지 ('nested' 또는 'flat')"""
    try:
        if hasattr(file, 'read'):
            file_content = io.BytesIO(file.read())
            file.seek(0)
            excel_file = pd.ExcelFile(file_content)
        else:
            excel_file = pd.ExcelFile(file)

        if 'BOXES' in excel_file.sheet_names:
            return 'nested'
        return 'flat'
    except:
        return 'flat'
