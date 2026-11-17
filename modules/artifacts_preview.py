"""
Artifacts and Live Web Canvas Previewer for Codex AI Chatbot (Claude-style Artifacts).
Detects and renders HTML/CSS/JS web components and SVG graphics live in an interactive sandbox.
"""
import re
from typing import List, Dict, Any, Optional


def extract_artifacts(text: str) -> List[Dict[str, Any]]:
    """
    Extract HTML, SVG, and web components from markdown text.
    Returns list of {"type": "html"|"svg", "title": str, "code": str}
    """
    if not text:
        return []

    artifacts = []

    # 1. HTML code blocks
    html_pattern = r"```(?:html|htm)\n(.*?)```"
    html_matches = re.findall(html_pattern, text, re.DOTALL)
    for idx, code in enumerate(html_matches):
        if code.strip():
            artifacts.append({
                "type": "html",
                "title": f"Web Component / HTML #{idx+1}",
                "code": code.strip()
            })

    # 2. SVG code blocks
    svg_pattern = r"```(?:svg|xml)\n(<svg.*?</svg>)```"
    svg_matches = re.findall(svg_pattern, text, re.DOTALL | re.IGNORECASE)
    for idx, code in enumerate(svg_matches):
        if code.strip():
            artifacts.append({
                "type": "svg",
                "title": f"Vector Graphic / SVG #{idx+1}",
                "code": code.strip()
            })

    # 3. Bare SVG tags if not in code block
    if not artifacts:
        bare_svgs = re.findall(r"(<svg[\s\S]*?</svg>)", text, re.IGNORECASE)
        for idx, code in enumerate(bare_svgs):
            artifacts.append({
                "type": "svg",
                "title": f"Vector Graphic / SVG #{idx+1}",
                "code": code.strip()
            })

    return artifacts
