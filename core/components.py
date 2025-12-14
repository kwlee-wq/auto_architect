"""
AutoArchitect - 컴포넌트 템플릿
재사용 가능한 작은 블록들 (DB 클러스터, Kafka, API Gateway 등)
"""

from typing import Dict, Any, List


# ==================== 컴포넌트 카탈로그 ====================

COMPONENT_CATALOG = {
    'db_cluster': {
        'name': 'DB 클러스터',
        'description': 'Master-Replica 구조의 데이터베이스 클러스터',
        'icon': '🗄️',
        'width': 300,
        'height': 150,
    },
    'kafka_cluster': {
        'name': 'Kafka 클러스터',
        'description': 'Broker 3대 구성의 메시지 큐',
        'icon': '📨',
        'width': 350,
        'height': 120,
    },
    'spark_cluster': {
        'name': 'Spark 클러스터',
        'description': 'Driver + Executor 구조',
        'icon': '⚡',
        'width': 300,
        'height': 150,
    },
    'load_balancer': {
        'name': '로드밸런서',
        'description': 'L4/L7 로드밸런서',
        'icon': '🔀',
        'width': 200,
        'height': 80,
    },
    'api_gateway': {
        'name': 'API Gateway',
        'description': 'REST API 게이트웨이',
        'icon': '🌐',
        'width': 250,
        'height': 100,
    },
    'storage': {
        'name': '스토리지',
        'description': '오브젝트/파일 스토리지',
        'icon': '💾',
        'width': 200,
        'height': 120,
    },
    'security_zone': {
        'name': '보안 영역',
        'description': 'DMZ/보안존 경계',
        'icon': '🔐',
        'width': 400,
        'height': 200,
    },
    'monitoring': {
        'name': '모니터링',
        'description': 'Prometheus + Grafana 모니터링 스택',
        'icon': '📊',
        'width': 300,
        'height': 120,
    },
    'k8s_cluster': {
        'name': 'K8s 클러스터',
        'description': 'Master + Worker 노드 구성',
        'icon': '☸️',
        'width': 350,
        'height': 180,
    },
    'cache_cluster': {
        'name': '캐시 클러스터',
        'description': 'Redis/Memcached 캐시',
        'icon': '🚀',
        'width': 250,
        'height': 100,
    },
}


def get_component_list() -> List[Dict[str, Any]]:
    """컴포넌트 목록 반환"""
    return [
        {'id': cid, **cdata}
        for cid, cdata in COMPONENT_CATALOG.items()
    ]


def generate_component_data(component_id: str) -> Dict[str, Any]:
    """
    컴포넌트 ID로 데이터 생성
    
    Returns:
        {
            'config': {...},
            'layers': [...],
            'boxes': [...],
            'components': [...],
            'connections': [...]
        }
    """
    if component_id not in COMPONENT_CATALOG:
        raise ValueError(f"Unknown component: {component_id}")
    
    meta = COMPONENT_CATALOG[component_id]
    width = meta['width']
    height = meta['height']
    
    # 각 컴포넌트별 데이터 정의
    generators = {
        'db_cluster': _create_db_cluster_data,
        'kafka_cluster': _create_kafka_cluster_data,
        'spark_cluster': _create_spark_cluster_data,
        'load_balancer': _create_load_balancer_data,
        'api_gateway': _create_api_gateway_data,
        'storage': _create_storage_data,
        'security_zone': _create_security_zone_data,
        'monitoring': _create_monitoring_data,
        'k8s_cluster': _create_k8s_cluster_data,
        'cache_cluster': _create_cache_cluster_data,
    }
    
    if component_id not in generators:
        raise ValueError(f"Component not implemented: {component_id}")
    
    return generators[component_id](width, height)


# ==================== 컴포넌트 데이터 생성 함수들 ====================

