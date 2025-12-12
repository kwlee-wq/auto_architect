"""
AutoArchitect - 시스템 구성도 자동 생성 도구
Streamlit 메인 애플리케이션 (v2.0 리팩토링)
"""

import streamlit as st
from pathlib import Path
import pandas as pd
import xml.etree.ElementTree as ET

# 프로젝트 모듈 임포트
from core.excel_parser import ExcelParser, NestedExcelParser, create_parser, detect_excel_type
from core.layout_engine import LayoutEngine, NestedLayoutEngine, create_layout_engine
from core.drawio_generator import DrawioGenerator, NestedDrawioGenerator, create_drawio_generator
from utils.constants import LAYOUT_PATTERNS


def init_session_state():
    """세션 상태 초기화"""
    defaults = {
        'xml_generated': False,
        'xml_content': None,
        'diagram_name': 'diagram',
        'is_nested': False
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def render_sidebar():
    """사이드바 렌더링"""
    with st.sidebar:
        st.title("📊 AutoArchitect")
        st.markdown("---")

        st.markdown("### 📥 다운로드")

        # 계층형 템플릿 (추천)
        st.markdown("**🔷 계층형 (추천)**")
        nested_sample_path = Path("templates/nested_sample.xlsx")
        if nested_sample_path.exists():
            with open(nested_sample_path, "rb") as f:
                st.download_button(
                    label="📑 계층형 샘플 (우체국)",
                    data=f.read(),
                    file_name="우체국_계층형_샘플.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="nested_sample_download"
                )
        else:
            st.button("📑 계층형 샘플", disabled=True, help="샘플 파일이 없습니다")

        st.markdown("---")
        st.markdown("**🔶 기본형**")

        # 기본 템플릿
        template_path = Path("templates/excel_template.xlsx")
        if template_path.exists():
            with open(template_path, "rb") as f:
                st.download_button(
                    label="📄 기본 템플릿",
                    data=f.read(),
                    file_name="시스템구성도_기본템플릿.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="basic_template_download"
                )

        # 기본 샘플
        sample_path = Path("templates/sample_data.xlsx")
        if sample_path.exists():
            with open(sample_path, "rb") as f:
                st.download_button(
                    label="📑 기본 샘플",
                    data=f.read(),
                    file_name="기본_샘플.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="basic_sample_download"
                )

        st.markdown("---")
        st.info("💡 작성 가이드는 템플릿 파일 내 GUIDE 시트를 참고하세요")

        st.markdown("---")
        st.markdown("### ℹ️ 정보")
        st.markdown("**Version:** 2.0.0")
        st.markdown("**Python:** 3.11")


def show_download_section(xml_content: str, diagram_name: str):
    """다운로드 섹션 표시"""
    st.subheader("✅ 구성도 생성 완료!")

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
                key="main_drawio_download",
                type="primary"
            )
            st.caption("👆 이 파일을 다운로드하세요")

        with col2:
            with st.expander("🔍 XML 미리보기"):
                st.code(xml_content[:500] + "...", language="xml")

        st.markdown("---")

        # 통계 정보
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
        
        ---
        
        #### 3️⃣ 이미지로 저장
        Draw.io에서:
        1. **File** > **Export as** > **PNG** (또는 SVG, PDF)
        2. **Export** 클릭
        3. PPT/문서에 삽입
        """)

    st.markdown("---")
    st.success("✨ 생성된 파일을 Draw.io에서 열어 편집하세요!")


def show_preview(data: dict, is_nested: bool):
    """구조 미리보기"""
    st.header("3️⃣ 구조 미리보기")

    if is_nested:
        # 계층형 미리보기
        st.markdown("**📦 박스 구조:**")
        for box in data.get('boxes', [])[:10]:  # 최대 10개
            row_num = box.get('row_number', '?')
            st.text(f"└─ {box['name']} (행{row_num}, 높이{box.get('height_percent', '?')}%)")

        if len(data.get('boxes', [])) > 10:
            st.text(f"   ... 외 {len(data['boxes']) - 10}개")

        st.markdown(f"**🔧 컴포넌트:** {len(data.get('components', []))}개")
    else:
        # 기본형 미리보기
        for layer in data.get('layers', []):
            st.subheader(f"📦 {layer['name']} (높이: {layer.get('height_percent', '?')}%)")
            components = [
                c for c in data.get('components', [])
                if c.get('layer_id') == layer['id']
            ]

            if components:
                comp_names = [c['name'] for c in components[:5]]
                if len(components) > 5:
                    comp_names.append(f"외 {len(components) - 5}개")
                st.text(f"   ➜ {', '.join(comp_names)}")
            else:
                st.text("   (컴포넌트 없음)")

        # 연결 요약
        if data.get('connections'):
            st.subheader("🔗 연결 관계")
            st.text(f"총 {len(data['connections'])}개의 연결")


def main():
    """메인 애플리케이션"""
    st.set_page_config(
        page_title="AutoArchitect - 시스템 구성도 생성기",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    init_session_state()
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
            # 파일 타입 감지
            uploaded_file.seek(0)
            excel_type = detect_excel_type(uploaded_file)
            is_nested = (excel_type == 'nested')
            st.session_state['is_nested'] = is_nested

            if is_nested:
                st.info("🔷 계층형(Nested) 구조 감지")
                parser = NestedExcelParser()
            else:
                st.info("🔶 기본(Flat) 구조 감지")
                parser = ExcelParser()

            # 파일 읽기 및 검증
            uploaded_file.seek(0)
            sheets = parser.read_excel(uploaded_file)
            validation_result = parser.validate_data(sheets)

        # 검증 결과 표시
        if validation_result['is_valid']:
            st.success("✅ 검증 완료! 데이터가 정상입니다.")

            # 데이터 파싱
            data = parser.parse_to_dict(sheets)

            # 요약 정보
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("레이어", f"{len(data.get('layers', []))}개")
            with col2:
                if is_nested:
                    st.metric("박스", f"{len(data.get('boxes', []))}개")
                else:
                    st.metric("컴포넌트", f"{len(data.get('components', []))}개")
            with col3:
                st.metric("연결", f"{len(data.get('connections', []))}개")
            with col4:
                if is_nested:
                    st.metric("컴포넌트", f"{len(data.get('components', []))}개")
                else:
                    st.metric("그룹", f"{len(data.get('groups', []))}개")

            # 경고/정보 메시지
            warnings = validation_result.get('warnings', [])
            if warnings:
                with st.expander("⚠️ 경고 메시지", expanded=False):
                    for warning in warnings:
                        st.warning(warning)

            infos = validation_result.get('infos', [])
            if infos:
                with st.expander("ℹ️ 정보", expanded=False):
                    for info in infos:
                        st.info(info)

            # Step 3: 미리보기
            show_preview(data, is_nested)

            # Step 4: 생성
            st.header("4️⃣ 구성도 생성")

            # 기본형만 레이아웃 옵션 제공
            if not is_nested:
                col1, col2 = st.columns(2)
                with col1:
                    layout_pattern = st.selectbox(
                        "레이아웃 패턴",
                        options=["수평레이어스택", "좌우분할", "중앙허브형", "좌우파이프라인"],
                        index=0,
                        help="수평레이어스택: 가장 일반적인 계층 구조"
                    )
                with col2:
                    default_margin = data.get('config', {}).get('여백비율', 15)
                    margin = st.slider(
                        "여백 비율 (%)",
                        min_value=5,
                        max_value=30,
                        value=int(default_margin)
                    )
                    data['config']['여백비율'] = margin

            # 생성 버튼
            if st.button("🎨 구성도 생성", type="primary", use_container_width=True):
                with st.spinner("구성도를 생성하는 중..."):
                    # 레이아웃 엔진 선택
                    layout_engine = create_layout_engine(is_nested)

                    if is_nested:
                        positions = layout_engine.calculate_positions(data)
                    else:
                        positions = layout_engine.calculate_positions(data, layout_pattern)

                        # 교차 검사
                        if data.get('connections'):
                            crossings = layout_engine.detect_crossings(positions, data['connections'])
                            if crossings > 5:
                                st.warning(
                                    f"⚠️ 예상 연결선 교차: {crossings}개\n"
                                    "Draw.io에서 수동 조정이 필요할 수 있습니다."
                                )

                    # Draw.io 생성기 선택
                    generator = create_drawio_generator(is_nested)
                    xml_content = generator.generate_xml(data, positions)

                    # 세션 저장
                    st.session_state['xml_content'] = xml_content
                    st.session_state['xml_generated'] = True
                    st.session_state['diagram_name'] = data.get('config', {}).get('다이어그램명', 'diagram')

                st.success("✅ 생성 완료!")

            # 생성 결과 표시
            if st.session_state.get('xml_generated'):
                st.header("5️⃣ 다운로드")
                show_download_section(
                    st.session_state['xml_content'],
                    st.session_state['diagram_name']
                )

        else:
            # 오류 표시
            st.error("❌ 데이터 검증 실패")
            for error in validation_result.get('errors', []):
                st.error(f"🔴 {error}")
            st.info("엑셀 파일을 수정 후 다시 업로드해주세요")

    else:
        # 파일 미업로드 안내
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
