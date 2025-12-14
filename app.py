"""
AutoArchitect v2.0 - 시스템 구성도 자동 생성 도구
메인 Streamlit 애플리케이션
"""

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import io

# 내부 모듈
from ui.drawio_editor import get_drawio_editor_html
from core.templates import TEMPLATE_CATALOG, generate_template_excel, get_available_templates
from core.components import COMPONENT_CATALOG, generate_component_data, get_component_list


# ============================================================
# 세션 상태 관리
# ============================================================
def init_session_state():
    """세션 상태 초기화"""
    defaults = {
        'current_page': 'upload',
        'xml_content': None,
        'diagram_name': None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def go_to_editor(xml_content: str = None, diagram_name: str = None):
    """편집기 페이지로 이동"""
    st.session_state['current_page'] = 'editor'
    if xml_content:
        st.session_state['xml_content'] = xml_content
    if diagram_name:
        st.session_state['diagram_name'] = diagram_name


def go_to_upload():
    """업로드 페이지로 이동"""
    st.session_state['current_page'] = 'upload'


def reset_editor():
    """에디터 초기화"""
    st.session_state['xml_content'] = None
    st.session_state['diagram_name'] = None


# ============================================================
# XML 유틸리티
# ============================================================
def generate_xml_from_template(template_id: str) -> tuple:
    """템플릿 ID로 XML 생성"""
    from core.excel_parser import ExcelParser
    from core.layout_engine import LayoutEngine
    from core.drawio_generator import DrawioGenerator

    excel_bytes = generate_template_excel(template_id)

    parser = ExcelParser()
    sheets = parser.read_excel(io.BytesIO(excel_bytes))
    data = parser.parse_to_dict(sheets)

    layout_engine = LayoutEngine()
    positions = layout_engine.calculate_positions(data)

    generator = DrawioGenerator()
    xml_content = generator.generate_xml(data, positions)

    diagram_name = data.get('config', {}).get('다이어그램명', 'diagram')

    return xml_content, diagram_name


def merge_xml_diagrams(existing_xml: str, new_xml: str, offset_x: int = 0, offset_y: int = 0) -> str:
    """두 Draw.io XML을 병합"""
    import xml.etree.ElementTree as ET

    if not existing_xml or not existing_xml.strip():
        return new_xml

    try:
        existing_root = ET.fromstring(existing_xml)
        new_root = ET.fromstring(new_xml)

        existing_graph_root = existing_root.find('.//root')
        new_graph_root = new_root.find('.//root')

        if existing_graph_root is None or new_graph_root is None:
            return new_xml

        # 기존 XML에서 가장 큰 ID 찾기
        max_id = 1
        for cell in existing_graph_root.iter('mxCell'):
            cell_id = cell.get('id', '0')
            if cell_id.isdigit():
                max_id = max(max_id, int(cell_id))

        # 자동 오프셋 계산
        if offset_x == 0 and offset_y == 0:
            max_x = 0
            for cell in existing_graph_root.iter('mxCell'):
                geom = cell.find('mxGeometry')
                if geom is not None:
                    x = float(geom.get('x', 0))
                    width = float(geom.get('width', 0))
                    max_x = max(max_x, x + width)
            offset_x = int(max_x) + 100

        # ID 매핑 및 병합
        id_mapping = {'0': '0', '1': '1'}
        next_id = max_id + 1

        for cell in new_graph_root.findall('mxCell'):
            old_id = cell.get('id', '0')
            if old_id in ['0', '1']:
                continue

            new_id = str(next_id)
            id_mapping[old_id] = new_id
            next_id += 1

            cell.set('id', new_id)

            parent_id = cell.get('parent', '1')
            if parent_id in id_mapping:
                cell.set('parent', id_mapping[parent_id])

            for attr in ['source', 'target']:
                ref_id = cell.get(attr)
                if ref_id and ref_id in id_mapping:
                    cell.set(attr, id_mapping[ref_id])

            geom = cell.find('mxGeometry')
            if geom is not None and cell.get('vertex') == '1':
                x = float(geom.get('x', 0))
                y = float(geom.get('y', 0))
                geom.set('x', str(int(x + offset_x)))
                geom.set('y', str(int(y + offset_y)))

            existing_graph_root.append(cell)

        from xml.dom import minidom
        rough_string = ET.tostring(existing_root, encoding='unicode')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")

    except Exception as e:
        print(f"XML 병합 오류: {e}")
        return new_xml


# ============================================================
# 페이지 1: 엑셀 업로드
# ============================================================
def render_upload_page():
    """엑셀 업로드 페이지"""
    st.title("📥 엑셀 업로드")
    st.markdown("엑셀 파일로 시스템 구성도를 생성합니다")
    st.markdown("---")

    # 파일 업로드
    st.header("1️⃣ 엑셀 파일 선택")
    uploaded_file = st.file_uploader(
        "시스템 구성 정보가 담긴 엑셀 파일을 업로드하세요",
        type=['xlsx'],
        help="사이드바에서 샘플 파일을 다운로드하여 참고하세요"
    )

    if uploaded_file is None:
        st.info("""
        👆 **시작하기:**
        1. 사이드바에서 **샘플 엑셀**을 다운로드
        2. 엑셀 파일을 수정하거나 그대로 사용
        3. 위 버튼으로 업로드
        
        💡 **또는** 사이드바 메뉴에서 **편집기**를 선택하면 템플릿을 바로 열 수 있습니다.
        """)
        return

    st.success(f"✅ 파일: {uploaded_file.name}")

    # 데이터 검증
    st.header("2️⃣ 데이터 검증")

    with st.spinner("엑셀 파일 분석 중..."):
        excel_file = pd.ExcelFile(uploaded_file)
        if 'BOXES' not in excel_file.sheet_names:
            st.error("❌ 지원하지 않는 형식입니다. BOXES 시트가 필요합니다.")
            return

        from core.excel_parser import ExcelParser
        parser = ExcelParser()
        uploaded_file.seek(0)
        sheets = parser.read_excel(uploaded_file)
        validation = parser.validate_data(sheets)

    if not validation['is_valid']:
        st.error("❌ 데이터 검증 실패")
        for error in validation.get('errors', []):
            st.error(f"🔴 {error}")
        return

    st.success("✅ 검증 완료!")

    # 요약 정보
    data = parser.parse_to_dict(sheets)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("레이어", f"{len(data.get('layers', []))}개")
    with col2:
        st.metric("박스", f"{len(data.get('boxes', []))}개")
    with col3:
        st.metric("컴포넌트", f"{len(data.get('components', []))}개")
    with col4:
        st.metric("연결", f"{len(data.get('connections', []))}개")

    # 생성 버튼
    st.header("3️⃣ 구성도 생성")

    if st.button("🎨 구성도 생성 → 편집기로 이동", type="primary", use_container_width=True):
        with st.spinner("구성도 생성 중..."):
            from core.layout_engine import LayoutEngine
            from core.drawio_generator import DrawioGenerator

            layout_engine = LayoutEngine()
            positions = layout_engine.calculate_positions(data)

            generator = DrawioGenerator()
            xml_content = generator.generate_xml(data, positions)

            diagram_name = data.get('config', {}).get('다이어그램명', 'diagram')
            go_to_editor(xml_content, diagram_name)
            st.rerun()


# ============================================================
# 페이지 2: 편집기
# ============================================================
def render_editor_page():
    """편집기 페이지"""
    st.title("✏️ Draw.io 편집기")

    # 상단 컨트롤
    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])

    with col1:
        if st.session_state.get('xml_content'):
            st.success(f"📊 현재: **{st.session_state.get('diagram_name', 'diagram')}**")
        else:
            st.info("💡 아래 템플릿을 선택하거나, 빈 에디터에서 직접 그리세요")

    with col2:
        if st.button("🔄 새로", use_container_width=True):
            reset_editor()
            st.rerun()

    with col3:
        if st.button("📥 업로드", use_container_width=True):
            go_to_upload()
            st.rerun()

    with col4:
        _render_excel_export_button()

    st.markdown("---")

    # 템플릿/컴포넌트 탭
    tab1, tab2 = st.tabs(["📐 전체 템플릿", "🧩 컴포넌트"])

    with tab1:
        _render_template_gallery()

    with tab2:
        _render_component_gallery()

    st.markdown("---")

    # Draw.io 에디터
    xml_content = st.session_state.get('xml_content', '')
    editor_html = get_drawio_editor_html(xml_content, height=600)
    components.html(editor_html, height=650, scrolling=False)

    # 사용 가이드
    with st.expander("💡 사용 가이드", expanded=False):
        st.markdown("""
        **기본 조작:** 드래그(이동), 모서리 드래그(크기), 더블클릭(텍스트), 우클릭(스타일)
        
        **저장:** SVG(벡터), PNG(이미지), XML(Draw.io), 엑셀(수정용)
        """)