def _create_db_cluster_data(width: int, height: int) -> Dict[str, Any]:
    """DB 클러스터 컴포넌트"""
    return {
        'config': {'다이어그램명': 'DB Cluster', '캔버스너비': width, '캔버스높이': height},
        'layers': [
            {'id': 'L1', 'name': '', 'order': 1, 'bg_color': '흰색', 'height_percent': 100}
        ],
        'boxes': [
            {'id': 'B_DB', 'name': 'DB Cluster', 'parent_id': 'L1', 'row_number': 1, 
             'y_percent': 0, 'height_percent': 100, 'bg_color': '연두색', 'border_color': '진한녹색', 'font_size': 12},
            {'id': 'B_MASTER', 'name': 'Master', 'parent_id': 'B_DB', 'row_number': 1, 
             'y_percent': 30, 'height_percent': 60, 'bg_color': '흰색', 'border_color': '회색', 'font_size': 10},
            {'id': 'B_REPLICA1', 'name': 'Replica', 'parent_id': 'B_DB', 'row_number': 1, 
             'y_percent': 30, 'height_percent': 60, 'bg_color': '흰색', 'border_color': '회색', 'font_size': 10},
            {'id': 'B_REPLICA2', 'name': 'Replica', 'parent_id': 'B_DB', 'row_number': 1, 
             'y_percent': 30, 'height_percent': 60, 'bg_color': '흰색', 'border_color': '회색', 'font_size': 10},
        ],
        'components': [],
        'connections': [
            {'from_id': 'B_MASTER', 'to_id': 'B_REPLICA1', 'type': '데이터흐름', 'label': 'Sync', 'style': '점선'},
            {'from_id': 'B_MASTER', 'to_id': 'B_REPLICA2', 'type': '데이터흐름', 'label': 'Sync', 'style': '점선'},
        ]
    }


def _create_kafka_cluster_data(width: int, height: int) -> Dict[str, Any]:
    """Kafka 클러스터 컴포넌트"""
    return {
        'config': {'다이어그램명': 'Kafka Cluster', '캔버스너비': width, '캔버스높이': height},
        'layers': [
            {'id': 'L1', 'name': '', 'order': 1, 'bg_color': '흰색', 'height_percent': 100}
        ],
        'boxes': [
            {'id': 'B_KAFKA', 'name': 'Kafka Cluster', 'parent_id': 'L1', 'row_number': 1, 
             'y_percent': 0, 'height_percent': 100, 'bg_color': '주황색', 'border_color': '진한주황', 'font_size': 12},
            {'id': 'B_BROKER1', 'name': 'Broker-1', 'parent_id': 'B_KAFKA', 'row_number': 1, 
             'y_percent': 30, 'height_percent': 60, 'bg_color': '흰색', 'border_color': '회색', 'font_size': 10},
            {'id': 'B_BROKER2', 'name': 'Broker-2', 'parent_id': 'B_KAFKA', 'row_number': 1, 
             'y_percent': 30, 'height_percent': 60, 'bg_color': '흰색', 'border_color': '회색', 'font_size': 10},
            {'id': 'B_BROKER3', 'name': 'Broker-3', 'parent_id': 'B_KAFKA', 'row_number': 1, 
             'y_percent': 30, 'height_percent': 60, 'bg_color': '흰색', 'border_color': '회색', 'font_size': 10},
        ],
        'components': [],
        'connections': []
    }


def _create_spark_cluster_data(width: int, height: int) -> Dict[str, Any]:
    """Spark 클러스터 컴포넌트"""
    return {
        'config': {'다이어그램명': 'Spark Cluster', '캔버스너비': width, '캔버스높이': height},
        'layers': [
            {'id': 'L1', 'name': '', 'order': 1, 'bg_color': '흰색', 'height_percent': 100}
        ],
        'boxes': [
            {'id': 'B_SPARK', 'name': 'Spark Cluster', 'parent_id': 'L1', 'row_number': 1, 
             'y_percent': 0, 'height_percent': 100, 'bg_color': '하늘색', 'border_color': '진한파랑', 'font_size': 12},
            {'id': 'B_DRIVER', 'name': 'Driver', 'parent_id': 'B_SPARK', 'row_number': 1, 
             'y_percent': 25, 'height_percent': 65, 'bg_color': '흰색', 'border_color': '회색', 'font_size': 10},
            {'id': 'B_EXEC1', 'name': 'Executor', 'parent_id': 'B_SPARK', 'row_number': 1, 
             'y_percent': 25, 'height_percent': 65, 'bg_color': '흰색', 'border_color': '회색', 'font_size': 10},
            {'id': 'B_EXEC2', 'name': 'Executor', 'parent_id': 'B_SPARK', 'row_number': 1, 
             'y_percent': 25, 'height_percent': 65, 'bg_color': '흰색', 'border_color': '회색', 'font_size': 10},
        ],
        'components': [],
        'connections': [
            {'from_id': 'B_DRIVER', 'to_id': 'B_EXEC1', 'type': '데이터흐름', 'label': 'Task', 'style': '실선'},
            {'from_id': 'B_DRIVER', 'to_id': 'B_EXEC2', 'type': '데이터흐름', 'label': 'Task', 'style': '실선'},
        ]
    }


