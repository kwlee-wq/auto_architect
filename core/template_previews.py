"""
AutoArchitect - 템플릿 미리보기 생성기
Phase 2.1: 레이아웃/컴포넌트 템플릿 hover 미리보기
"""

from typing import Dict


class LayoutPreview:
    """레이아웃 패턴 미리보기 SVG 생성"""

    @staticmethod
    def get_all_previews() -> Dict[str, str]:
        """모든 레이아웃 패턴 미리보기 반환"""
        return {
            '수평레이어스택': LayoutPreview.horizontal_stack(),
            '좌우분할': LayoutPreview.left_right_split(),
            '중앙허브형': LayoutPreview.central_hub(),
            '좌우파이프라인': LayoutPreview.pipeline()
        }

    @staticmethod
    def horizontal_stack() -> str:
        """수평 레이어 스택 미리보기"""
        return '''
        <svg width="200" height="150" viewBox="0 0 200 150" xmlns="http://www.w3.org/2000/svg">
            <rect x="2" y="2" width="196" height="146" fill="#fafafa" stroke="#e0e0e0" rx="4"/>
            
            <!-- Layer 1 -->
            <rect x="10" y="10" width="180" height="35" fill="#E3F2FD" stroke="#1976D2" rx="2"/>
            <text x="100" y="32" text-anchor="middle" font-size="10" fill="#333">Service Layer</text>
            
            <!-- Layer 2 -->
            <rect x="10" y="50" width="180" height="45" fill="#E8F5E9" stroke="#388E3C" rx="2"/>
            <text x="100" y="65" text-anchor="middle" font-size="10" fill="#333">Application Layer</text>
            <!-- Components in Layer 2 -->
            <rect x="20" y="72" width="50" height="18" fill="#fff" stroke="#666" rx="2"/>
            <rect x="75" y="72" width="50" height="18" fill="#fff" stroke="#666" rx="2"/>
            <rect x="130" y="72" width="50" height="18" fill="#fff" stroke="#666" rx="2"/>
            
            <!-- Layer 3 -->
            <rect x="10" y="100" width="180" height="40" fill="#FFE0B2" stroke="#F57C00" rx="2"/>
            <text x="100" y="115" text-anchor="middle" font-size="10" fill="#333">Data Layer</text>
            <rect x="40" y="122" width="55" height="14" fill="#fff" stroke="#666" rx="2"/>
            <rect x="105" y="122" width="55" height="14" fill="#fff" stroke="#666" rx="2"/>
        </svg>
        '''

    @staticmethod
    def left_right_split() -> str:
        """좌우 분할 미리보기"""
        return '''
        <svg width="200" height="150" viewBox="0 0 200 150" xmlns="http://www.w3.org/2000/svg">
            <rect x="2" y="2" width="196" height="146" fill="#fafafa" stroke="#e0e0e0" rx="4"/>
            
            <!-- Left Section -->
            <rect x="10" y="10" width="55" height="130" fill="#E3F2FD" stroke="#1976D2" rx="2"/>
            <text x="37" y="25" text-anchor="middle" font-size="8" fill="#333">Source</text>
            <rect x="15" y="35" width="45" height="25" fill="#fff" stroke="#666" rx="2"/>
            <rect x="15" y="65" width="45" height="25" fill="#fff" stroke="#666" rx="2"/>
            <rect x="15" y="95" width="45" height="25" fill="#fff" stroke="#666" rx="2"/>
            
            <!-- Center Section -->
            <rect x="72" y="10" width="55" height="130" fill="#E8F5E9" stroke="#388E3C" rx="2"/>
            <text x="100" y="25" text-anchor="middle" font-size="8" fill="#333">Process</text>
            <rect x="77" y="50" width="45" height="30" fill="#fff" stroke="#666" rx="2"/>
            <rect x="77" y="90" width="45" height="30" fill="#fff" stroke="#666" rx="2"/>
            
            <!-- Right Section -->
            <rect x="135" y="10" width="55" height="130" fill="#FFE0B2" stroke="#F57C00" rx="2"/>
            <text x="162" y="25" text-anchor="middle" font-size="8" fill="#333">Target</text>
            <rect x="140" y="55" width="45" height="40" fill="#fff" stroke="#666" rx="2"/>
            
            <!-- Arrows -->
            <path d="M62 75 L72 75" stroke="#666" stroke-width="2" marker-end="url(#arrow)"/>
            <path d="M124 75 L135 75" stroke="#666" stroke-width="2" marker-end="url(#arrow)"/>
            
            <defs>
                <marker id="arrow" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto">
                    <polygon points="0 0, 6 3, 0 6" fill="#666"/>
                </marker>
            </defs>
        </svg>
        '''

    @staticmethod
    def central_hub() -> str:
        """중앙 허브형 미리보기"""
        return '''
        <svg width="200" height="150" viewBox="0 0 200 150" xmlns="http://www.w3.org/2000/svg">
            <rect x="2" y="2" width="196" height="146" fill="#fafafa" stroke="#e0e0e0" rx="4"/>
            
            <!-- Center Hub -->
            <rect x="70" y="50" width="60" height="50" fill="#E8F5E9" stroke="#388E3C" stroke-width="2" rx="4"/>
            <text x="100" y="80" text-anchor="middle" font-size="10" font-weight="bold" fill="#333">Hub</text>
            
            <!-- Surrounding Components -->
            <rect x="75" y="10" width="50" height="25" fill="#E3F2FD" stroke="#1976D2" rx="2"/>
            <rect x="10" y="35" width="45" height="25" fill="#E3F2FD" stroke="#1976D2" rx="2"/>
            <rect x="145" y="35" width="45" height="25" fill="#E3F2FD" stroke="#1976D2" rx="2"/>
            <rect x="10" y="90" width="45" height="25" fill="#FFE0B2" stroke="#F57C00" rx="2"/>
            <rect x="145" y="90" width="45" height="25" fill="#FFE0B2" stroke="#F57C00" rx="2"/>
            <rect x="75" y="115" width="50" height="25" fill="#FFE0B2" stroke="#F57C00" rx="2"/>
            
            <!-- Connection Lines -->
            <line x1="100" y1="35" x2="100" y2="50" stroke="#999" stroke-width="1.5"/>
            <line x1="55" y1="47" x2="70" y2="65" stroke="#999" stroke-width="1.5"/>
            <line x1="145" y1="47" x2="130" y2="65" stroke="#999" stroke-width="1.5"/>
            <line x1="55" y1="102" x2="70" y2="85" stroke="#999" stroke-width="1.5"/>
            <line x1="145" y1="102" x2="130" y2="85" stroke="#999" stroke-width="1.5"/>
            <line x1="100" y1="100" x2="100" y2="115" stroke="#999" stroke-width="1.5"/>
        </svg>
        '''

    @staticmethod
    def pipeline() -> str:
        """좌우 파이프라인 미리보기"""
        return '''
        <svg width="200" height="150" viewBox="0 0 200 150" xmlns="http://www.w3.org/2000/svg">
            <rect x="2" y="2" width="196" height="146" fill="#fafafa" stroke="#e0e0e0" rx="4"/>
            
            <!-- Stage 1 -->
            <rect x="10" y="30" width="35" height="90" fill="#E3F2FD" stroke="#1976D2" rx="2"/>
            <text x="27" y="50" text-anchor="middle" font-size="8" fill="#333">수집</text>
            <rect x="14" y="58" width="27" height="20" fill="#fff" stroke="#666" rx="2"/>
            <rect x="14" y="82" width="27" height="20" fill="#fff" stroke="#666" rx="2"/>
            
            <!-- Stage 2 -->
            <rect x="55" y="30" width="35" height="90" fill="#E8F5E9" stroke="#388E3C" rx="2"/>
            <text x="72" y="50" text-anchor="middle" font-size="8" fill="#333">처리</text>
            <rect x="59" y="65" width="27" height="30" fill="#fff" stroke="#666" rx="2"/>
            
            <!-- Stage 3 -->
            <rect x="100" y="30" width="35" height="90" fill="#FFF9C4" stroke="#FBC02D" rx="2"/>
            <text x="117" y="50" text-anchor="middle" font-size="8" fill="#333">분석</text>
            <rect x="104" y="58" width="27" height="20" fill="#fff" stroke="#666" rx="2"/>
            <rect x="104" y="82" width="27" height="20" fill="#fff" stroke="#666" rx="2"/>
            
            <!-- Stage 4 -->
            <rect x="145" y="30" width="45" height="90" fill="#FFE0B2" stroke="#F57C00" rx="2"/>
            <text x="167" y="50" text-anchor="middle" font-size="8" fill="#333">저장</text>
            <rect x="152" y="65" width="32" height="35" fill="#fff" stroke="#666" rx="2"/>
            
            <!-- Arrows -->
            <path d="M45 75 L55 75" stroke="#666" stroke-width="2" marker-end="url(#arrow2)"/>
            <path d="M90 75 L100 75" stroke="#666" stroke-width="2" marker-end="url(#arrow2)"/>
            <path d="M135 75 L145 75" stroke="#666" stroke-width="2" marker-end="url(#arrow2)"/>
            
            <defs>
                <marker id="arrow2" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto">
                    <polygon points="0 0, 6 3, 0 6" fill="#666"/>
                </marker>
            </defs>
        </svg>
        '''


