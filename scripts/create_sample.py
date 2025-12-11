"""
우체국 빅데이터 플랫폼 샘플 데이터 생성
실행: python scripts/create_sample.py
"""

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation
from pathlib import Path


def create_sample_data():
    """우체국 예시 기반 샘플 데이터 생성"""

    wb = openpyxl.Workbook()
    wb.remove(wb.active)

    # 각 시트 생성
    create_config(wb)
    create_layers(wb)
    create_components(wb)
    create_sub_components(wb)
    create_connections(wb)
    create_groups(wb)

    # 파일 저장
    output_path = Path("../templates/sample_data.xlsx")
    output_path.parent.mkdir(exist_ok=True)
    wb.save(output_path)

    print(f"✅ 샘플 데이터 생성 완료: {output_path}")


def apply_header_style(cell):
    """헤더 스타일"""
    cell.font = Font(bold=True, color="FFFFFF", size=11)
    cell.fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    cell.alignment = Alignment(horizontal="center", vertical="center")


def apply_data_style(cell):
    """데이터 스타일"""
    cell.alignment = Alignment(horizontal="left", vertical="center")


def create_config(wb):
    """CONFIG 시트"""
    ws = wb.create_sheet("CONFIG")

    headers = ["항목", "값"]
    for col, header in enumerate(headers, 1):
        apply_header_style(ws.cell(1, col, header))

    data = [
        ["다이어그램명", "우체국 금융 빅데이터 플랫폼"],
        ["캔버스너비", 1400],
        ["캔버스높이", 900],
        ["레이아웃패턴", "수평레이어스택"],
        ["여백비율", 12]
    ]

    for row_idx, row_data in enumerate(data, 2):
        for col_idx, value in enumerate(row_data, 1):
            apply_data_style(ws.cell(row_idx, col_idx, value))

    ws.column_dimensions['A'].width = 20
    ws.column_dimensions['B'].width = 35


def create_layers(wb):
    """LAYERS 시트"""
    ws = wb.create_sheet("LAYERS")

    headers = ["레이어ID", "레이어명", "높이%", "배경색", "테두리색"]
    for col, header in enumerate(headers, 1):
        apply_header_style(ws.cell(1, col, header))

    data = [
        ["L1", "Application & Portal", 18, "하늘색", "진한파랑"],
        ["L2", "Service Layer", 22, "연두색", "진한녹색"],
        ["L3", "Data Lake & Analytics", 35, "주황색", "진한주황"],
        ["L4", "Infrastructure & Platform", 25, "회색", "진한회색"]
    ]

    for row_idx, row_data in enumerate(data, 2):
        for col_idx, value in enumerate(row_data, 1):
            apply_data_style(ws.cell(row_idx, col_idx, value))

    ws.column_dimensions['A'].width = 12
    ws.column_dimensions['B'].width = 30
    ws.column_dimensions['C'].width = 10
    ws.column_dimensions['D'].width = 12
    ws.column_dimensions['E'].width = 12


def create_components(wb):
    """COMPONENTS 시트"""
    ws = wb.create_sheet("COMPONENTS")

    headers = ["ID", "컴포넌트명", "레이어ID", "타입", "너비", "아이콘", "텍스트크기"]
    for col, header in enumerate(headers, 1):
        apply_header_style(ws.cell(1, col, header))

    data = [
        # Application Layer
        ["C1", "빅데이터 포털", "L1", "서비스", 3, "portal", "중간"],
        ["C2", "모니터링 대시보드", "L1", "서비스", 2, "monitor", "중간"],

        # Service Layer
        ["C3", "분석 플랫폼 (TeraONE+)", "L2", "서비스", 3, "api", "중간"],
        ["C4", "ML/DL Modeler", "L2", "서비스", 2, "api", "중간"],
        ["C5", "Batch 분석모듈", "L2", "서비스", 2, "server", "중간"],

        # Data Lake
        ["C6", "Hadoop Cluster", "L3", "클러스터", 4, "hadoop", "중간"],
        ["C7", "Staging Lake", "L3", "저장소", 2, "storage", "중간"],
        ["C8", "Data Mart", "L3", "데이터베이스", 2, "database", "중간"],
        ["C9", "Meta Repository", "L3", "데이터베이스", 2, "database", "작음"],

        # Infrastructure
        ["C10", "Kubernetes Platform", "L4", "클러스터", 3, "kubernetes", "중간"],
        ["C11", "Kafka Cluster", "L4", "서비스", 2, "kafka", "중간"],
        ["C12", "Spark Cluster", "L4", "서비스", 2, "spark", "중간"],
    ]

    for row_idx, row_data in enumerate(data, 2):
        for col_idx, value in enumerate(row_data, 1):
            apply_data_style(ws.cell(row_idx, col_idx, value))

    ws.column_dimensions['A'].width = 8
    ws.column_dimensions['B'].width = 28
    ws.column_dimensions['C'].width = 12
    ws.column_dimensions['D'].width = 15
    ws.column_dimensions['E'].width = 8
    ws.column_dimensions['F'].width = 12
    ws.column_dimensions['G'].width = 12