def _create_load_balancer_data(width: int, height: int) -> Dict[str, Any]:
    """로드밸런서 컴포넌트"""
    return {
        'config': {'다이어그램명': 'Load Balancer', '캔버스너비': width, '캔버스높이': height},
        'layers': [
            {'id': 'L1', 'name': '', 'order': 1, 'bg_color': '흰색', 'height_percent': 100}
        ],
        'boxes': [
            {'id': 'B_LB', 'name': 'Load Balancer\n(L4/L7)', 'parent_id': 'L1', 'row_number': 1, 
             'y_percent': 5, 'height_percent': 90, 'bg_color': '파란색', 'border_color': '진한파랑', 'font_size': 11},
        ],
        'components': [],
        'connections': []
    }


def _create_api_gateway_data(width: int, height: int) -> Dict[str, Any]:
    """API Gateway 컴포넌트"""
    return {
        'config': {'다이어그램명': 'API Gateway', '캔버스너비': width, '캔버스높이': height},
        'layers': [
            {'id': 'L1', 'name': '', 'order': 1, 'bg_color': '흰색', 'height_percent': 100}
        ],
        'boxes': [
            {'id': 'B_APIGW', 'name': 'API Gateway', 'parent_id': 'L1', 'row_number': 1, 
             'y_percent': 0, 'height_percent': 100, 'bg_color': '보라색', 'border_color': '진한보라', 'font_size': 12},
            {'id': 'B_AUTH', 'name': 'Auth', 'parent_id': 'B_APIGW', 'row_number': 1, 
             'y_percent': 30, 'height_percent': 55, 'bg_color': '흰색', 'border_color': '회색', 'font_size': 9},
            {'id': 'B_RATE', 'name': 'Rate\nLimit', 'parent_id': 'B_APIGW', 'row_number': 1, 
             'y_percent': 30, 'height_percent': 55, 'bg_color': '흰색', 'border_color': '회색', 'font_size': 9},
            {'id': 'B_ROUTE', 'name': 'Router', 'parent_id': 'B_APIGW', 'row_number': 1, 
             'y_percent': 30, 'height_percent': 55, 'bg_color': '흰색', 'border_color': '회색', 'font_size': 9},
        ],
        'components': [],
        'connections': []
    }


def _create_storage_data(width: int, height: int) -> Dict[str, Any]:
    """스토리지 컴포넌트"""
    return {
        'config': {'다이어그램명': 'Storage', '캔버스너비': width, '캔버스높이': height},
        'layers': [
            {'id': 'L1', 'name': '', 'order': 1, 'bg_color': '흰색', 'height_percent': 100}
        ],
        'boxes': [
            {'id': 'B_STORAGE', 'name': 'Object Storage', 'parent_id': 'L1', 'row_number': 1, 
             'y_percent': 0, 'height_percent': 100, 'bg_color': '노란색', 'border_color': '진한주황', 'font_size': 12},
            {'id': 'B_BUCKET1', 'name': 'Raw', 'parent_id': 'B_STORAGE', 'row_number': 1, 
             'y_percent': 30, 'height_percent': 55, 'bg_color': '흰색', 'border_color': '회색', 'font_size': 10},
            {'id': 'B_BUCKET2', 'name': 'Processed', 'parent_id': 'B_STORAGE', 'row_number': 1, 
             'y_percent': 30, 'height_percent': 55, 'bg_color': '흰색', 'border_color': '회색', 'font_size': 10},
        ],
        'components': [],
        'connections': []
    }


