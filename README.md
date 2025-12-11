# AutoArchitect

시스템 구성도 자동 생성 도구 - 엑셀로 정의하고, Draw.io로 시각화

## 🎯 프로젝트 개요

제안서 및 보고서용 시스템 아키텍처 다이어그램을 엑셀 템플릿 기반으로 자동 생성하여
작업 시간을 80% 절감하고 일관된 품질을 유지합니다.

## ⚡ 주요 기능

- 📊 **엑셀 템플릿 기반**: 익숙한 엑셀로 시스템 정보 입력
- 🎨 **자동 레이아웃**: 4가지 레이아웃 패턴 지원 (수평스택, 좌우분할, 허브형, 파이프라인)
- ✏️ **웹 편집기**: Draw.io 임베디드로 바로 편집
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
# 가상환경 생성 및 활성화
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

1. **템플릿 다운로드**: 웹 UI에서 엑셀 템플릿 다운로드
2. **정보 입력**: 시스템 레이어, 컴포넌트, 연결 관계 입력
3. **업로드**: 작성한 엑셀 파일 업로드
4. **생성**: 자동으로 구성도 생성 및 웹 에디터에 표시
5. **편집**: 웹에서 바로 수정하거나 Draw.io 파일로 다운로드
6. **저장**: PNG/SVG로 저장하여 PPT에 삽입

## 📁 프로젝트 구조
```
AutoArchitect/
├── app.py                      # Streamlit 메인
├── requirements.txt
├── README.md
├── core/
│   ├── excel_parser.py         # 엑셀 파싱
│   ├── drawio_generator.py     # Draw.io XML 생성
│   └── layout_engine.py        # 레이아웃 계산
├── utils/
│   ├── constants.py            # 상수 정의
│   └── validators.py           # 검증 함수
├── templates/
│   ├── excel_template.xlsx     # 엑셀 템플릿
│   └── sample_data.xlsx        # 샘플 데이터
└── tests/
    └── ...                     # 단위 테스트
```

## 🛠️ 기술 스택

- **Python 3.11**
- **Streamlit**: 웹 UI
- **Pandas**: 엑셀 데이터 처리
- **Draw.io**: 다이어그램 편집

## 📋 개발 현황

- [ ] Phase 0: 프로젝트 셋업
- [ ] Phase 1: 엑셀 템플릿 & 파서
- [ ] Phase 2: Draw.io XML 생성
- [ ] Phase 3: 레이아웃 엔진
- [ ] Phase 4: Streamlit UI
- [ ] Phase 5: 웹 에디터 임베딩
- [ ] Phase 6: 테스트 & 문서화

## 📄 라이선스

ZettaSoft