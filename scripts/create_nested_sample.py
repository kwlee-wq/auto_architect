"""
우체국 스타일 계층형 샘플 데이터 생성 (pandas 사용)
"""

import pandas as pd
from pathlib import Path


def create_nested_sample():
    """계층형 샘플 엑셀 파일 생성"""

    # === CONFIG ===
    df_config = pd.DataFrame({
        '항목': ['다이어그램명', '캔버스너비', '캔버스높이', '레이아웃패턴', '여백비율'],
        '값': ['우체국 금융 빅데이터 플랫폼', 1200, 900, '계층형', 2]
    })

    # === LAYERS ===
    df_layers = pd.DataFrame({
        '레이어ID': ['L1', 'L2'],
        '레이어명': ['Service Layer (Big Data Portal)', 'Application & Solution Layer'],
        '순서': [1, 2],
        '배경색': ['회색', '흰색'],
        '높이%': [10, 90]
    })

    # === BOXES ===
    boxes_data = [
        # Service Layer 박스들
        ['B_SVC1', '공통기능\n(공지사항, 게시판)', 'L1', 15, 15, 12, 70, '연회색', '진회색', 10],
        ['B_SVC2', 'Monitoring\n(Data Lake/분석플랫폼)', 'L1', 29, 15, 12, 70, '연회색', '진회색', 10],
        ['B_SVC3', '시각화 시스템 연동', 'L1', 43, 15, 12, 70, '연회색', '진회색', 10],
        ['B_SVC4', 'Meta 정보 조회', 'L1', 57, 15, 12, 70, '연회색', '진회색', 10],
        ['B_SVC5', 'SSO연동', 'L1', 71, 15, 12, 70, '연회색', '진회색', 10],
        # Application Layer 큰 박스들
        ['B_INTERFACE', 'Interface', 'L2', 2, 12, 14, 86, '연회색', '진회색', 12],
        ['B_DATALAKE', 'Data Lake', 'L2', 18, 12, 32, 86, '연회색', '진회색', 12],
        ['B_ANALYTICS', '분석 플랫폼', 'L2', 52, 12, 23, 43, '연회색', '진회색', 12],
        ['B_META', 'Meta 관리', 'L2', 18, 55, 32, 43, '연회색', '진회색', 12],
        ['B_MODULE', '분석모듈관리', 'L2', 52, 57, 23, 41, '연회색', '진회색', 12],
        # Interface 내부 박스
        ['B_DATA_COLLECT', '내/외부 데이터 수집', 'B_INTERFACE', 8, 6, 84, 12, '흰색', '회색', 11],
        ['B_DATA_INPUT', 'Data 수집', 'B_INTERFACE', 8, 20, 84, 36, '연회색', '회색', 11],
        # Data Lake 내부 박스
        ['B_HADOOP', 'Hadoop Cluster(HDP3.x)', 'B_DATALAKE', 5, 5, 90, 90, '흰색', '회색', 11],
        ['B_HADOOP_SW', 'Software Layer : HDP', 'B_HADOOP', 5, 23, 90, 8, '연회색', '회색', 10],
        # 분석 플랫폼 내부 박스
        ['B_ANAL_MODEL', '분석모델관리', 'B_ANALYTICS', 5, 8, 90, 20, '연회색', '회색', 11],
        ['B_MODELER', 'Modeler', 'B_ANALYTICS', 5, 32, 90, 30, '연회색', '회색', 11],
        ['B_K8S', 'Kubernetes Orchestration Platform', 'B_ANALYTICS', 5, 66, 90, 28, '흰색', '회색', 11],
    ]

    df_boxes = pd.DataFrame(boxes_data, columns=[
        '박스ID', '박스명', '부모ID', 'X%', 'Y%', '너비%', '높이%', '배경색', '테두리색', '폰트크기'
    ])

    # === COMPONENTS ===
    components_data = [
        # Data 수집 내부
        ['C_JDBC', 'JDBC Interface', 'B_DATA_INPUT', 8, 10, 84, 26, 10, '단일박스'],
        ['C_BATCH', 'Batch Interface\n(SAM file / XML)', 'B_DATA_INPUT', 8, 40, 84, 26, 10, '단일박스'],
        ['C_BIGDATA', 'Big Data Interface', 'B_DATA_INPUT', 8, 70, 84, 26, 10, '단일박스'],
        # Interface 하단
        ['C_TRANSFER', 'Transfer\n(parsing, cleansing)', 'B_INTERFACE', 8, 60, 84, 10, 10, '단일박스'],
        ['C_LOGGING', 'Logging', 'B_INTERFACE', 8, 72, 84, 8, 10, '단일박스'],
        ['C_MODULE', 'Big Data Module', 'B_INTERFACE', 8, 82, 84, 8, 10, '단일박스'],
        ['C_REPO', 'Repository', 'B_INTERFACE', 8, 92, 84, 6, 10, '단일박스'],
        # Hadoop Cluster
        ['C_STAGING', 'Staging', 'B_HADOOP', 5, 8, 28, 12, 10, '단일박스'],
        ['C_LAKE', 'Lake', 'B_HADOOP', 35, 8, 28, 12, 10, '단일박스'],
        ['C_MART', 'Mart', 'B_HADOOP', 65, 8, 28, 12, 10, '단일박스'],
        ['C_AMBARI', 'Operation(Ambari)', 'B_HADOOP', 5, 34, 90, 10, 10, '단일박스'],
        ['C_SQOOP', 'Sqoop\n(Integration)', 'B_HADOOP', 5, 48, 28, 20, 10, '단일박스'],
        ['C_HIVE', 'Hive\n(Batch ETL)', 'B_HADOOP', 35, 48, 28, 20, 10, '단일박스'],
        ['C_SPARK', 'Spark\n(Streaming)', 'B_HADOOP', 65, 48, 28, 20, 10, '단일박스'],
        ['C_YARN', 'YARN\n(Resource Mgt)', 'B_HADOOP', 5, 72, 90, 12, 10, '단일박스'],
        ['C_HDFS', 'HDFS(Data Storage)', 'B_HADOOP', 5, 87, 90, 10, 10, '단일박스'],
        # 분석모델관리
        ['C_BATCH_M', 'Batch', 'B_ANAL_MODEL', 10, 25, 38, 60, 10, '단일박스'],
        ['C_ML', 'ML Modeler', 'B_ANAL_MODEL', 52, 25, 38, 60, 10, '단일박스'],
        # Modeler
        ['C_DL', 'DL Modeler', 'B_MODELER', 10, 15, 38, 38, 10, '단일박스'],
        ['C_AUTO_ML', 'Auto ML', 'B_MODELER', 52, 15, 38, 38, 10, '단일박스'],
        ['C_RP', 'RP Modeler', 'B_MODELER', 10, 57, 38, 38, 10, '단일박스'],
        ['C_AUTO_DL', 'Auto DL', 'B_MODELER', 52, 57, 38, 38, 10, '단일박스'],
        # Meta 관리
        ['C_META_DB', '데이터베이스\n정보관리', 'B_META', 8, 15, 28, 75, 10, '단일박스'],
        ['C_META_TBL', '테이블/파티션\n정보관리', 'B_META', 38, 15, 28, 75, 10, '단일박스'],
        ['C_META_FLD', '테이블 필드\n정보 관리', 'B_META', 68, 15, 28, 75, 10, '단일박스'],
        # 분석모듈관리
        ['C_PY_LIB', 'Python Library 관리', 'B_MODULE', 8, 15, 28, 75, 10, '단일박스'],
        ['C_R_REPO', 'R/Python\nRepository 관리', 'B_MODULE', 38, 15, 28, 75, 10, '단일박스'],
        ['C_R_LIB', 'R Library 관리', 'B_MODULE', 68, 15, 28, 75, 10, '단일박스'],
    ]

    df_components = pd.DataFrame(components_data, columns=[
        'ID', '컴포넌트명', '부모ID', 'X%', 'Y%', '너비%', '높이%', '폰트크기', '타입'
    ])

    # === CONNECTIONS ===
    df_connections = pd.DataFrame({
        '출발ID': ['B_SVC1', 'B_INTERFACE', 'B_DATALAKE'],
        '도착ID': ['B_INTERFACE', 'B_DATALAKE', 'B_ANALYTICS'],
        '연결타입': ['데이터흐름', '데이터흐름', '데이터흐름'],
        '라벨': ['', '', ''],
        '선스타일': ['실선', '실선', '실선']
    })

    # === 저장 ===
    output_path = Path('../templates/nested_sample.xlsx')
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with pd.ExcelWriter(str(output_path), engine='openpyxl') as writer:
        df_config.to_excel(writer, sheet_name='CONFIG', index=False)
        df_layers.to_excel(writer, sheet_name='LAYERS', index=False)
        df_boxes.to_excel(writer, sheet_name='BOXES', index=False)
        df_components.to_excel(writer, sheet_name='COMPONENTS', index=False)
        df_connections.to_excel(writer, sheet_name='CONNECTIONS', index=False)

    print(f"✅ {output_path} 생성 완료!")


if __name__ == '__main__':
    create_nested_sample()