class ComponentPreview:
    """컴포넌트 타입 미리보기 SVG 생성"""

    @staticmethod
    def get_all_previews() -> Dict[str, str]:
        """모든 컴포넌트 타입 미리보기 반환"""
        return {
            '단일박스': ComponentPreview.single_box(),
            '클러스터': ComponentPreview.cluster(),
            '서비스': ComponentPreview.service(),
            '데이터베이스': ComponentPreview.database(),
            '저장소': ComponentPreview.storage(),
            '문서': ComponentPreview.document()
        }

    @staticmethod
    def single_box() -> str:
        """단일 박스 미리보기"""
        return '''
        <svg width="120" height="80" viewBox="0 0 120 80" xmlns="http://www.w3.org/2000/svg">
            <rect x="2" y="2" width="116" height="76" fill="#fafafa" stroke="#e0e0e0" rx="4"/>
            <rect x="20" y="15" width="80" height="50" fill="#FFFFFF" stroke="#666666" stroke-width="1.5" rx="2"/>
            <text x="60" y="45" text-anchor="middle" font-size="11" fill="#333">컴포넌트</text>
        </svg>
        '''

    @staticmethod
    def cluster() -> str:
        """클러스터 미리보기"""
        return '''
        <svg width="120" height="80" viewBox="0 0 120 80" xmlns="http://www.w3.org/2000/svg">
            <rect x="2" y="2" width="116" height="76" fill="#fafafa" stroke="#e0e0e0" rx="4"/>
            <rect x="10" y="10" width="100" height="60" fill="#F5F5F5" stroke="#666666" 
                  stroke-width="1.5" stroke-dasharray="5,3" rx="3"/>
            <text x="60" y="22" text-anchor="middle" font-size="9" font-weight="bold" fill="#333">클러스터</text>
            <rect x="18" y="30" width="35" height="20" fill="#fff" stroke="#999" rx="2"/>
            <rect x="58" y="30" width="35" height="20" fill="#fff" stroke="#999" rx="2"/>
            <rect x="38" y="52" width="35" height="15" fill="#fff" stroke="#999" rx="2"/>
        </svg>
        '''

    @staticmethod
    def service() -> str:
        """서비스 미리보기"""
        return '''
        <svg width="120" height="80" viewBox="0 0 120 80" xmlns="http://www.w3.org/2000/svg">
            <rect x="2" y="2" width="116" height="76" fill="#fafafa" stroke="#e0e0e0" rx="4"/>
            <rect x="20" y="15" width="80" height="50" fill="#FFFFFF" stroke="#666666" stroke-width="1.5" rx="12"/>
            <text x="60" y="45" text-anchor="middle" font-size="11" fill="#333">서비스</text>
        </svg>
        '''

    @staticmethod
    def database() -> str:
        """데이터베이스 미리보기"""
        return '''
        <svg width="120" height="80" viewBox="0 0 120 80" xmlns="http://www.w3.org/2000/svg">
            <rect x="2" y="2" width="116" height="76" fill="#fafafa" stroke="#e0e0e0" rx="4"/>
            <!-- Cylinder shape -->
            <ellipse cx="60" cy="20" rx="35" ry="8" fill="#FFFFFF" stroke="#666666" stroke-width="1.5"/>
            <rect x="25" y="20" width="70" height="40" fill="#FFFFFF" stroke="none"/>
            <line x1="25" y1="20" x2="25" y2="60" stroke="#666666" stroke-width="1.5"/>
            <line x1="95" y1="20" x2="95" y2="60" stroke="#666666" stroke-width="1.5"/>
            <ellipse cx="60" cy="60" rx="35" ry="8" fill="#FFFFFF" stroke="#666666" stroke-width="1.5"/>
            <text x="60" y="45" text-anchor="middle" font-size="10" fill="#333">Database</text>
        </svg>
        '''

    @staticmethod
    def storage() -> str:
        """저장소 미리보기"""
        return '''
        <svg width="120" height="80" viewBox="0 0 120 80" xmlns="http://www.w3.org/2000/svg">
            <rect x="2" y="2" width="116" height="76" fill="#fafafa" stroke="#e0e0e0" rx="4"/>
            <!-- Folder shape -->
            <path d="M20 25 L20 65 L100 65 L100 25 L55 25 L50 15 L25 15 L20 25 Z" 
                  fill="#FFFFFF" stroke="#666666" stroke-width="1.5"/>
            <text x="60" y="48" text-anchor="middle" font-size="10" fill="#333">Storage</text>
        </svg>
        '''

    @staticmethod
    def document() -> str:
        """문서 미리보기"""
        return '''
        <svg width="120" height="80" viewBox="0 0 120 80" xmlns="http://www.w3.org/2000/svg">
            <rect x="2" y="2" width="116" height="76" fill="#fafafa" stroke="#e0e0e0" rx="4"/>
            <!-- Document shape with folded corner -->
            <path d="M30 10 L30 70 L90 70 L90 25 L75 10 Z" 
                  fill="#FFFFFF" stroke="#666666" stroke-width="1.5"/>
            <path d="M75 10 L75 25 L90 25" fill="none" stroke="#666666" stroke-width="1.5"/>
            <line x1="40" y1="35" x2="80" y2="35" stroke="#ccc" stroke-width="1"/>
            <line x1="40" y1="45" x2="80" y2="45" stroke="#ccc" stroke-width="1"/>
            <line x1="40" y1="55" x2="70" y2="55" stroke="#ccc" stroke-width="1"/>
        </svg>
        '''