def _create_security_zone_data(width: int, height: int) -> Dict[str, Any]:
    """보안 영역 컴포넌트"""
    return {
        'config': {'다이어그램명': 'Security Zone', '캔버스너비': width, '캔버스높이': height},
        'layers': [
            {'id': 'L1', 'name': '', 'order': 1, 'bg_color': '흰색', 'height_percent': 100}
        ],
        'boxes': [
            {'id': 'B_ZONE', 'name': '🔐 보안 영역 (DMZ)', 'parent_id': 'L1', 'row_number': 1, 
             'y_percent': 0, 'height_percent': 100, 'bg_color': '분홍색', 'border_color': '진한빨강', 'font_size': 12},
            {'id': 'B_FW', 'name': 'Firewall', 'parent_id': 'B_ZONE', 'row_number': 1, 
             'y_percent': 25, 'height_percent': 60, 'bg_color': '흰색', 'border_color': '회색', 'font_size': 10},
            {'id': 'B_IDS', 'name': 'IDS/IPS', 'parent_id': 'B_ZONE', 'row_number': 1, 
             'y_percent': 25, 'height_percent': 60, 'bg_color': '흰색', 'border_color': '회색', 'font_size': 10},
            {'id': 'B_WAF', 'name': 'WAF', 'parent_id': 'B_ZONE', 'row_number': 1, 
             'y_percent': 25, 'height_percent': 60, 'bg_color': '흰색', 'border_color': '회색', 'font_size': 10},
        ],
        'components': [],
        'connections': []
    }


def _create_monitoring_data(width: int, height: int) -> Dict[str, Any]:
    """모니터링 컴포넌트"""
    return {
        'config': {'다이어그램명': 'Monitoring', '캔버스너비': width, '캔버스높이': height},
        'layers': [
            {'id': 'L1', 'name': '', 'order': 1, 'bg_color': '흰색', 'height_percent': 100}
        ],
        'boxes': [
            {'id': 'B_MON', 'name': 'Monitoring Stack', 'parent_id': 'L1', 'row_number': 1, 
             'y_percent': 0, 'height_percent': 100, 'bg_color': '연두색', 'border_color': '진한녹색', 'font_size': 12},
            {'id': 'B_PROM', 'name': 'Prometheus', 'parent_id': 'B_MON', 'row_number': 1, 
             'y_percent': 30, 'height_percent': 55, 'bg_color': '흰색', 'border_color': '회색', 'font_size': 10},
            {'id': 'B_GRAF', 'name': 'Grafana', 'parent_id': 'B_MON', 'row_number': 1, 
             'y_percent': 30, 'height_percent': 55, 'bg_color': '흰색', 'border_color': '회색', 'font_size': 10},
            {'id': 'B_ALERT', 'name': 'AlertManager', 'parent_id': 'B_MON', 'row_number': 1, 
             'y_percent': 30, 'height_percent': 55, 'bg_color': '흰색', 'border_color': '회색', 'font_size': 10},
        ],
        'components': [],
        'connections': [
            {'from_id': 'B_PROM', 'to_id': 'B_GRAF', 'type': '데이터흐름', 'label': 'Query', 'style': '실선'},
            {'from_id': 'B_PROM', 'to_id': 'B_ALERT', 'type': '데이터흐름', 'label': 'Alert', 'style': '점선'},
        ]
    }


