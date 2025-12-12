# AutoArchitect 개발 로드맵

> 시스템 구성도 자동 생성 도구  
> 최종 수정: 2025-12

---

## 📌 프로젝트 비전

**"대화로 설명하면 아키텍처 다이어그램이 완성된다"**

엑셀 → Draw.io → PPT 워크플로우를 자동화하고,  
최종적으로 LLM을 통해 자연어로 다이어그램을 생성하는 도구

---

## 📅 전체 로드맵 요약

| Phase | 내용 | 우선순위 | 상태 |
|-------|------|---------|------|
| 0 | 기반 구축 | - | ✅ 완료 |
| 1 | 코드 정리/안정화 | 🔴 높음 | 대기 |
| 1.5 | Draw.io 임베딩 | 🔴 높음 | 대기 |
| 2 | 템플릿 갤러리 | 🟡 중간 | 대기 |
| 2.5 | 사용자 계정/개인화 | 🟡 중간 | 대기 |
| 3 | LLM 연동 | 🔴 높음 | 대기 |
| 4 | PPT 워크플로우 개선 | 🟢 낮음 | 대기 |
| 5 | 배포/문서화 | 🟡 중간 | 대기 |

---

## ✅ Phase 0: 기반 구축 (완료)

| 항목 | 상태 |
|------|------|
| 엑셀 파서 (행번호 기반) | ✅ 완료 |
| 레이아웃 엔진 (자동 배치) | ✅ 완료 |
| Draw.io XML 생성기 | ✅ 완료 |
| 헤더 영역 분리 | ✅ 완료 |
| 기본 연결선 | ✅ 완료 |
| Streamlit UI | ✅ 완료 |
| 우체국 빅데이터 샘플 | ✅ 완료 |

---

## 🔧 Phase 1: 코드 정리 및 안정화

### 목표
현재 여러 버전 파일이 혼재된 상태 → 단일 버전으로 통합

### 작업 항목
- [ ] 불필요한 파일 정리 (v5, v6 분리 코드 통합)
- [ ] 에러 핸들링 강화
- [ ] 코드 리팩토링 (중복 제거)
- [ ] 단위 테스트 작성
- [ ] 기존 기본형(LAYERS/COMPONENTS) 모드 유지 여부 결정

### 산출물
- 정리된 코드베이스
- 테스트 커버리지 80% 이상

---

## 🖼️ Phase 1.5: Draw.io 임베딩

### 목표
생성된 다이어그램을 화면에서 바로 편집 가능하도록 Draw.io 임베딩

### 현재 vs 개선

```
현재:
  생성 → .drawio 다운로드 → 별도 앱에서 열기 → 편집 → 내보내기

개선 후:
  생성 → 화면에서 바로 편집 → 저장/내보내기 (원클릭)
```

### 작업 항목
- [ ] Draw.io 임베딩 모드 연동
- [ ] XML → 임베디드 에디터 로드
- [ ] 편집 결과 저장 (postMessage 통신)
- [ ] SVG/PNG 내보내기 버튼
- [ ] 편집 후 XML 업데이트

### 기술 구현

```python
# Streamlit에서 Draw.io 임베딩
import streamlit.components.v1 as components

drawio_url = "https://embed.diagrams.net/?embed=1&proto=json&spin=1"
components.iframe(src=drawio_url, height=600)
```

### 핵심 기능

| 기능 | 방법 |
|------|------|
| XML 로드 | postMessage로 전송 |
| 편집 저장 | postMessage로 수신 |
| 이미지 추출 | export 이벤트 활용 |

### 산출물
- 웹 UI 내 Draw.io 에디터 임베딩
- 원클릭 내보내기 기능

---

## 🎨 Phase 2: 템플릿 갤러리

### 목표
사용자가 바로 사용하거나 수정할 수 있는 샘플 템플릿 제공

### 작업 항목
- [ ] AWS 3-Tier 아키텍처 템플릿
- [ ] 데이터 파이프라인 템플릿 (ETL)
- [ ] 마이크로서비스 아키텍처 템플릿
- [ ] 온프레미스 인프라 템플릿
- [ ] UI에서 템플릿 선택/미리보기/다운로드 기능

### 템플릿 목록 (예정)

| 템플릿명 | 용도 | 구성요소 |
|---------|------|---------|
| 우체국 빅데이터 | 빅데이터 플랫폼 | Hadoop, Kafka, Spark |
| AWS 3-Tier | 클라우드 웹서비스 | CloudFront, ECS, RDS |
| 데이터 파이프라인 | ETL 흐름 | Source, Transform, Load |
| MSA 구조 | 마이크로서비스 | API Gateway, Services, DB |
| 하이브리드 클라우드 | 온프레미스+클라우드 | On-Prem, VPN, Cloud |

### 산출물
- 5개 이상의 엑셀 템플릿
- 템플릿 선택 UI

---

## 👤 Phase 2.5: 사용자 계정 및 개인화

### 목표
사용자별 작업 히스토리, 템플릿, 설정 저장