class ColorPreview:
    """색상 미리보기 SVG 생성"""

    COLORS = {
        '하늘색': '#E3F2FD',
        '연두색': '#E8F5E9',
        '주황색': '#FFE0B2',
        '회색': '#E0E0E0',
        '연회색': '#F5F5F5',
        '흰색': '#FFFFFF',
        '노란색': '#FFF9C4',
        '분홍색': '#FCE4EC',
        '보라색': '#EDE7F6',
        '파란색': '#BBDEFB',
        '녹색': '#C8E6C9'
    }

    BORDER_COLORS = {
        '진한파랑': '#1976D2',
        '진한녹색': '#388E3C',
        '진한주황': '#F57C00',
        '진한회색': '#616161',
        '회색': '#999999',
        '진한빨강': '#D32F2F',
        '진한보라': '#7B1FA2',
        '검정': '#000000'
    }

    @staticmethod
    def get_color_swatch(color_name: str, is_border: bool = False) -> str:
        """색상 견본 SVG 생성"""
        colors = ColorPreview.BORDER_COLORS if is_border else ColorPreview.COLORS
        hex_color = colors.get(color_name, '#CCCCCC')

        return f'''
        <svg width="60" height="30" viewBox="0 0 60 30" xmlns="http://www.w3.org/2000/svg">
            <rect x="2" y="2" width="56" height="26" fill="{hex_color}" stroke="#999" rx="4"/>
        </svg>
        '''

    @staticmethod
    def get_all_color_swatches() -> Dict[str, str]:
        """모든 배경색 견본 반환"""
        return {name: ColorPreview.get_color_swatch(name) for name in ColorPreview.COLORS}

    @staticmethod
    def get_all_border_swatches() -> Dict[str, str]:
        """모든 테두리색 견본 반환"""
        return {name: ColorPreview.get_color_swatch(name, is_border=True) for name in ColorPreview.BORDER_COLORS}


