"""
AutoArchitect - 시스템 구성도 자동 생성 도구
Streamlit 메인 애플리케이션
"""

import streamlit as st
import streamlit.components.v1 as components
import urllib.parse
from pathlib import Path

# TODO: 모듈 import (개발 후 활성화)
# from core.excel_parser import ExcelParser
# from core.layout_engine import LayoutEngine
# from core.drawio_generator import DrawioGenerator

import pandas as pd  # 추가


def init_session_state():
    """세션 상태 초기화"""
    if 'xml_generated' not in st.session_state:
        st.session_state['xml_generated'] = False
    if 'xml_content' not in st.session_state:
        st.session_state['xml_content'] = None


def embed_drawio_editor(xml_content: str, diagram_name: str):
    """Draw.io 파일 다운로드 및 안내"""

    st.subheader("✅ 구성도 생성 완료!")

    # 탭으로 구분
    tab1, tab2 = st.tabs(["📥 다운로드", "ℹ️ 사용 방법"])

    with tab1:
        st.markdown("### 생성된 Draw.io 파일")

        col1, col2 = st.columns(2)

        with col1:
            st.download_button(
                label="📥 Draw.io 파일 다운로드",
                data=xml_content,
                file_name=f"{diagram_name}.drawio",
                mime="application/xml",
                help="Draw.io에서 열 수 있는 파일",
                key="main_drawio_download"  # 고유 키 추가
            )
            st.caption("👆 이 파일을 다운로드하세요")

        with col2:
            # XML 미리보기
            with st.expander("🔍 XML 미리보기"):
                st.code(xml_content[:500] + "...", language="xml")

        st.markdown("---")

        # 통계 정보
        import xml.etree.ElementTree as ET
        try:
            root = ET.fromstring(xml_content)
            cells = list(root.iter('mxCell'))
            vertices = [c for c in cells if c.get('vertex') == '1']
            edges = [c for c in cells if c.get('edge') == '1']

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("총 셀", len(cells))
            with col2:
                st.metric("컴포넌트", len(vertices))
            with col3:
                st.metric("연결선", len(edges))
        except:
            pass

    with tab2:
        st.markdown("""
        ### 📖 다음 단계
        
        #### 1️⃣ Draw.io에서 열기
        
        **옵션 A: 웹 브라우저 (추천)**
        1. [https://app.diagrams.net](https://app.diagrams.net) 접속
        2. 다운로드한 `.drawio` 파일을 드래그 & 드롭
        3. 다이어그램이 자동으로 열립니다
        
        **옵션 B: 데스크톱 앱**
        1. [Draw.io 데스크톱 다운로드](https://github.com/jgraph/drawio-desktop/releases)
        2. 설치 후 `.drawio` 파일 열기
        
        ---
        
        #### 2️⃣ 편집하기
        - 🖱️ **마우스 드래그**: 컴포넌트 이동
        - 📏 **모서리 드래그**: 크기 조절
        - 🖊️ **더블클릭**: 텍스트 수정
        - 🎨 **우클릭**: 스타일 변경
        - 🔗 **컴포넌트 연결**: 컴포넌트에서 화살표 드래그
        
        ---
        
        #### 3️⃣ 이미지로 저장
        Draw.io에서:
        1. **File** > **Export as** > **PNG** (또는 SVG, PDF)
        2. 해상도 선택 (기본 100% 권장)
        3. **Export** 클릭
        4. PPT/문서에 삽입
        
        ---
        
        #### 💡 팁
        - 배경 투명: Export 시 "Transparent Background" 체크
        - 고해상도: Export 시 Zoom을 200-300%로 설정
        - 여백 제거: Export 시 "Border Width" 를 0으로 설정
        """)

    st.markdown("---")
    st.success("✨ 수고하셨습니다! 생성된 파일을 Draw.io에서 열어 자유롭게 편집하세요.")

    # 사용 안내
    st.info(
        """
        💡 **편집 방법:**
        - 마우스로 컴포넌트 이동/크기 조절
        - 더블클릭으로 텍스트 수정
        - 우클릭으로 스타일 변경
        - 완료 후: File > Export as > PNG/SVG 또는 File > Save as
        """
    )

    # 추가 다운로드 옵션
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="📥 원본 XML 다운로드",
            data=xml_content,
            file_name=f"{diagram_name}.drawio",
            mime="application/xml",
            help="Draw.io 데스크톱에서 열 수 있습니다"
        )
    with col2:
        st.info("이미지 저장은 에디터에서 File > Export로 진행")