def _create_k8s_cluster_data(width: int, height: int) -> Dict[str, Any]:
    """K8s 클러스터 컴포넌트"""
    return {
        'config': {'다이어그램명': 'K8s Cluster', '캔버스너비': width, '캔버스높이': height},
        'layers': [
            {'id': 'L1', 'name': '', 'order': 1, 'bg_color': '흰색', 'height_percent': 100}
        ],
        'boxes': [
            {'id': 'B_K8S', 'name': 'Kubernetes Cluster', 'parent_id': 'L1', 'row_number': 1, 
             'y_percent': 0, 'height_percent': 100, 'bg_color': '하늘색', 'border_color': '진한파랑', 'font_size': 12},
            {'id': 'B_MASTER', 'name': 'Master', 'parent_id': 'B_K8S', 'row_number': 1, 
             'y_percent': 25, 'height_percent': 65, 'bg_color': '흰색', 'border_color': '회색', 'font_size': 10},
            {'id': 'B_WORKER1', 'name': 'Worker-1', 'parent_id': 'B_K8S', 'row_number': 1, 
             'y_percent': 25, 'height_percent': 65, 'bg_color': '흰색', 'border_color': '회색', 'font_size': 10},
            {'id': 'B_WORKER2', 'name': 'Worker-2', 'parent_id': 'B_K8S', 'row_number': 1, 
             'y_percent': 25, 'height_percent': 65, 'bg_color': '흰색', 'border_color': '회색', 'font_size': 10},
            {'id': 'B_WORKER3', 'name': 'Worker-3', 'parent_id': 'B_K8S', 'row_number': 1, 
             'y_percent': 25, 'height_percent': 65, 'bg_color': '흰색', 'border_color': '회색', 'font_size': 10},
        ],
        'components': [],
        'connections': [
            {'from_id': 'B_MASTER', 'to_id': 'B_WORKER1', 'type': '데이터흐름', 'label': '', 'style': '점선'},
            {'from_id': 'B_MASTER', 'to_id': 'B_WORKER2', 'type': '데이터흐름', 'label': '', 'style': '점선'},
            {'from_id': 'B_MASTER', 'to_id': 'B_WORKER3', 'type': '데이터흐름', 'label': '', 'style': '점선'},
        ]
    }


def _create_cache_cluster_data(width: int, height: int) -> Dict[str, Any]:
    """캐시 클러스터 컴포넌트"""
    return {
        'config': {'다이어그램명': 'Cache Cluster', '캔버스너비': width, '캔버스높이': height},
        'layers': [
            {'id': 'L1', 'name': '', 'order': 1, 'bg_color': '흰색', 'height_percent': 100}
        ],
        'boxes': [
            {'id': 'B_CACHE', 'name': 'Redis Cluster', 'parent_id': 'L1', 'row_number': 1, 
             'y_percent': 0, 'height_percent': 100, 'bg_color': '분홍색', 'border_color': '진한빨강', 'font_size': 12},
            {'id': 'B_NODE1', 'name': 'Primary', 'parent_id': 'B_CACHE', 'row_number': 1, 
             'y_percent': 30, 'height_percent': 55, 'bg_color': '흰색', 'border_color': '회색', 'font_size': 10},
            {'id': 'B_NODE2', 'name': 'Replica', 'parent_id': 'B_CACHE', 'row_number': 1, 
             'y_percent': 30, 'height_percent': 55, 'bg_color': '흰색', 'border_color': '회색', 'font_size': 10},
        ],
        'components': [],
        'connections': [
            {'from_id': 'B_NODE1', 'to_id': 'B_NODE2', 'type': '데이터흐름', 'label': 'Sync', 'style': '점선'},
        ]
    }


def generate_component_xml(component_id: str, offset_x: int = 0, offset_y: int = 0) -> str:
    """
    컴포넌트 ID로 XML 직접 생성
    
    Args:
        component_id: 컴포넌트 ID
        offset_x: X 오프셋
        offset_y: Y 오프셋
    
    Returns:
        Draw.io XML 문자열
    """
    from core.layout_engine import LayoutEngine
    from core.drawio_generator import DrawioGenerator
    
    data = generate_component_data(component_id)
    
    # 레이아웃 계산
    layout_engine = LayoutEngine()
    data['config']['캔버스너비'] = COMPONENT_CATALOG[component_id]['width']
    data['config']['캔버스높이'] = COMPONENT_CATALOG[component_id]['height']
    
    positions = layout_engine.calculate_positions(data)
    
    # 오프셋 적용
    if offset_x != 0 or offset_y != 0:
        for key in positions:
            if 'x' in positions[key]:
                positions[key]['x'] += offset_x
            if 'y' in positions[key]:
                positions[key]['y'] += offset_y
    
    # XML 생성
    generator = DrawioGenerator()
    xml_content = generator.generate_xml(data, positions)
    
    return xml_content