def get_hover_preview_css() -> str:
    """hover 미리보기를 위한 CSS 스타일"""
    return '''
    <style>
    .preview-container {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
    }
    
    .preview-item {
        position: relative;
        cursor: pointer;
        transition: transform 0.2s;
    }
    
    .preview-item:hover {
        transform: scale(1.05);
    }
    
    .preview-item:hover .preview-tooltip {
        display: block;
    }
    
    .preview-tooltip {
        display: none;
        position: absolute;
        bottom: 100%;
        left: 50%;
        transform: translateX(-50%);
        background: white;
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 10px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 1000;
        white-space: nowrap;
    }
    
    .preview-tooltip::after {
        content: '';
        position: absolute;
        top: 100%;
        left: 50%;
        transform: translateX(-50%);
        border: 8px solid transparent;
        border-top-color: white;
    }
    
    .preview-button {
        padding: 8px 16px;
        border: 2px solid #e0e0e0;
        border-radius: 8px;
        background: white;
        cursor: pointer;
        transition: all 0.2s;
        font-size: 13px;
    }
    
    .preview-button:hover {
        border-color: #1976D2;
        background: #f5f5f5;
    }
    
    .preview-button.selected {
        border-color: #1976D2;
        background: #E3F2FD;
    }
    </style>
    '''


