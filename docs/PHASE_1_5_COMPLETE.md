# AutoArchitect v1.5 - Phase 1.5 완료

## 🎯 Phase 1.5: Draw.io 임베딩

### ✅ 완료된 작업

| 작업 | 상태 | 설명 |
|------|------|------|
| Draw.io iframe 임베딩 | ✅ | `embed.diagrams.net` 사용 |
| postMessage 통신 | ✅ | JSON 프로토콜로 양방향 통신 |
| XML 로드 | ✅ | Base64 인코딩으로 안전하게 전송 |
| SVG 내보내기 | ✅ | 버튼 클릭으로 즉시 다운로드 |
| PNG 내보내기 | ✅ | 2배 해상도로 고품질 출력 |
| XML 저장 | ✅ | 편집된 다이어그램 저장 |
| 화면 맞춤 | ✅ | fit 레이아웃 적용 |
| 상태 표시 | ✅ | 로딩/준비/저장 상태 표시 |

---

## 📁 새 파일 구조

```
auto_architect/
├── app.py                              # 메인 앱 (Draw.io 임베딩 통합)
├── requirements.txt
├── components/
│   ├── __init__.py
│   └── drawio_editor.py               # Draw.io 임베딩 컴포넌트 (신규)
├── core/
│   ├── __init__.py
│   ├── nested_excel_parser.py
│   ├── nested_layout_engine.py
│   └── nested_drawio_generator.py
└── utils/
    └── __init__.py
```

---

## 🆕 주요 변경사항

### 1. Draw.io 임베딩 에디터 (`components/drawio_editor.py`)

```python

from ui import drawio_editor

# 에디터 렌더링
drawio_editor(xml_content, height=650)
```

**기능:**
- 웹 페이지 내 Draw.io 에디터 직접 임베딩
- 툴바: SVG/PNG/XML 내보내기, 화면 맞춤
- 상태 바: 연결 상태, 마지막 저장 시간

### 2. 새 app.py 워크플로우

```
기존:
  생성 → .drawio 다운로드 → 별도 앱 → 편집 → 내보내기

개선 후:
  생성 → 화면에서 바로 편집 → 버튼 클릭으로 내보내기 ✨
```

### 3. postMessage 통신

| 이벤트 | 방향 | 용도 |
|--------|------|------|
| `init` | Draw.io → App | 에디터 준비 완료 |
| `load` | App → Draw.io | 다이어그램 로드 |
| `export` | 양방향 | 이미지 내보내기 |
| `save` | Draw.io → App | 변경사항 저장 |

---

## 🚀 실행 방법

```bash
# 1. 디렉토리 이동
cd auto_architect

# 2. 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 패키지 설치
pip install -r requirements.txt

# 4. 실행
streamlit run app.py
```

브라우저에서 `http://localhost:8501` 접속

---

## 📸 스크린샷

### 1. 메인 화면
- 엑셀 파일 업로드
- 데이터 검증 및 요약
- 구성도 생성 버튼

### 2. Draw.io 에디터 (임베딩)
- 상단 툴바: SVG/PNG/XML 내보내기
- 중앙: Draw.io 에디터
- 하단: 연결 상태 표시

### 3. 내보내기
- SVG: 벡터 이미지 (PPT 권장)
- PNG: 래스터 이미지 (2배 해상도)
- XML: Draw.io 파일

---

## ⚠️ 알려진 제한사항

1. **브라우저 보안**: 일부 환경에서 iframe 차단 가능
2. **네트워크 필요**: Draw.io는 온라인 서비스
3. **저장 동기화**: 편집 내용이 Streamlit 세션에 자동 반영되지 않음
   - 해결: XML 저장 버튼으로 수동 다운로드

---

## 📅 다음 단계 (Phase 2)

- [ ] 템플릿 갤러리 (5개+)
- [ ] AWS/Azure/GCP 아이콘 지원
- [ ] 사용자 커스텀 템플릿 저장

---

## 📝 변경 이력

| 날짜      | 버전 | 내용 |
|---------|------|------|
| 2025-12 | v1.5.0 | Phase 1.5 완료 - Draw.io 임베딩 |