def create_sub_components(wb):
    """SUB_COMPONENTS 시트"""
    ws = wb.create_sheet("SUB_COMPONENTS")

    headers = ["부모ID", "서브컴포넌트명", "순서"]
    for col, header in enumerate(headers, 1):
        apply_header_style(ws.cell(1, col, header))

    data = [
        # Hadoop Cluster 내부
        ["C6", "HDFS", 1],
        ["C6", "YARN", 2],
        ["C6", "Hive", 3],
        ["C6", "Spark", 4],
        ["C6", "Sqoop", 5],

        # Kubernetes Platform 내부
        ["C10", "JupyterHub", 1],
        ["C10", "Python Runtime", 2],
        ["C10", "R Runtime", 3],
        ["C10", "GitLab", 4]
    ]

    for row_idx, row_data in enumerate(data, 2):
        for col_idx, value in enumerate(row_data, 1):
            apply_data_style(ws.cell(row_idx, col_idx, value))

    ws.column_dimensions['A'].width = 12
    ws.column_dimensions['B'].width = 30
    ws.column_dimensions['C'].width = 10


def create_connections(wb):
    """CONNECTIONS 시트"""
    ws = wb.create_sheet("CONNECTIONS")

    headers = ["출발ID", "도착ID", "연결타입", "라벨", "선스타일"]
    for col, header in enumerate(headers, 1):
        apply_header_style(ws.cell(1, col, header))

    data = [
        # Portal → Service
        ["C1", "C3", "데이터흐름", "사용자 요청", "실선"],
        ["C1", "C2", "데이터흐름", "모니터링", "실선"],

        # Service → Data Lake
        ["C3", "C6", "데이터흐름", "데이터 조회", "실선"],
        ["C4", "C6", "데이터흐름", "모델 학습", "실선"],
        ["C5", "C7", "배치", "배치 처리", "점선"],

        # Data Lake 내부
        ["C7", "C6", "데이터흐름", "ETL", "실선"],
        ["C6", "C8", "데이터흐름", "Mart 생성", "실선"],
        ["C9", "C6", "데이터흐름", "메타 관리", "점선"],

        # Infrastructure → Data Lake
        ["C11", "C12", "스트림", "실시간 처리", "굵은실선"],
        ["C12", "C6", "데이터흐름", "데이터 저장", "실선"],

        # Kubernetes → Service
        ["C10", "C4", "데이터흐름", "분석 환경", "실선"]
    ]

    for row_idx, row_data in enumerate(data, 2):
        for col_idx, value in enumerate(row_data, 1):
            apply_data_style(ws.cell(row_idx, col_idx, value))

    ws.column_dimensions['A'].width = 10
    ws.column_dimensions['B'].width = 10
    ws.column_dimensions['C'].width = 15
    ws.column_dimensions['D'].width = 20
    ws.column_dimensions['E'].width = 15


def create_groups(wb):
    """GROUPS 시트"""
    ws = wb.create_sheet("GROUPS")

    headers = ["그룹ID", "그룹명", "포함컴포넌트(IDs)", "테두리스타일", "배경투명도"]
    for col, header in enumerate(headers, 1):
        apply_header_style(ws.cell(1, col, header))

    data = [
        ["G1", "분석 환경", "C3,C4,C5,C10", "파란실선", "5%"],
        ["G2", "데이터 저장소", "C6,C7,C8", "녹색점선", "10%"]
    ]

    for row_idx, row_data in enumerate(data, 2):
        for col_idx, value in enumerate(row_data, 1):
            apply_data_style(ws.cell(row_idx, col_idx, value))

    ws.column_dimensions['A'].width = 12
    ws.column_dimensions['B'].width = 20
    ws.column_dimensions['C'].width = 35
    ws.column_dimensions['D'].width = 15
    ws.column_dimensions['E'].width = 15


if __name__ == "__main__":
    print("🔧 샘플 데이터 생성 시작...")
    create_sample_data()
    print("✅ 완료!")