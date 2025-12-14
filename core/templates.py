"""
AutoArchitect - 템플릿 관리
엑셀 파일 기반 템플릿 카탈로그
"""

from pathlib import Path
from typing import Dict, Any, List


# ==================== 템플릿 카탈로그 ====================

TEMPLATE_CATALOG = {
    'postoffice_bigdata': {
        'name': '우체국 빅데이터 플랫폼',
        'description': 'Hadoop, Kafka, Spark 기반 금융권 빅데이터 플랫폼 (4계층 구조)',
        'icon': '🏛️',
        'file': 'postoffice_bigdata.xlsx',
        'tags': ['빅데이터', 'Hadoop', '금융', 'Kafka'],
        'complexity': '상',
    },
    'cloud_bigdata': {
        'name': '클라우드 빅데이터 플랫폼',
        'description': '클라우드 기반 빅데이터 플랫폼 (K8s, Auto Scaling)',
        'icon': '☁️',
        'file': 'cloud_bigdata.xlsx',
        'tags': ['클라우드', 'Kubernetes', 'Auto Scaling'],
        'complexity': '상',
    },
    'gcp_data_platform': {
        'name': 'GCP 데이터 플랫폼',
        'description': 'BigQuery, Airflow, GCS 기반 엔터프라이즈 데이터 플랫폼',
        'icon': '🌐',
        'file': 'gcp_data_platform.xlsx',
        'tags': ['GCP', 'BigQuery', 'Airflow', '데이터 포털'],
        'complexity': '최상',
    },
    'aws_3tier': {
        'name': 'AWS 3-Tier 아키텍처',
        'description': 'CloudFront, ALB, ECS, RDS 기반 클라우드 웹서비스',
        'icon': '🔶',
        'file': 'aws_3tier.xlsx',
        'tags': ['AWS', 'ECS', 'RDS', '웹서비스'],
        'complexity': '중',
    },
    'onpremise_infra': {
        'name': '온프레미스 인프라',
        'description': '전통적인 3계층 서버 구조 (WEB-WAS-DB)',
        'icon': '🏢',
        'file': 'onpremise_infra.xlsx',
        'tags': ['온프레미스', 'WEB', 'WAS', 'DB'],
        'complexity': '중',
    },
    'data_pipeline': {
        'name': '데이터 파이프라인',
        'description': 'ETL/ELT 데이터 처리 흐름 (Source → Transform → Load)',
        'icon': '🔄',
        'file': 'data_pipeline.xlsx',
        'tags': ['ETL', 'Airflow', '데이터 처리'],
        'complexity': '중',
    },
    'msa': {
        'name': '마이크로서비스 (MSA)',
        'description': 'API Gateway, K8s, Kafka 기반 MSA 구조',
        'icon': '🧩',
        'file': 'msa.xlsx',
        'tags': ['MSA', 'Kubernetes', 'API Gateway', 'Kafka'],
        'complexity': '상',
    },
}


def get_templates_dir() -> Path:
    """템플릿 디렉토리 경로 반환"""
    return Path(__file__).parent.parent / 'templates'


def get_template_list() -> List[Dict[str, Any]]:
    """템플릿 목록 반환"""
    return [
        {'id': tid, **tdata}
        for tid, tdata in TEMPLATE_CATALOG.items()
    ]


def generate_template_excel(template_id: str) -> bytes:
    """
    템플릿 ID로 엑셀 파일 바이트 반환
    
    Args:
        template_id: 템플릿 ID (예: 'aws_3tier')
    
    Returns:
        엑셀 파일 바이트
    
    Raises:
        ValueError: 템플릿 ID가 존재하지 않을 때
        FileNotFoundError: 엑셀 파일이 없을 때
    """
    if template_id not in TEMPLATE_CATALOG:
        raise ValueError(f"Unknown template: {template_id}")
    
    template = TEMPLATE_CATALOG[template_id]
    file_path = get_templates_dir() / template['file']
    
    if not file_path.exists():
        raise FileNotFoundError(f"Template file not found: {file_path}")
    
    with open(file_path, 'rb') as f:
        return f.read()


def get_template_path(template_id: str) -> Path:
    """템플릿 파일 경로 반환"""
    if template_id not in TEMPLATE_CATALOG:
        raise ValueError(f"Unknown template: {template_id}")
    
    return get_templates_dir() / TEMPLATE_CATALOG[template_id]['file']


def template_exists(template_id: str) -> bool:
    """템플릿 파일 존재 여부 확인"""
    if template_id not in TEMPLATE_CATALOG:
        return False
    
    file_path = get_templates_dir() / TEMPLATE_CATALOG[template_id]['file']
    return file_path.exists()


def get_available_templates() -> List[str]:
    """실제 파일이 존재하는 템플릿 ID 목록"""
    return [
        tid for tid in TEMPLATE_CATALOG.keys()
        if template_exists(tid)
    ]