def _render_excel_export_button():
    """엑셀 내보내기 버튼"""
    if st.session_state.get('xml_content'):
        try:
            from core.xml_to_excel import xml_to_excel
            excel_bytes = xml_to_excel(st.session_state['xml_content'])
            st.download_button(
                label="📤 엑셀",
                data=excel_bytes,
                file_name=f"{st.session_state.get('diagram_name', 'diagram')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        except:
            st.button("📤 엑셀", disabled=True, use_container_width=True)
    else:
        st.button("📤 엑셀", disabled=True, use_container_width=True)


def _render_template_gallery():
    """템플릿 갤러리"""
    st.caption("💡 전체 아키텍처 레이아웃을 선택하세요")

    available = get_available_templates()
    cols = st.columns(len(available))

    for i, template_id in enumerate(available):
        template = TEMPLATE_CATALOG[template_id]
        with cols[i]:
            if st.button(
                    f"{template['icon']}\n{template['name'][:8]}",
                    key=f"tpl_{template_id}",
                    use_container_width=True,
                    help=template['description']
            ):
                with st.spinner(f"'{template['name']}' 로딩 중..."):
                    xml, name = generate_xml_from_template(template_id)
                    st.session_state['xml_content'] = xml
                    st.session_state['diagram_name'] = name
                    st.rerun()


def _render_component_gallery():
    """컴포넌트 갤러리"""
    has_diagram = st.session_state.get('xml_content') is not None

    if has_diagram:
        st.caption("💡 현재 다이어그램에 컴포넌트를 추가합니다")
    else:
        st.caption("💡 컴포넌트를 선택하면 새 다이어그램이 생성됩니다")

    component_list = get_component_list()

    # 2줄 배치
    row1 = component_list[:5]
    row2 = component_list[5:] if len(component_list) > 5 else []

    cols1 = st.columns(5)
    for i, comp in enumerate(row1):
        with cols1[i]:
            if st.button(
                    f"{comp['icon']}\n{comp['name'][:6]}",
                    key=f"comp_{comp['id']}",
                    use_container_width=True,
                    help=comp['description']
            ):
                _add_component(comp['id'], comp['name'])

    if row2:
        cols2 = st.columns(5)
        for i, comp in enumerate(row2):
            with cols2[i]:
                if st.button(
                        f"{comp['icon']}\n{comp['name'][:6]}",
                        key=f"comp_{comp['id']}",
                        use_container_width=True,
                        help=comp['description']
                ):
                    _add_component(comp['id'], comp['name'])


def _add_component(component_id: str, component_name: str):
    """컴포넌트 추가 (기존 다이어그램에 병합 또는 새로 생성)"""
    with st.spinner(f"'{component_name}' 추가 중..."):
        try:
            from core.layout_engine import LayoutEngine
            from core.drawio_generator import DrawioGenerator

            comp_data = generate_component_data(component_id)
            comp_meta = COMPONENT_CATALOG[component_id]
            comp_data['config']['캔버스너비'] = comp_meta['width']
            comp_data['config']['캔버스높이'] = comp_meta['height']

            layout_engine = LayoutEngine()
            positions = layout_engine.calculate_positions(comp_data)

            generator = DrawioGenerator()
            comp_xml = generator.generate_xml(comp_data, positions)

            # 기존 다이어그램이 있으면 병합, 없으면 새로 생성
            existing_xml = st.session_state.get('xml_content')

            if existing_xml:
                merged_xml = merge_xml_diagrams(existing_xml, comp_xml)
                st.session_state['xml_content'] = merged_xml
                st.session_state['diagram_name'] = f"{st.session_state.get('diagram_name', 'diagram')} + {component_name}"
            else:
                # 새 다이어그램으로 시작
                st.session_state['xml_content'] = comp_xml
                st.session_state['diagram_name'] = component_name

            st.rerun()
        except Exception as e:
            st.error(f"컴포넌트 추가 실패: {e}")


# ============================================================
# 사이드바
# ============================================================
def render_sidebar():
    """사이드바"""
    with st.sidebar:
        st.markdown("## 🏗️ AutoArchitect")
        st.caption("시스템 구성도 자동 생성")
        st.markdown("---")

        # 페이지 네비게이션
        st.markdown("### 📌 메뉴")
        current_page = st.session_state.get('current_page', 'upload')

        if st.button(
                "📥 엑셀 업로드",
                use_container_width=True,
                type="primary" if current_page == 'upload' else "secondary"
        ):
            st.session_state['current_page'] = 'upload'
            st.rerun()

        if st.button(
                "✏️ 편집기",
                use_container_width=True,
                type="primary" if current_page == 'editor' else "secondary"
        ):
            st.session_state['current_page'] = 'editor'
            st.rerun()

        st.markdown("---")

        # 업로드 페이지: 샘플 다운로드
        if current_page == 'upload':
            st.markdown("### 📥 샘플 다운로드")
            for template_id in get_available_templates():
                template = TEMPLATE_CATALOG[template_id]
                try:
                    excel_data = generate_template_excel(template_id)
                    st.download_button(
                        label=f"{template['icon']} {template['name']}",
                        data=excel_data,
                        file_name=f"{template_id}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key=f"dl_{template_id}",
                        use_container_width=True
                    )
                except:
                    pass

        # 편집기 페이지: 템플릿 설명
        elif current_page == 'editor':
            st.markdown("### 🎨 템플릿 안내")
            for template_id, template in TEMPLATE_CATALOG.items():
                with st.expander(f"{template['icon']} {template['name']}", expanded=False):
                    st.markdown(f"**{template['description']}**")
                    st.caption(f"복잡도: {template.get('complexity', '-')}")

        st.markdown("---")
        st.caption("v2.0 | Made with ❤️")


# ============================================================
# 메인
# ============================================================
def main():
    """메인 애플리케이션"""
    st.set_page_config(
        page_title="AutoArchitect v2.0",
        page_icon="🏗️",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    init_session_state()
    render_sidebar()

    current_page = st.session_state.get('current_page', 'upload')

    if current_page == 'upload':
        render_upload_page()
    elif current_page == 'editor':
        render_editor_page()
    else:
        render_upload_page()


if __name__ == "__main__":
    main()