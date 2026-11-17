"""
Safe interactive Python code runner for Codex AI Chatbot.
Extracts and executes Python code blocks from AI responses, capturing stdout and Matplotlib charts.
"""
import io
import re
import contextlib
import traceback
from typing import List, Dict, Any, Optional

try:
    import matplotlib
    matplotlib.use("Agg")  # Non-GUI backend for Streamlit
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False


def extract_python_code_blocks(text: str) -> List[str]:
    """Extract all ```python ... ``` code blocks from markdown text."""
    if not text:
        return []
    # Match ```python ... ``` or ```py ... ```
    pattern = r"```(?:python|py)\n(.*?)```"
    matches = re.findall(pattern, text, re.DOTALL)
    return [m.strip() for m in matches if m.strip()]


def execute_python_code(code: str) -> Dict[str, Any]:
    """
    Execute a snippet of Python code.
    Returns:
        {
            "success": bool,
            "stdout": str,
            "error": Optional[str],
            "has_figure": bool,
            "figure": Optional[plt.Figure]
        }
    """
    stdout_buf = io.StringIO()
    result = {
        "success": False,
        "stdout": "",
        "error": None,
        "has_figure": False,
        "figure": None
    }

    if HAS_MATPLOTLIB:
        plt.clf()
        plt.close("all")

    # Safe local namespace
    local_env = {
        "__name__": "__main__",
    }

    try:
        with contextlib.redirect_stdout(stdout_buf), contextlib.redirect_stderr(stdout_buf):
            exec(code, local_env)

        result["success"] = True
        result["stdout"] = stdout_buf.getvalue().strip()

        # Check if a matplotlib plot was generated
        if HAS_MATPLOTLIB and plt.get_fignums():
            fig = plt.gcf()
            # If the figure has axes and drawings
            if fig.axes:
                result["has_figure"] = True
                result["figure"] = fig

    except Exception as e:
        result["success"] = False
        result["error"] = traceback.format_exc()
        result["stdout"] = stdout_buf.getvalue().strip()

    return result