def generate_layout_selector_html(selected: str = '수평레이어스택') -> str:
    """레이아웃 선택기 HTML 생성 (hover 미리보기 포함)"""
    previews = LayoutPreview.get_all_previews()

    items_html = ''
    for name, svg in previews.items():
        selected_class = 'selected' if name == selected else ''
        items_html += f'''
        <div class="preview-item">
            <button class="preview-button {selected_class}" data-value="{name}">
                {name}
            </button>
            <div class="preview-tooltip">
                {svg}
                <div style="text-align: center; margin-top: 8px; font-weight: bold; color: #333;">
                    {name}
                </div>
            </div>
        </div>
        '''

    return f'''
    {get_hover_preview_css()}
    <div class="preview-container">
        {items_html}
    </div>
    '''


def generate_component_selector_html(selected: str = '단일박스') -> str:
    """컴포넌트 타입 선택기 HTML 생성 (hover 미리보기 포함)"""
    previews = ComponentPreview.get_all_previews()

    items_html = ''
    for name, svg in previews.items():
        selected_class = 'selected' if name == selected else ''
        items_html += f'''
        <div class="preview-item">
            <button class="preview-button {selected_class}" data-value="{name}">
                {name}
            </button>
            <div class="preview-tooltip">
                {svg}
            </div>
        </div>
        '''

    return f'''
    {get_hover_preview_css()}
    <div class="preview-container">
        {items_html}
    </div>
    '''