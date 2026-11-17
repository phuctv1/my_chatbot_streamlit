"""
Mermaid & Flowchart Interactive Diagram Visualizer for Codex AI Chatbot.
Detects Mermaid code blocks and renders SVG vector diagrams in Streamlit via Mermaid.js CDN.
"""
import re
from typing import List, Dict, Any


def extract_mermaid_blocks(text: str) -> List[str]:
    """Extract all ```mermaid ... ``` code blocks from markdown text."""
    if not text:
        return []
    pattern = r"```mermaid\n(.*?)```"
    matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
    return [m.strip() for m in matches if m.strip()]


def generate_mermaid_html(mermaid_code: str, height: int = 420) -> str:
    """Generate HTML snippet to render Mermaid code using Mermaid.js CDN."""
    # Sanitize backticks in code
    clean_code = mermaid_code.replace("`", "'")

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{
                margin: 0;
                padding: 10px;
                background: rgba(15, 23, 42, 0.4);
                display: flex;
                justify-content: center;
                align-items: center;
                color: #e2e8f0;
                font-family: sans-serif;
            }}
            .mermaid {{
                display: flex;
                justify-content: center;
                width: 100%;
            }}
            svg {{
                max-width: 100% !important;
                height: auto !important;
            }}
        </style>
        <script type="module">
            import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
            mermaid.initialize({{
                startOnLoad: true,
                theme: 'dark',
                securityLevel: 'loose',
                themeVariables: {{
                    darkMode: true,
                    background: 'transparent',
                    primaryColor: '#6366f1',
                    primaryTextColor: '#ffffff',
                    primaryBorderColor: '#818cf8',
                    lineColor: '#38bdf8',
                    secondaryColor: '#10b981',
                    tertiaryColor: '#1e293b'
                }}
            }});
        </script>
    </head>
    <body>
        <div class="mermaid">
{clean_code}
        </div>
    </body>
    </html>
    """
    return html