def render_sidebar():
    """사이드바 렌더링"""
    with st.sidebar:
        st.title("📊 AutoArchitect")
        st.markdown("---")

        st.markdown("### 📥 다운로드")

        # 계층형 템플릿/샘플 우선 표시
        st.markdown("**🔷 계층형 (추천)**")

        # 계층형 샘플 다운로드
        nested_sample_path = Path("templates/nested_sample.xlsx")
        if nested_sample_path.exists():
            with open(nested_sample_path, "rb") as f:
                file_bytes = f.read()

            st.download_button(
                label="📑 계층형 샘플 (우체국)",
                data=file_bytes,
                file_name="우체국_계층형_샘플.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="nested_sample_download"
            )
        else:
            st.button(
                "📑 계층형 샘플",
                help="templates/nested_sample.xlsx 파일이 없습니다. scripts/create_nested_sample.py를 실행하세요.",
                disabled=True
            )

        st.markdown("---")
        st.markdown("**🔶 기본형**")

        # 기존 템플릿 다운로드
        template_path = Path("templates/excel_template.xlsx")
        if template_path.exists():
            with open(template_path, "rb") as f:
                file_bytes = f.read()

            st.download_button(
                label="📄 기본 템플릿",
                data=file_bytes,
                file_name="시스템구성도_기본템플릿.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="basic_template_download"
            )

        # 기존 샘플 다운로드
        sample_path = Path("templates/sample_data.xlsx")
        if sample_path.exists():
            with open(sample_path, "rb") as f:
                file_bytes = f.read()

            st.download_button(
                label="📑 기본 샘플",
                data=file_bytes,
                file_name="기본_샘플.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="basic_sample_download"
            )


        st.markdown("---")
        st.info("💡 작성 가이드는 템플릿 파일 내 GUIDE 시트를 참고하세요")

        st.markdown("---")
        st.markdown("### ℹ️ 정보")
        st.markdown("**Version:** 0.1.0-dev")
        st.markdown("**Python:** 3.11")


