"""
Code Diff & Version Comparison Tool for Codex AI Chatbot (Git-Style Diff Viewer).
Visualizes changes between original and refactored code with syntax-highlighted additions and deletions.
"""
import difflib
import html
from typing import List, Dict, Any, Tuple


def generate_diff_html(old_code: str, new_code: str) -> str:
    """Generate a clean GitHub-style HTML diff view with additions and deletions."""
    old_lines = old_code.splitlines()
    new_lines = new_code.splitlines()

    diff = difflib.unified_diff(old_lines, new_lines, fromfile="Bản Cũ (Before)", tofile="Bản Mới (After)", lineterm="")

    lines_html = []
    for line in diff:
        escaped = html.escape(line)
        if line.startswith("+") and not line.startswith("+++"):
            lines_html.append(f"<div style='background: rgba(16, 185, 129, 0.2); color: #34d399; padding: 2px 8px; border-left: 3px solid #10b981;'>{escaped}</div>")
        elif line.startswith("-") and not line.startswith("---"):
            lines_html.append(f"<div style='background: rgba(239, 68, 68, 0.2); color: #f87171; padding: 2px 8px; border-left: 3px solid #ef4444;'>{escaped}</div>")
        elif line.startswith("@@"):
            lines_html.append(f"<div style='color: #818cf8; font-weight: bold; padding: 4px 8px; background: rgba(99, 102, 241, 0.1);'>{escaped}</div>")
        else:
            lines_html.append(f"<div style='color: #94a3b8; padding: 2px 8px;'>{escaped}</div>")

    content = "".join(lines_html)
    return f"""
    <div style='background: #0f172a; border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; font-family: monospace; font-size: 0.84rem; overflow-x: auto; padding: 6px 0;'>
        {content}
    </div>
    """
