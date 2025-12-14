"""
AutoArchitect - 사이드바 UI
"""

import streamlit as st
from pathlib import Path


def render_sidebar():
    """사이드바 렌더링"""
    with st.sidebar:
        st.title("📊 AutoArchitect")
        st.caption("v2.0 - 시스템 구성도 생성기")
        
        st.markdown("---")
        
        # 페이지 네비게이션
        st.markdown("### 📑 메뉴")
        
        page = st.radio(
            "페이지 선택",
            options=["📤 엑셀 업로드", "✏️ 편집기"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # 도움말
        with st.expander("💡 사용 가이드", expanded=False):
            st.markdown("""
            **기본 워크플로우:**
            1. 📤 엑셀 업로드 → XML 생성
            2. ✏️ 편집기에서 수정
            3. 📥 SVG/PNG 다운로드
            
            **빠른 시작:**
            - 편집기에서 템플릿 바로 열기
            - 컴포넌트 추가로 확장
            
            **양방향 편집:**
            - 📤 엑셀 내보내기 → 수정 → 재업로드
            """)
        
        st.markdown("---")
        st.caption("© 2024 ZettaSoft")
        
        return page


def render_download_section():
    """다운로드 섹션 (엑셀 업로드 페이지용)"""
    st.markdown("### 📥 다운로드")
    
    templates_dir = Path(__file__).parent.parent / 'templates'
    
    # 빈 템플릿
    template_path = templates_dir / 'excel_template.xlsx'
    if template_path.exists():
        with open(template_path, 'rb') as f:
            st.download_button(
                label="📄 빈 템플릿",
                data=f.read(),
                file_name="시스템구성도_템플릿.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
    
    # 샘플 (우체국)
    sample_path = templates_dir / 'postoffice_bigdata.xlsx'
    if sample_path.exists():
        with open(sample_path, 'rb') as f:
            st.download_button(
                label="📑 샘플 (우체국)",
                data=f.read(),
                file_name="우체국_빅데이터_샘플.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
