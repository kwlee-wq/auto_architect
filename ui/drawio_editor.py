"""
AutoArchitect - Draw.io 에디터 임베딩
HTML/CSS/JS 생성
"""

import urllib.parse


def get_drawio_editor_html(xml_content: str, height: int = 700) -> str:
    """Draw.io 임베딩 에디터 HTML 생성"""

    escaped_xml = ""
    if xml_content:
        escaped_xml = xml_content.replace('\\', '\\\\').replace('`', '\\`').replace('${', '\\${')

    params = {
        'embed': '1',
        'proto': 'json',
        'spin': '1',
        'modified': 'unsavedChanges',
        'keepmodified': '1',
        'libraries': '1',
        'noSaveBtn': '0',
        'noExitBtn': '1',
    }

    base_url = "https://embed.diagrams.net/"
    query_string = urllib.parse.urlencode(params)
    drawio_url = f"{base_url}?{query_string}"

    html = f'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }}
        
        .editor-wrapper {{
            width: 100%;
            height: {height}px;
            border: 2px solid #e0e0e0;
            border-radius: 12px;
            overflow: hidden;
            background: #fff;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            transition: border-color 0.2s, box-shadow 0.2s;
        }}
        
        .editor-wrapper:hover {{
            border-color: #3b82f6;
        }}
        
        .editor-wrapper:focus-within {{
            border-color: #2563eb;
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
        }}
        
        .toolbar {{
            display: flex;
            gap: 10px;
            padding: 12px 16px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            flex-wrap: wrap;
            align-items: center;
        }}
        
        .toolbar-title {{
            color: white;
            font-weight: 600;
            font-size: 14px;
            margin-right: auto;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .btn {{
            padding: 8px 16px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 13px;
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 6px;
            transition: all 0.2s ease;
        }}
        
        .btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }}
        
        .btn-svg {{ background: #10b981; color: white; }}
        .btn-svg:hover {{ background: #059669; }}
        
        .btn-png {{ background: #3b82f6; color: white; }}
        .btn-png:hover {{ background: #2563eb; }}
        
        .btn-xml {{ background: #6366f1; color: white; }}
        .btn-xml:hover {{ background: #4f46e5; }}
        
        .btn-fit {{ background: #f59e0b; color: white; }}
        .btn-fit:hover {{ background: #d97706; }}
        
        .btn-fullscreen {{ background: #8b5cf6; color: white; }}
        .btn-fullscreen:hover {{ background: #7c3aed; }}
        
        .editor-wrapper.fullscreen {{
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            width: 100vw !important;
            height: 100vh !important;
            z-index: 9999 !important;
            border-radius: 0 !important;
            border: none !important;
        }}
        
        .editor-wrapper.fullscreen .editor-frame {{
            height: calc(100vh - 56px) !important;
        }}
        
        .editor-wrapper.fullscreen .toolbar {{
            border-radius: 0;
        }}
        
        .fullscreen-hint {{
            display: none;
            color: rgba(255,255,255,0.7);
            font-size: 12px;
            margin-left: 10px;
        }}
        
        .editor-wrapper.fullscreen .fullscreen-hint {{
            display: inline;
        }}
        
        .editor-frame {{
            width: 100%;
            height: calc(100% - 56px);
            border: none;
        }}
        
        .loading-overlay {{
            position: absolute;
            top: 56px;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(255,255,255,0.95);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            z-index: 100;
        }}
        
        .spinner {{
            width: 48px;
            height: 48px;
            border: 4px solid #e5e7eb;
            border-top: 4px solid #6366f1;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }}
        
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
        
        .loading-text {{
            margin-top: 16px;
            color: #6b7280;
            font-size: 14px;
        }}
        
        .status-bar {{
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            padding: 6px 16px;
            background: #f3f4f6;
            font-size: 12px;
            color: #6b7280;
            display: flex;
            justify-content: space-between;
            border-top: 1px solid #e5e7eb;
        }}
        
        .status-dot {{
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #10b981;
            display: inline-block;
            margin-right: 6px;
        }}
        
        .status-dot.loading {{
            background: #f59e0b;
            animation: pulse 1s infinite;
        }}
        
        @keyframes pulse {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.5; }}
        }}
        
        .hidden {{ display: none !important; }}
    </style>
</head>
<body>
    <div class="editor-wrapper" style="position: relative;">
        <div class="toolbar">
            <div class="toolbar-title">
                ✏️ Draw.io 에디터
                <span class="fullscreen-hint">(ESC로 종료)</span>
            </div>
            <button class="btn btn-svg" onclick="exportSVG()" title="SVG 파일로 저장">
                📷 SVG
            </button>
            <button class="btn btn-png" onclick="exportPNG()" title="PNG 이미지로 저장">
                🖼️ PNG
            </button>
            <button class="btn btn-xml" onclick="exportXML()" title="Draw.io 파일로 저장">
                💾 XML
            </button>
            <button class="btn btn-fit" onclick="fitToPage()" title="화면에 맞추기">
                🔍 화면 맞춤
            </button>
            <button class="btn btn-fullscreen" onclick="toggleFullscreen()" id="fullscreen-btn" title="전체화면 전환">
                ⛶ 전체화면
            </button>
        </div>
        
        <iframe id="drawio-frame" class="editor-frame" src="{drawio_url}"></iframe>
        
        <div class="loading-overlay" id="loading-overlay">
            <div class="spinner"></div>
            <div class="loading-text">Draw.io 에디터를 불러오는 중...</div>
        </div>
        
        <div class="status-bar">
            <span>
                <span class="status-dot loading" id="status-dot"></span>
                <span id="status-text">연결 중...</span>
            </span>
            <span id="last-saved">-</span>
        </div>
    </div>

    <script>
        let iframe = null;
        let isReady = false;
        let currentXml = null;
        const initialXml = `{escaped_xml}`;
        
        document.addEventListener('DOMContentLoaded', function() {{
            iframe = document.getElementById('drawio-frame');
            window.addEventListener('message', handleMessage);
            
            // 자동 포커스 기능
            const editorWrapper = document.querySelector('.editor-wrapper');
            
            // 마우스가 에디터 영역에 들어오면 자동 포커스
            editorWrapper.addEventListener('mouseenter', function() {{
                if (iframe && isReady) {{
                    iframe.focus();
                }}
            }});
            
            // 클릭해도 포커스
            editorWrapper.addEventListener('click', function(e) {{
                // 버튼 클릭이 아닌 경우에만
                if (!e.target.closest('.btn') && iframe) {{
                    iframe.focus();
                }}
            }});
            
            // iframe 로드 완료 후에도 포커스
            iframe.addEventListener('load', function() {{
                setTimeout(function() {{
                    iframe.focus();
                }}, 500);
            }});
        }});
        
        function handleMessage(event) {{
            if (event.origin !== 'https://embed.diagrams.net') return;
            
            let data;
            try {{
                data = JSON.parse(event.data);
            }} catch (e) {{ return; }}
            
            console.log('Draw.io:', data.event);
            
            switch (data.event) {{
                case 'init':
                    handleInit();
                    break;
                case 'load':
                    handleLoad();
                    break;
                case 'save':
                case 'autosave':
                    handleSave(data.xml);
                    break;
                case 'export':
                    handleExport(data);
                    break;
                case 'configure':
                    sendConfigure();
                    break;
            }}
        }}
        
        function handleInit() {{
            isReady = true;
            if (initialXml && initialXml.trim()) {{
                loadDiagram(initialXml);
            }} else {{
                sendAction({{
                    action: 'load',
                    xml: '<mxfile><diagram name="Page-1"><mxGraphModel><root><mxCell id="0"/><mxCell id="1" parent="0"/></root></mxGraphModel></diagram></mxfile>',
                    autosave: 1
                }});
            }}
        }}
        
        function handleLoad() {{
            hideLoading();
            updateStatus('ready', '준비됨');
            // 로드 완료 후 자동 포커스
            setTimeout(function() {{
                if (iframe) iframe.focus();
            }}, 300);
        }}
        
        function handleSave(xml) {{
            currentXml = xml;
            updateLastSaved();
        }}
        
        function handleExport(data) {{
            if (data.format === 'svg' || data.format === 'xmlsvg') {{
                if (data.data && data.data.startsWith('data:')) {{
                    downloadBase64(data.data, 'diagram.svg');
                }} else {{
                    downloadFile(data.data, 'diagram.svg', 'image/svg+xml');
                }}
            }} else if (data.format === 'png') {{
                downloadBase64(data.data, 'diagram.png');
            }}
            updateStatus('ready', '다운로드 완료!');
        }}
        
        function loadDiagram(xml) {{
            sendAction({{ action: 'load', xml: xml, autosave: 1 }});
        }}
        
        function sendAction(msg) {{
            if (iframe && iframe.contentWindow) {{
                iframe.contentWindow.postMessage(JSON.stringify(msg), '*');
            }}
        }}
        
        function sendConfigure() {{
            sendAction({{
                action: 'configure',
                config: {{ defaultFonts: ['Arial', 'Helvetica', 'Pretendard'] }}
            }});
        }}
        
        function exportSVG() {{
            updateStatus('loading', '내보내는 중...');
            sendAction({{ action: 'export', format: 'svg', spin: 'Exporting' }});
        }}
        
        function exportPNG() {{
            updateStatus('loading', '내보내는 중...');
            sendAction({{ action: 'export', format: 'png', scale: 2, spin: 'Exporting' }});
        }}
        
        function exportXML() {{
            if (currentXml) {{
                downloadFile(currentXml, 'diagram.drawio', 'application/xml');
                updateStatus('ready', '다운로드 완료!');
            }} else {{
                alert('먼저 다이어그램을 편집하세요.');
            }}
        }}
        
        function fitToPage() {{
            sendAction({{ action: 'layout', layouts: [{{ type: 'fit' }}] }});
        }}
        
        function toggleFullscreen() {{
            const wrapper = document.querySelector('.editor-wrapper');
            const btn = document.getElementById('fullscreen-btn');
            
            if (!document.fullscreenElement) {{
                if (wrapper.requestFullscreen) {{
                    wrapper.requestFullscreen();
                }} else if (wrapper.webkitRequestFullscreen) {{
                    wrapper.webkitRequestFullscreen();
                }} else if (wrapper.msRequestFullscreen) {{
                    wrapper.msRequestFullscreen();
                }} else {{
                    wrapper.classList.add('fullscreen');
                    btn.innerHTML = '✕ 종료';
                }}
            }} else {{
                if (document.exitFullscreen) {{
                    document.exitFullscreen();
                }} else if (document.webkitExitFullscreen) {{
                    document.webkitExitFullscreen();
                }} else if (document.msExitFullscreen) {{
                    document.msExitFullscreen();
                }}
            }}
        }}
        
        document.addEventListener('fullscreenchange', handleFullscreenChange);
        document.addEventListener('webkitfullscreenchange', handleFullscreenChange);
        document.addEventListener('msfullscreenchange', handleFullscreenChange);
        
        function handleFullscreenChange() {{
            const wrapper = document.querySelector('.editor-wrapper');
            const btn = document.getElementById('fullscreen-btn');
            
            if (document.fullscreenElement) {{
                wrapper.classList.add('fullscreen');
                btn.innerHTML = '✕ 종료';
            }} else {{
                wrapper.classList.remove('fullscreen');
                btn.innerHTML = '⛶ 전체화면';
            }}
        }}
        
        document.addEventListener('keydown', function(e) {{
            if (e.key === 'Escape') {{
                const wrapper = document.querySelector('.editor-wrapper');
                if (wrapper.classList.contains('fullscreen') && !document.fullscreenElement) {{
                    wrapper.classList.remove('fullscreen');
                    document.getElementById('fullscreen-btn').innerHTML = '⛶ 전체화면';
                }}
            }}
        }});
        
        function downloadFile(content, filename, mimeType) {{
            const blob = new Blob([content], {{ type: mimeType }});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }}
        
        function downloadBase64(dataUrl, filename) {{
            const a = document.createElement('a');
            a.href = dataUrl;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
        }}
        
        function hideLoading() {{
            document.getElementById('loading-overlay').classList.add('hidden');
        }}
        
        function updateStatus(state, text) {{
            const dot = document.getElementById('status-dot');
            const statusText = document.getElementById('status-text');
            dot.className = 'status-dot' + (state === 'loading' ? ' loading' : '');
            statusText.textContent = text;
        }}
        
        function updateLastSaved() {{
            document.getElementById('last-saved').textContent = 
                '저장: ' + new Date().toLocaleTimeString();
        }}
    </script>
</body>
</html>
'''
    return html