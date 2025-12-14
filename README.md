# AutoArchitect v2.0

시스템 구성도 자동 생성 도구 - 엑셀로 정의하고, Draw.io로 시각화

## 🎯 프로젝트 개요

제안서 및 보고서용 시스템 아키텍처 다이어그램을 엑셀 템플릿 기반으로 자동 생성하여
작업 시간을 80% 절감하고 일관된 품질을 유지합니다.

**최종 비전**: "대화로 설명하면 아키텍처 다이어그램이 완성된다"

## ⚡ 주요 기능

- 📊 **엑셀 템플릿 기반**: 익숙한 엑셀로 시스템 정보 입력
- 🎨 **자동 레이아웃**: 행번호 기반 스마트 배치
- ✏️ **웹 편집기**: Draw.io 임베디드로 바로 편집 (Ctrl+Z 지원)
- 📦 **템플릿 갤러리**: 7개 산업별 템플릿 제공
- 🧩 **컴포넌트 블록**: 10개 재사용 가능한 컴포넌트
- 🔍 **실시간 검증**: 데이터 무결성 자동 체크
- 📥 **다양한 출력**: Draw.io XML, PNG, SVG 지원

## 🚀 빠른 시작

### 설치
```bash
# 저장소 클론
git clone https://github.com/yourusername/AutoArchitect.git
cd AutoArchitect

# Python 3.11 가상환경 생성
python3.11 -m venv venv

# 가상환경 활성화
source venv/bin/activate  # Windows: venv\Scripts\activate

# 패키지 업데이트 
python -m pip install --upgrade pip

# 패키지 설치
pip install -r requirements.txt
```

### 실행
```bash
streamlit run app.py
```

브라우저에서 `http://localhost:8501` 접속

## 📖 사용 방법

### 방법 1: 템플릿 갤러리에서 시작
1. **템플릿 선택**: 7개 템플릿 중 원하는 것 선택
2. **바로 열기**: "🚀 바로 열기" 버튼 클릭
3. **편집**: Draw.io 에디터에서 수정
4. **저장**: PNG/SVG/XML로 내보내기

### 방법 2: 엑셀 업로드
1. **템플릿 다운로드**: 사이드바에서 엑셀 템플릿 다운로드
2. **정보 입력**: 레이어, 박스, 컴포넌트, 연결 관계 입력
3. **업로드**: 작성한 엑셀 파일 업로드
4. **생성**: 자동으로 구성도 생성

### 방법 3: 컴포넌트 조합
1. **컴포넌트 탭**: 🧩 컴포넌트 탭 선택
2. **추가**: 원하는 컴포넌트 클릭 (DB 클러스터, Kafka 등)
3. **조합**: 여러 컴포넌트를 추가하여 다이어그램 구성

## 📦 제공 템플릿

| 템플릿 | 설명 | 구성요소 |
|--------|------|----------|
| 우체국 빅데이터 | 금융권 빅데이터 플랫폼 | Hadoop, Kafka, Spark |
| BNK 클라우드 | 클라우드 기반 빅데이터 | Naver Cloud, Kubernetes |
| LG전자 GCP | GCP 데이터 플랫폼 | BigQuery, Composer, GCS |
| AWS 3-Tier | 클라우드 웹서비스 | CloudFront, ECS, RDS |
| 온프레미스 | 전통적 인프라 | WEB, WAS, DB 이중화 |
| 데이터 파이프라인 | ETL 흐름 | Source → Transform → Load |
| MSA 구조 | 마이크로서비스 | API Gateway, Services |

## 🧩 컴포넌트 블록

| 컴포넌트 | 용도 |
|----------|------|
| DB 클러스터 | Primary/Replica 구성 |
| Kafka 클러스터 | 메시지 브로커 |
| Spark 클러스터 | 분산 처리 |
| 로드밸런서 | 트래픽 분산 |
| API Gateway | API 관리 |
| 스토리지 레이어 | 저장소 계층 |
| 보안 영역 | DMZ/방화벽 |
| 모니터링 스택 | Prometheus/Grafana |
| Kubernetes | 컨테이너 오케스트레이션 |
| 캐시 레이어 | Redis/Memcached |

## 📁 프로젝트 구조

```
AutoArchitect/
├── app.py                      # Streamlit 메인 (492줄)
├── requirements.txt            # 의존성
├── README.md                   # 이 파일
│
├── core/
│   ├── templates.py            # 템플릿 카탈로그 (134줄)
│   ├── components.py           # 컴포넌트 카탈로그 (398줄)
│   ├── excel_parser.py         # 엑셀 파싱
│   ├── layout_engine.py        # 레이아웃 계산
│   ├── drawio_generator.py     # Draw.io XML 생성
│   └── xml_to_excel.py         # XML→엑셀 역변환
│
├── ui/
│   ├── drawio_editor.py        # Draw.io 임베딩
│   ├── sidebar.py              # 사이드바
│   └── gallery.py              # 갤러리 UI
│
├── templates/
│   ├── postoffice_bigdata.xlsx # 우체국 빅데이터
│   ├── cloud_bigdata.xlsx      # BNK 클라우드
│   ├── gcp_data_platform.xlsx  # LG전자 GCP
│   ├── aws_3tier.xlsx          # AWS 3-Tier
│   ├── onpremise_infra.xlsx    # 온프레미스
│   ├── data_pipeline.xlsx      # 데이터 파이프라인
│   └── msa.xlsx                # MSA 구조
│
├── docs/
│   ├── ROADMAP.md              # 개발 로드맵
│   └── HISTORY.md              # 변경 이력
│
└── tests/
    └── ...                     # 단위 테스트
```

## 🛠️ 기술 스택

- **Python 3.11**
- **Streamlit 1.29+**: 웹 UI
- **Pandas 2.1+**: 엑셀 데이터 처리
- **OpenPyXL 3.1+**: 엑셀 파일 생성
- **Draw.io**: 다이어그램 편집 (임베디드)

## 📋 개발 현황

- [x] Phase 0: 프로젝트 셋업
- [x] Phase 1: 엑셀 템플릿 & 파서
- [x] Phase 2: Draw.io XML 생성
- [x] Phase 3: 레이아웃 엔진
- [x] Phase 4: Streamlit UI
- [x] Phase 1.5: 웹 에디터 임베딩
- [x] Phase 2: 템플릿 갤러리 (7개)
- [x] 컴포넌트 블록 (10개)
- [x] 코드 리팩토링 (90% 감소)
- [ ] Phase 2.5: 사용자 계정/개인화
- [ ] Phase 3: LLM 연동 (자연어 → 다이어그램)
- [ ] Phase 4: PPT 워크플로우 개선
- [ ] Phase 5: 배포/문서화

## 🔮 향후 계획

### Phase 3: LLM 연동 (핵심 기능)
```
사용자: "AWS 기반 3-tier 웹서비스 그려줘"
    ↓
[자동 다이어그램 생성]
    ↓
사용자: "DB를 Aurora로 바꿔줘"
    ↓
[수정된 다이어그램]
```

### Phase 2.5: 사용자 계정
- 작업 히스토리 저장
- 내 템플릿 관리
- 프로젝트 폴더

## 📄 라이선스

ZettaSoft © 2025