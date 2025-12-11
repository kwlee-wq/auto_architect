"""
우체국 스타일 계층형 샘플 데이터 생성 (개선 버전)
PDF 예시를 정확히 분석하여 최적화
"""

import pandas as pd
from pathlib import Path


def create_optimized_nested_sample():
    """최적화된 계층형 샘플 엑셀 파일 생성"""

    # === CONFIG ===
    df_config = pd.DataFrame({
        '항목': ['다이어그램명', '캔버스너비', '캔버스높이', '레이아웃패턴', '여백비율'],
        '값': ['우체국 금융 빅데이터 플랫폼', 1400, 900, '계층형', 2]
    })

    # === LAYERS ===
    # 우체국 예시: Service Layer는 약 15%, Application Layer는 85%
    df_layers = pd.DataFrame({
        '레이어ID': ['L1', 'L2'],
        '레이어명': ['Service Layer (Big Data Portal)', 'Application & Solution Layer'],
        '순서': [1, 2],
        '배경색': ['연회색', '흰색'],
        '높이%': [15, 85]  # 10% → 15%로 조정
    })

    # === BOXES ===
    boxes_data = [
        # Service Layer 박스들 (L1: 15% = 135px)
        # 박스 높이: 70% → 80%로 조정 (더 두드러지게)
        ['B_SVC1', '공통기능\n(공지사항, 게시판)', 'L1', 2, 20, 11, 65, '흰색', '회색', 10],
        ['B_SVC2', 'Monitoring\n(Data Lake/분석플랫폼)', 'L1', 14, 20, 11, 65, '흰색', '회색', 10],
        ['B_SVC3', '시각화 시스템 연동', 'L1', 26, 20, 11, 65, '흰색', '회색', 10],
        ['B_SVC4', 'Meta 정보 조회', 'L1', 38, 20, 11, 65, '흰색', '회색', 10],
        ['B_SVC5', 'SSO연동', 'L1', 50, 20, 11, 65, '흰색', '회색', 10],

        # Application Layer 큰 박스들 (L2: 85% = 765px)
        ['B_INTERFACE', 'Interface', 'L2', 1, 8, 13, 88, '연회색', '회색', 11],
        ['B_DATALAKE', 'Data Lake', 'L2', 15, 8, 30, 88, '연회색', '회색', 11],
        ['B_ANALYTICS', '분석 플랫폼', 'L2', 46, 8, 21, 45, '연회색', '회색', 11],
        ['B_META', 'Meta 관리', 'L2', 46, 55, 21, 41, '연회색', '회색', 11],
        ['B_MODULE', '분석모듈관리', 'L2', 68, 55, 21, 41, '연회색', '회색', 11],
        ['B_MODELER', 'Modeler', 'L2', 68, 8, 21, 45, '연회색', '회색', 11],

        # Interface 내부 박스들 (B_INTERFACE: 182px wide × 673px tall)
        ['B_DATA_COLLECT', '내/외부 데이터 수집', 'B_INTERFACE', 5, 3, 90, 10, '흰색', '회색', 10],
        ['B_DATA_INPUT', 'Data 수집', 'B_INTERFACE', 5, 15, 90, 35, '연회색', '회색', 10],
        ['B_TRANSFER', 'Transfer\n(parsing, cleansing)', 'B_INTERFACE', 5, 52, 90, 12, '흰색', '회색', 10],
        ['B_LOGGING', 'Logging', 'B_INTERFACE', 5, 66, 90, 10, '흰색', '회색', 10],
        ['B_MODULE_REPO', 'Big Data Module', 'B_INTERFACE', 5, 78, 90, 10, '흰색', '회색', 10],
        ['B_REPO', 'Repository', 'B_INTERFACE', 5, 90, 90, 8, '흰색', '회색', 10],

        # Data Lake 내부 (B_DATALAKE: 420px wide × 673px tall)
        ['B_HADOOP', 'Hadoop Cluster(HDP3.x)', 'B_DATALAKE', 3, 3, 94, 94, '흰색', '회색', 11],

        # Hadoop Cluster 내부 (B_HADOOP)
        ['B_HADOOP_TOP', 'Staging | Lake | Mart', 'B_HADOOP', 3, 5, 94, 12, '연회색', '회색', 10],
        ['B_HADOOP_SW', 'Software Layer : HDP', 'B_HADOOP', 3, 20, 94, 8, '연회색', '회색', 10],
        ['B_HADOOP_OP', 'Operation(Ambari)', 'B_HADOOP', 3, 30, 94, 10, '흰색', '회색', 10],
        ['B_HADOOP_MID', 'Sqoop | Hive | Spark', 'B_HADOOP', 3, 42, 94, 20, '연회색', '회색', 10],
        ['B_HADOOP_YARN', 'YARN (Resource Mgt)', 'B_HADOOP', 3, 64, 94, 12, '흰색', '회색', 10],
        ['B_HADOOP_HDFS', 'HDFS(Data Storage)', 'B_HADOOP', 3, 78, 94, 10, '흰색', '회색', 10],

        # 분석 플랫폼 내부 (B_ANALYTICS)
        ['B_ANAL_MODEL', '분석모델관리', 'B_ANALYTICS', 3, 5, 94, 20, '연회색', '회색', 10],
        ['B_MODELER_BOX', 'Modeler', 'B_ANALYTICS', 3, 27, 94, 30, '연회색', '회색', 10],
        ['B_K8S', 'Kubernetes Orchestration Platform', 'B_ANALYTICS', 3, 60, 94, 35, '흰색', '회색', 10],
    ]

    df_boxes = pd.DataFrame(boxes_data, columns=[
        '박스ID', '박스명', '부모ID', 'X%', 'Y%', '너비%', '높이%', '배경색', '테두리색', '폰트크기'
    ])

    # === COMPONENTS ===
    components_data = [
        # Data 수집 내부 (B_DATA_INPUT 내부에 3개 컴포넌트)
        ['C_JDBC', 'JDBC Interface', 'B_DATA_INPUT', 8, 8, 84, 26, 9, '단일박스'],
        ['C_BATCH', 'Batch Interface\n(SAM file / XML)', 'B_DATA_INPUT', 8, 38, 84, 26, 9, '단일박스'],
        ['C_BIGDATA', 'Big Data Interface', 'B_DATA_INPUT', 8, 68, 84, 26, 9, '단일박스'],

        # Hadoop Top 영역 (Staging, Lake, Mart)
        ['C_STAGING', 'Staging', 'B_HADOOP_TOP', 3, 15, 30, 70, 9, '단일박스'],
        ['C_LAKE', 'Lake', 'B_HADOOP_TOP', 35, 15, 30, 70, 9, '단일박스'],
        ['C_MART', 'Mart', 'B_HADOOP_TOP', 67, 15, 30, 70, 9, '단일박스'],

        # Hadoop Mid 영역 (Sqoop, Hive, Spark)
        ['C_SQOOP', 'Sqoop\n(Integration)', 'B_HADOOP_MID', 3, 15, 30, 70, 9, '단일박스'],
        ['C_HIVE', 'Hive\n(Batch ETL)', 'B_HADOOP_MID', 35, 15, 30, 70, 9, '단일박스'],
        ['C_SPARK', 'Spark\n(Streaming)', 'B_HADOOP_MID', 67, 15, 30, 70, 9, '단일박스'],

        # 분석모델관리 (2개)
        ['C_BATCH_M', 'Batch', 'B_ANAL_MODEL', 8, 20, 40, 60, 9, '단일박스'],
        ['C_ML', 'ML Modeler', 'B_ANAL_MODEL', 52, 20, 40, 60, 9, '단일박스'],

        # Modeler Box (4개)
        ['C_DL', 'DL Modeler', 'B_MODELER_BOX', 8, 10, 40, 38, 9, '단일박스'],
        ['C_AUTO_ML', 'Auto ML', 'B_MODELER_BOX', 52, 10, 40, 38, 9, '단일박스'],
        ['C_RP', 'RP Modeler', 'B_MODELER_BOX', 8, 52, 40, 38, 9, '단일박스'],
        ['C_AUTO_DL', 'Auto DL', 'B_MODELER_BOX', 52, 52, 40, 38, 9, '단일박스'],

        # Meta 관리 (3개)
        ['C_META_DB', '데이터베이스\n정보관리', 'B_META', 5, 10, 28, 80, 9, '단일박스'],
        ['C_META_TBL', '테이블/파티션\n정보관리', 'B_META', 36, 10, 28, 80, 9, '단일박스'],
        ['C_META_FLD', '테이블 필드\n정보 관리', 'B_META', 67, 10, 28, 80, 9, '단일박스'],

        # 분석모듈관리 (3개)
        ['C_PY_LIB', 'Python Library\n관리', 'B_MODULE', 5, 10, 28, 80, 9, '단일박스'],
        ['C_R_REPO', 'R/Python\nRepository 관리', 'B_MODULE', 36, 10, 28, 80, 9, '단일박스'],
        ['C_R_LIB', 'R Library 관리', 'B_MODULE', 67, 10, 28, 80, 9, '단일박스'],

        # Modeler (우측 상단, 4개)
        ['C_DL2', 'DL Modeler', 'B_MODELER', 5, 10, 43, 38, 9, '단일박스'],
        ['C_AUTO_ML2', 'Auto ML', 'B_MODELER', 52, 10, 43, 38, 9, '단일박스'],
        ['C_RP2', 'RP Modeler', 'B_MODELER', 5, 52, 43, 38, 9, '단일박스'],
        ['C_AUTO_DL2', 'Auto DL', 'B_MODELER', 52, 52, 43, 38, 9, '단일박스'],
    ]

    df_components = pd.DataFrame(components_data, columns=[
        'ID', '컴포넌트명', '부모ID', 'X%', 'Y%', '너비%', '높이%', '폰트크기', '타입'
    ])

    # === CONNECTIONS ===
    df_connections = pd.DataFrame({
        '출발ID': ['B_SVC1', 'B_INTERFACE', 'B_DATALAKE', 'B_ANALYTICS'],
        '도착ID': ['B_INTERFACE', 'B_DATALAKE', 'B_ANALYTICS', 'B_META'],
        '연결타입': ['데이터흐름', '데이터흐름', '데이터흐름', '데이터흐름'],
        '라벨': ['', '', '', ''],
        '선스타일': ['실선', '실선', '실선', '실선']
    })

    # === 저장 ===
    output_path = Path('../templates/nested_sample_optimized.xlsx')

    with pd.ExcelWriter(str(output_path), engine='openpyxl') as writer:
        df_config.to_excel(writer, sheet_name='CONFIG', index=False)
        df_layers.to_excel(writer, sheet_name='LAYERS', index=False)
        df_boxes.to_excel(writer, sheet_name='BOXES', index=False)
        df_components.to_excel(writer, sheet_name='COMPONENTS', index=False)
        df_connections.to_excel(writer, sheet_name='CONNECTIONS', index=False)

    print(f"✅ 최적화된 샘플 생성 완료: {output_path}")

    # 요약 정보
    print(f"\n📊 구조 요약:")
    print(f"   레이어: {len(df_layers)}개")
    print(f"   박스: {len(df_boxes)}개")
    print(f"   컴포넌트: {len(df_components)}개")
    print(f"   연결: {len(df_connections)}개")

    return output_path


if __name__ == '__main__':
    create_optimized_nested_sample()