def main():
    """메인 애플리케이션"""

    # 페이지 설정
    st.set_page_config(
        page_title="AutoArchitect - 시스템 구성도 생성기",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # 세션 상태 초기화
    init_session_state()

    # 사이드바
    render_sidebar()

    # 메인 영역
    st.title("🏗️ AutoArchitect")
    st.markdown("### 시스템 구성도 자동 생성 도구")
    st.markdown("엑셀로 시스템 정보를 입력하면 Draw.io 다이어그램을 자동 생성합니다")

    st.markdown("---")

    # Step 1: 파일 업로드
    st.header("1️⃣ 엑셀 파일 업로드")
    uploaded_file = st.file_uploader(
        "작성한 엑셀 파일을 업로드하세요",
        type=['xlsx'],
        help="템플릿 파일을 다운로드하여 작성 후 업로드"
    )

    if uploaded_file is not None:
        st.success(f"✅ 파일 업로드 완료: {uploaded_file.name}")

        # Step 2: 파싱 및 검증
        st.header("2️⃣ 데이터 검증")

        with st.spinner("엑셀 파일을 분석하는 중..."):
            # 파일 확인 - BOXES 시트가 있으면 계층형
            excel_file = pd.ExcelFile(uploaded_file)
            is_nested = 'BOXES' in excel_file.sheet_names

            if is_nested:
                from core.nested_excel_parser import NestedExcelParser
                parser = NestedExcelParser()
                st.info("🔷 계층형(Nested) 구조 감지")
            else:
                from core.excel_parser import ExcelParser
                parser = ExcelParser()
                st.info("🔶 기본(Flat) 구조 감지")

            sheets = parser.read_excel(uploaded_file)
            validation_result = parser.validate_data(sheets)
        # 검증 결과 표시
        if validation_result['is_valid']:
            st.success("✅ 검증 완료! 데이터가 정상입니다.")

            # 요약 정보
            data = parser.parse_to_dict(sheets)

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("레이어", f"{len(data['layers'])}개")
            with col2:
                st.metric("컴포넌트", f"{len(data['components'])}개")
            with col3:
                st.metric("연결", f"{len(data['connections'])}개")
            with col4:
                st.metric("그룹", f"{len(data.get('groups', []))}개")

            # 경고 메시지
            if validation_result['warnings']:
                with st.expander("⚠️ 경고 메시지 (생성은 가능)", expanded=False):
                    for warning in validation_result['warnings']:
                        st.warning(warning)

            # 정보 메시지
            if validation_result['infos']:
                with st.expander("ℹ️ 정보", expanded=False):
                    for info in validation_result['infos']:
                        st.info(info)

            # Step 3: 구조 미리보기
            st.header("3️⃣ 구조 미리보기")

            if is_nested:
                # 계층형 미리보기
                st.markdown("**📦 박스 구조:**")
                for box in data.get('boxes', []):
                    indent = "  " * (box['parent_id'].count('_') if '_' in box['parent_id'] else 0)
                    st.text(f"{indent}└─ {box['name']} ({box['width_percent']}% × {box['height_percent']}%)")

                st.markdown(f"**🔧 컴포넌트:** {len(data.get('components', []))}개")
            else:
                # 기존 레이어별 미리보기
                for layer in data['layers']:
                    st.subheader(f"📦 {layer['name']} (높이: {layer['height_percent']}%)")
                    components = [c for c in data['components']
                                  if c['layer_id'] == layer['id']]

                    if components:
                        comp_info = []
                        for c in components:
                            sub_count = len([s for s in data.get('sub_components', [])
                                             if s['parent_id'] == c['id']])
                            if sub_count > 0:
                                comp_info.append(f"{c['name']} ({sub_count}개 서브)")
                            else:
                                comp_info.append(c['name'])

                        st.text(f"   ➜ {', '.join(comp_info)}")
                    else:
                        st.text("   (컴포넌트 없음)")

                # 연결 요약
                if data.get('connections'):
                    st.subheader("🔗 연결 관계")
                    st.text(f"총 {len(data['connections'])}개의 연결")

            # Step 4: 구성도 생성
            st.header("4️⃣ 구성도 생성")

            if not is_nested:
                # 기존 레이아웃 설정 (기본 모드만)
                col1, col2 = st.columns(2)

                with col1:
                    layout_pattern = st.selectbox(
                        "레이아웃 패턴",
                        options=["수평레이어스택", "좌우분할", "중앙허브형", "좌우파이프라인"],
                        index=0,
                        help="수평레이어스택: 가장 일반적인 계층 구조"
                    )

                with col2:
                    default_margin = data['config'].get('여백비율', 15)
                    margin = st.slider(
                        "여백 비율 (%)",
                        min_value=5,
                        max_value=30,
                        value=int(default_margin)
                    )
                    data['config']['여백비율'] = margin

            # 생성 버튼
            if st.button("🎨 구성도 생성", type="primary", use_container_width=True):
                if is_nested:
                    # 계층형 생성
                    from core.nested_layout_engine import NestedLayoutEngine
                    from core.nested_drawio_generator import NestedDrawioGenerator

                    with st.spinner("계층 구조 계산 중..."):
                        layout_engine = NestedLayoutEngine()
                        positions = layout_engine.calculate_positions(data)

                    with st.spinner("Draw.io XML 생성 중..."):
                        generator = NestedDrawioGenerator()
                        xml_content = generator.generate_xml(data, positions)
                        st.session_state['xml_content'] = xml_content
                        st.session_state['xml_generated'] = True
                        st.session_state['diagram_name'] = data['config'].get('다이어그램명', 'diagram')
                else:
                    # 기존 방식
                    from core.layout_engine import LayoutEngine
                    from core.drawio_generator import DrawioGenerator

                    with st.spinner("레이아웃 계산 중..."):
                        layout_engine = LayoutEngine()
                        positions = layout_engine.calculate_positions(data, layout_pattern)

                        if data.get('connections'):
                            crossings = layout_engine.detect_crossings(positions, data['connections'])
                            if crossings > 5:
                                st.warning(
                                    f"⚠️ 예상 연결선 교차: {crossings}개\n"
                                    "Draw.io에서 수동 조정이 필요할 수 있습니다."
                                )

                    with st.spinner("Draw.io XML 생성 중..."):
                        generator = DrawioGenerator()
                        xml_content = generator.generate_xml(data, positions)
                        st.session_state['xml_content'] = xml_content
                        st.session_state['xml_generated'] = True
                        st.session_state['diagram_name'] = data['config'].get('다이어그램명', 'diagram')

                st.success("✅ 생성 완료!")

            # 생성된 경우 에디터 표시
            if st.session_state.get('xml_generated'):
                st.header("5️⃣ 웹에서 편집하기")
                embed_drawio_editor(
                    st.session_state['xml_content'],
                    st.session_state['diagram_name']
                )

        else:
            # 오류 표시
            st.error("❌ 데이터 검증 실패")

            for error in validation_result['errors']:
                st.error(f"🔴 {error}")

            st.info("엑셀 파일을 수정 후 다시 업로드해주세요")

    else:
        # 파일 미업로드 시 안내
        st.info(
            """
            👆 **시작하기:**
            
            1. 사이드바에서 엑셀 템플릿을 다운로드하세요
            2. 템플릿에 시스템 정보를 입력하세요
            3. 작성한 파일을 위의 업로드 버튼으로 업로드하세요
            4. 자동으로 구성도가 생성됩니다!
            """
        )


if __name__ == "__main__":
    main()