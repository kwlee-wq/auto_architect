"""
AutoArchitect - 엑셀 파일 파서
엑셀 파일을 읽고 검증하여 표준 Dict 구조로 변환
"""

import pandas as pd
from typing import Dict, List, Any, Tuple
from pathlib import Path
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


class ExcelParser:
    """엑셀 파일 파서 및 검증"""

    def __init__(self):
        self.errors = []
        self.warnings = []
        self.infos = []

    def read_excel(self, file_path) -> Dict[str, pd.DataFrame]:
        """
        엑셀 파일의 모든 시트를 읽어 DataFrame Dict로 반환

        Args:
            file_path: 파일 경로 또는 UploadedFile 객체 (Streamlit)

        Returns:
            {sheet_name: DataFrame} 형태의 Dict
        """
        self.errors = []
        self.warnings = []
        self.infos = []

        try:
            # Streamlit UploadedFile 처리
            if hasattr(file_path, 'read'):
                file_path = io.BytesIO(file_path.read())

            # 모든 시트 읽기
            excel_file = pd.ExcelFile(file_path)
            sheets = {}

            for sheet_name in excel_file.sheet_names:
                # GUIDE 시트는 제외
                if sheet_name == EXCEL_SHEETS['GUIDE']:
                    continue

                df = pd.read_excel(excel_file, sheet_name=sheet_name)

                # 빈 행 제거 (모든 컬럼이 NaN인 행)
                df = df.dropna(how='all')

                sheets[sheet_name] = df

            # 필수 시트 존재 확인
            required_sheets = [
                EXCEL_SHEETS['CONFIG'],
                EXCEL_SHEETS['LAYERS'],
                EXCEL_SHEETS['COMPONENTS']
            ]

            for sheet_name in required_sheets:
                if sheet_name not in sheets:
                    self.errors.append(
                        ERROR_MESSAGES['missing_sheet'].format(sheet_name=sheet_name)
                    )

            return sheets

        except Exception as e:
            self.errors.append(f"엑셀 파일 읽기 실패: {str(e)}")
            return {}

    def validate_data(self, sheets: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """
        데이터 검증

        Returns:
            {
                'is_valid': bool,
                'errors': List[str],
                'warnings': List[str],
                'infos': List[str]
            }
        """
        if self.errors:  # read_excel에서 에러 발생한 경우
            return {
                'is_valid': False,
                'errors': self.errors,
                'warnings': self.warnings,
                'infos': self.infos
            }

        # 1. 필수 컬럼 검증
        self._validate_required_columns(sheets)

        # 2. CONFIG 검증
        if EXCEL_SHEETS['CONFIG'] in sheets:
            self._validate_config(sheets[EXCEL_SHEETS['CONFIG']])

        # 3. LAYERS 검증
        if EXCEL_SHEETS['LAYERS'] in sheets:
            self._validate_layers(sheets[EXCEL_SHEETS['LAYERS']])

        # 4. COMPONENTS 검증
        if EXCEL_SHEETS['COMPONENTS'] in sheets:
            self._validate_components(
                sheets[EXCEL_SHEETS['COMPONENTS']],
                sheets.get(EXCEL_SHEETS['LAYERS'])
            )

        # 5. SUB_COMPONENTS 검증
        if EXCEL_SHEETS['SUB_COMPONENTS'] in sheets:
            self._validate_sub_components(
                sheets[EXCEL_SHEETS['SUB_COMPONENTS']],
                sheets.get(EXCEL_SHEETS['COMPONENTS'])
            )

        # 6. CONNECTIONS 검증
        if EXCEL_SHEETS['CONNECTIONS'] in sheets:
            self._validate_connections(
                sheets[EXCEL_SHEETS['CONNECTIONS']],
                sheets.get(EXCEL_SHEETS['COMPONENTS'])
            )

        # 7. GROUPS 검증
        if EXCEL_SHEETS['GROUPS'] in sheets:
            self._validate_groups(
                sheets[EXCEL_SHEETS['GROUPS']],
                sheets.get(EXCEL_SHEETS['COMPONENTS'])
            )

        return {
            'is_valid': len(self.errors) == 0,
            'errors': self.errors,
            'warnings': self.warnings,
            'infos': self.infos
        }

    def _validate_required_columns(self, sheets: Dict[str, pd.DataFrame]):
        """필수 컬럼 존재 확인"""
        for sheet_name, required_cols in REQUIRED_COLUMNS.items():
            if sheet_name not in sheets:
                continue

            df = sheets[sheet_name]
            missing_cols = set(required_cols) - set(df.columns)

            if missing_cols:
                for col in missing_cols:
                    self.errors.append(
                        ERROR_MESSAGES['missing_column'].format(
                            sheet_name=sheet_name,
                            column_name=col
                        )
                    )

    def _validate_config(self, df: pd.DataFrame):
        """CONFIG 시트 검증"""
        config_dict = dict(zip(df['항목'], df['값']))

        # 필수 항목 체크
        required_items = ['다이어그램명', '캔버스너비', '캔버스높이', '레이아웃패턴']
        for item in required_items:
            if item not in config_dict or pd.isna(config_dict[item]):
                self.errors.append(
                    ERROR_MESSAGES['empty_required'].format(
                        sheet_name='CONFIG',
                        column_name=item
                    )
                )

        # 레이아웃패턴 유효성 체크
        if '레이아웃패턴' in config_dict:
            pattern = config_dict['레이아웃패턴']
            if pattern not in LAYOUT_PATTERNS:
                self.errors.append(
                    ERROR_MESSAGES['invalid_value'].format(
                        column_name='레이아웃패턴',
                        value=pattern,
                        allowed=', '.join(LAYOUT_PATTERNS)
                    )
                )

    def _validate_layers(self, df: pd.DataFrame):
        """LAYERS 시트 검증"""
        # ID 중복 체크
        layer_ids = df['레이어ID'].dropna()
        duplicates = layer_ids[layer_ids.duplicated()].unique()

        for dup_id in duplicates:
            self.errors.append(
                ERROR_MESSAGES['duplicate_id'].format(
                    id_type='레이어',
                    id_value=dup_id
                )
            )

        # 높이% 합계 체크
        heights = df['높이%'].dropna()
        total_height = heights.sum()
        tolerance = VALIDATION_RULES['height_percent_tolerance']

        if not (100 - tolerance <= total_height <= 100 + tolerance):
            self.warnings.append(
                ERROR_MESSAGES['height_sum_error'].format(
                    sum=total_height,
                    tolerance=tolerance
                )
            )

        # 레이어 개수 체크
        if len(df) > VALIDATION_RULES['max_layers']:
            self.warnings.append(
                f"레이어가 {len(df)}개입니다. {VALIDATION_RULES['max_layers']}개 이하 권장"
            )

        # 색상 유효성 체크
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

            border_color = row.get('테두리색')
            if pd.notna(border_color) and border_color not in BORDER_COLOR_MAP:
                self.errors.append(
                    ERROR_MESSAGES['invalid_value'].format(
                        column_name=f'테두리색 (행 {idx + 2})',
                        value=border_color,
                        allowed=', '.join(BORDER_COLOR_MAP.keys())
                    )
                )

    def _validate_components(self, df: pd.DataFrame, layers_df: pd.DataFrame = None):
        """COMPONENTS 시트 검증"""
        # ID 중복 체크
        comp_ids = df['ID'].dropna()
        duplicates = comp_ids[comp_ids.duplicated()].unique()

        for dup_id in duplicates:
            self.errors.append(
                ERROR_MESSAGES['duplicate_id'].format(
                    id_type='컴포넌트',
                    id_value=dup_id
                )
            )

        # 레이어ID 참조 무결성 체크
        if layers_df is not None:
            valid_layer_ids = set(layers_df['레이어ID'].dropna())

            for idx, row in df.iterrows():
                layer_id = row.get('레이어ID')
                if pd.notna(layer_id) and layer_id not in valid_layer_ids:
                    self.errors.append(
                        ERROR_MESSAGES['invalid_reference'].format(
                            ref_type=f'컴포넌트 {row["ID"]}',
                            id_value=layer_id
                        )
                    )

        # 타입 유효성 체크
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

        # 너비 범위 체크
        width_range = VALIDATION_RULES['width_range']
        for idx, row in df.iterrows():
            width = row.get('너비')
            if pd.notna(width):
                if not (width_range[0] <= width <= width_range[1]):
                    self.errors.append(
                        f"컴포넌트 {row['ID']}의 너비({width})는 "
                        f"{width_range[0]}-{width_range[1]} 범위여야 합니다"
                    )

        # 컴포넌트 개수 경고
        if len(df) > VALIDATION_RULES['max_components']:
            self.warnings.append(
                WARNING_MESSAGES['too_many_components'].format(
                    count=len(df),
                    max=VALIDATION_RULES['max_components']
                )
            )

    def _validate_sub_components(self, df: pd.DataFrame, components_df: pd.DataFrame = None):
        """SUB_COMPONENTS 시트 검증"""
        if components_df is None:
            return

        valid_comp_ids = set(components_df['ID'].dropna())

        # 부모ID 참조 무결성 체크
        for idx, row in df.iterrows():
            parent_id = row.get('부모ID')
            if pd.notna(parent_id) and parent_id not in valid_comp_ids:
                self.errors.append(
                    ERROR_MESSAGES['invalid_reference'].format(
                        ref_type='서브컴포넌트',
                        id_value=parent_id
                    )
                )

            # 부모가 클러스터 타입인지 확인
            if pd.notna(parent_id) and parent_id in valid_comp_ids:
                parent_row = components_df[components_df['ID'] == parent_id].iloc[0]
                if parent_row['타입'] != '클러스터':
                    self.warnings.append(
                        f"컴포넌트 {parent_id}는 클러스터 타입이 아닙니다. "
                        f"서브컴포넌트를 추가하려면 타입을 '클러스터'로 변경하세요."
                    )

        # 서브컴포넌트 개수 체크
        sub_counts = df['부모ID'].value_counts()
        max_subs = VALIDATION_RULES['max_sub_components_per_parent']

        for parent_id, count in sub_counts.items():
            if count > max_subs:
                self.warnings.append(
                    f"컴포넌트 {parent_id}의 서브컴포넌트가 {count}개입니다. "
                    f"{max_subs}개 이하 권장"
                )

    def _validate_connections(self, df: pd.DataFrame, components_df: pd.DataFrame = None):
        """CONNECTIONS 시트 검증"""
        if components_df is None:
            return

        valid_comp_ids = set(components_df['ID'].dropna())

        # 참조 무결성 체크
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

            # 자기 자신으로의 연결 경고
            if pd.notna(from_id) and pd.notna(to_id) and from_id == to_id:
                self.warnings.append(
                    WARNING_MESSAGES['self_connection'].format(id=from_id)
                )

        # 연결 타입 유효성 체크
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

        # 연결 개수 경고
        if len(df) > VALIDATION_RULES['max_connections']:
            self.warnings.append(
                WARNING_MESSAGES['too_many_connections'].format(count=len(df))
            )

    def _validate_groups(self, df: pd.DataFrame, components_df: pd.DataFrame = None):
        """GROUPS 시트 검증"""
        if components_df is None:
            return

        valid_comp_ids = set(components_df['ID'].dropna())

        # 그룹ID 중복 체크
        group_ids = df['그룹ID'].dropna()
        duplicates = group_ids[group_ids.duplicated()].unique()

        for dup_id in duplicates:
            self.errors.append(
                ERROR_MESSAGES['duplicate_id'].format(
                    id_type='그룹',
                    id_value=dup_id
                )
            )

        # 포함컴포넌트 참조 무결성 체크
        for idx, row in df.iterrows():
            comp_ids_str = row.get('포함컴포넌트(IDs)')
            if pd.notna(comp_ids_str):
                comp_ids = [cid.strip() for cid in str(comp_ids_str).split(',')]

                for comp_id in comp_ids:
                    if comp_id and comp_id not in valid_comp_ids:
                        self.errors.append(
                            ERROR_MESSAGES['invalid_reference'].format(
                                ref_type=f'그룹 {row["그룹ID"]}',
                                id_value=comp_id
                            )
                        )

    def parse_to_dict(self, sheets: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """
        검증된 데이터를 표준 Dict 구조로 변환

        Returns:
            {
                'config': {...},
                'layers': [{...}, ...],
                'components': [{...}, ...],
                'sub_components': [{...}, ...],
                'connections': [{...}, ...],
                'groups': [{...}, ...]
            }
        """
        result = {
            'config': {},
            'layers': [],
            'components': [],
            'sub_components': [],
            'connections': [],
            'groups': []
        }

        # CONFIG 파싱
        if EXCEL_SHEETS['CONFIG'] in sheets:
            config_df = sheets[EXCEL_SHEETS['CONFIG']]
            result['config'] = dict(zip(config_df['항목'], config_df['값']))

        # LAYERS 파싱
        if EXCEL_SHEETS['LAYERS'] in sheets:
            layers_df = sheets[EXCEL_SHEETS['LAYERS']]
            result['layers'] = [
                {
                    'id': row['레이어ID'],
                    'name': row['레이어명'],
                    'height_percent': row['높이%'],
                    'bg_color': row['배경색'],
                    'border_color': row.get('테두리색', '검정')
                }
                for _, row in layers_df.iterrows()
                if pd.notna(row['레이어ID'])
            ]

        # COMPONENTS 파싱
        if EXCEL_SHEETS['COMPONENTS'] in sheets:
            comp_df = sheets[EXCEL_SHEETS['COMPONENTS']]
            result['components'] = [
                {
                    'id': row['ID'],
                    'name': row['컴포넌트명'],
                    'layer_id': row['레이어ID'],
                    'type': row['타입'],
                    'width': row['너비'],
                    'icon': row.get('아이콘'),
                    'text_size': row.get('텍스트크기', '중간')
                }
                for _, row in comp_df.iterrows()
                if pd.notna(row['ID'])
            ]

        # SUB_COMPONENTS 파싱
        if EXCEL_SHEETS['SUB_COMPONENTS'] in sheets:
            sub_df = sheets[EXCEL_SHEETS['SUB_COMPONENTS']]
            result['sub_components'] = [
                {
                    'parent_id': row['부모ID'],
                    'name': row['서브컴포넌트명'],
                    'order': row['순서']
                }
                for _, row in sub_df.iterrows()
                if pd.notna(row['부모ID'])
            ]

        # CONNECTIONS 파싱
        if EXCEL_SHEETS['CONNECTIONS'] in sheets:
            conn_df = sheets[EXCEL_SHEETS['CONNECTIONS']]
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

        # GROUPS 파싱
        if EXCEL_SHEETS['GROUPS'] in sheets:
            group_df = sheets[EXCEL_SHEETS['GROUPS']]
            result['groups'] = [
                {
                    'id': row['그룹ID'],
                    'name': row['그룹명'],
                    'component_ids': [
                        cid.strip()
                        for cid in str(row['포함컴포넌트(IDs)']).split(',')
                    ],
                    'border_style': row.get('테두리스타일', '검정실선'),
                    'bg_opacity': row.get('배경투명도', '5%')
                }
                for _, row in group_df.iterrows()
                if pd.notna(row['그룹ID'])
            ]

        return result