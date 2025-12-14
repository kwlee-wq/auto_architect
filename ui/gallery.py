"""
AutoArchitect - 템플릿/컴포넌트 갤러리 UI
"""

import streamlit as st
from typing import Callable

from core.templates import TEMPLATE_CATALOG, get_available_templates
from core.components import COMPONENT_CATALOG, get_component_list


def render_template_gallery(on_select: Callable[[str], None]):
    """
    템플릿 갤러리 렌더링
    
    Args:
        on_select: 템플릿 선택 시 콜백 (template_id)
    """
    st.markdown("#### 📐 전체 템플릿")
    st.caption("클릭하면 새 다이어그램으로 열립니다")
    
    available = get_available_templates()
    
    # 3열 그리드
    cols = st.columns(3)
    
    for idx, template_id in enumerate(available):
        template = TEMPLATE_CATALOG[template_id]
        col = cols[idx % 3]
        
        with col:
            if st.button(
                f"{template['icon']} {template['name']}",
                key=f"tmpl_{template_id}",
                use_container_width=True,
                help=template['description']
            ):
                on_select(template_id)
    
    # 안내
    if not available:
        st.warning("사용 가능한 템플릿이 없습니다.")


def render_component_gallery(on_select: Callable[[str], None], has_diagram: bool = False):
    """
    컴포넌트 갤러리 렌더링
    
    Args:
        on_select: 컴포넌트 선택 시 콜백 (component_id)
        has_diagram: 현재 다이어그램이 있는지 여부
    """
    st.markdown("#### 🧩 컴포넌트 추가")
    
    if not has_diagram:
        st.info("💡 먼저 템플릿을 열거나 엑셀을 업로드하세요. 컴포넌트는 기존 다이어그램에 추가됩니다.")
        st.caption("아래 컴포넌트들은 비활성화 상태입니다.")
    else:
        st.caption("클릭하면 현재 다이어그램에 추가됩니다")
    
    components = get_component_list()
    
    # 5열 그리드 (2줄)
    row1 = st.columns(5)
    row2 = st.columns(5)
    
    for idx, comp in enumerate(components):
        if idx < 5:
            col = row1[idx]
        else:
            col = row2[idx - 5]
        
        with col:
            btn_label = f"{comp['icon']}\n{comp['name']}"
            
            if st.button(
                btn_label,
                key=f"comp_{comp['id']}",
                use_container_width=True,
                disabled=not has_diagram,
                help=comp['description']
            ):
                on_select(comp['id'])


def render_gallery_tabs(
    on_template_select: Callable[[str], None],
    on_component_select: Callable[[str], None],
    has_diagram: bool = False
):
    """
    템플릿/컴포넌트 탭 렌더링
    
    Args:
        on_template_select: 템플릿 선택 콜백
        on_component_select: 컴포넌트 선택 콜백
        has_diagram: 현재 다이어그램 존재 여부
    """
    tab1, tab2 = st.tabs(["📐 전체 템플릿", "🧩 컴포넌트"])
    
    with tab1:
        render_template_gallery(on_template_select)
    
    with tab2:
        render_component_gallery(on_component_select, has_diagram)