### 작업 항목
- [ ] 로그인/회원가입 (PostgreSQL 연동)
- [ ] 작업 히스토리 저장/조회
- [ ] 내 템플릿 저장/관리
- [ ] 사용자 설정 저장 (기본 색상, 캔버스 크기 등)
- [ ] 프로젝트/폴더 관리

### 데이터 구조

```sql
-- 사용자
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    settings JSONB
);

-- 프로젝트
CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 다이어그램
CREATE TABLE diagrams (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id),
    name VARCHAR(255) NOT NULL,
    excel_data JSONB,
    xml_content TEXT,
    thumbnail TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 사용자 템플릿
CREATE TABLE user_templates (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    excel_data JSONB,
    is_public BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 기술 스택
- PostgreSQL (기존 DB 활용)
- streamlit-authenticator 또는 자체 구현

### 산출물
- 사용자 인증 시스템
- 개인 대시보드
- 히스토리/템플릿 관리 UI

---

## 🤖 Phase 3: LLM 연동 (핵심 차별화)

### 목표
자연어 대화로 아키텍처 다이어그램 생성

### 예상 사용자 경험

```
┌─────────────────────────────────────────────────────┐
│  💬 아키텍처를 설명해주세요                          │
│  ┌─────────────────────────────────────────────────┐│
│  │ "AWS 기반 3-tier 웹서비스야.                    ││
│  │  프론트는 CloudFront+S3,                        ││
│  │  백엔드는 ECS Fargate로 3개 서비스,             ││
│  │  DB는 Aurora MySQL 사용해"                      ││
│  └─────────────────────────────────────────────────┘│
│                                    [🎨 생성하기]     │
└─────────────────────────────────────────────────────┘
                    ↓
            [다이어그램 미리보기]
                    ↓
    💬 "로드밸런서 추가해줘"  →  [수정된 다이어그램]
```

### 작업 항목
- [ ] LLM 프롬프트 설계 (엑셀 구조 → JSON 스키마)
- [ ] LLM API 연동 (OpenAI / Claude)
- [ ] JSON → 엑셀 데이터 변환
- [ ] 대화형 수정 기능 ("DB를 3개로 늘려줘")
- [ ] 스트리밍 응답 UI
- [ ] 대화 컨텍스트 관리

### 기술 스택
- OpenAI API 또는 Anthropic Claude API
- JSON Schema 기반 구조화 출력

### 산출물
- 대화형 다이어그램 생성 기능
- 수정 요청 처리

---

## 📊 Phase 4: PPT 워크플로우 개선

### 목표
Draw.io에서 편집한 다이어그램을 PPT에 편집 가능한 객체로 변환

### 현재 워크플로우 (수동)

```
AutoArchitect → Draw.io XML → Draw.io에서 편집 
    → SVG 내보내기 → PPT 삽입 → 도형으로 변환
```

### 작업 항목
- [ ] SVG 내보내기 자동화 연구 (drawio-cli)
- [ ] 폰트 크기 보정 옵션 (PPT 변환 시 75% 축소)
- [ ] 원클릭 SVG 다운로드 버튼
- [ ] PPT 변환 가이드 문서

### 알려진 이슈
- SVG → PPT 변환 시 폰트 크기 1.33배 증가 (DPI 차이)
- 해결: 코드에서 미리 75% 축소 또는 PPT에서 수동 조정

### 산출물
- 개선된 PPT 변환 워크플로우
- 사용자 가이드

---

## 📦 Phase 5: 배포 및 문서화

### 작업 항목
- [ ] Docker 컨테이너화
- [ ] Streamlit Cloud 또는 자체 서버 배포
- [ ] 사용자 가이드 작성
- [ ] API 문서화
- [ ] CI/CD 파이프라인

### 산출물
- 배포된 웹 서비스
- 사용자 문서

---

## 📅 예상 일정

| Phase | 기간 | 우선순위 |
|-------|------|---------|
| Phase 1: 코드 정리 | 1주 | 🔴 높음 |
| Phase 1.5: Draw.io 임베딩 | 1주 | 🔴 높음 |
| Phase 2: 템플릿 갤러리 | 1-2주 | 🟡 중간 |
| Phase 2.5: 사용자 계정 | 1-2주 | 🟡 중간 |
| Phase 3: LLM 연동 | 2-3주 | 🔴 높음 |
| Phase 4: PPT 개선 | 1주 | 🟢 낮음 |
| Phase 5: 배포 | 1주 | 🟡 중간 |

---

## 🔮 미래 기능 (Backlog)

- 실시간 협업 편집
- 버전 관리 (다이어그램 히스토리)
- AI 기반 레이아웃 최적화
- Confluence/Notion 연동
- 아이콘 라이브러리 확장 (AWS, Azure, GCP 공식 아이콘)
- 다이어그램 공유 링크 생성

---

## 📝 변경 이력

| 날짜 | 버전 | 변경 내용 |
|------|------|----------|
| 2024-12 | v0.1 | 초기 로드맵 작성 |
| 2024-12 | v0.2 | Phase 1.5 (Draw.io 임베딩), Phase 2.5 (사용자 계정) 추가 |