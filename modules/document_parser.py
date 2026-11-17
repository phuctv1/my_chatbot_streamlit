"""
Document and File Parser for Codex AI Chatbot.
Extracts text, structured summaries, and image data from PDF, DOCX, XLSX, CSV, code, and image files.
"""
import io
import os
import base64
from typing import Dict, Any, Optional

MAX_CHARS = 25000  # Prevent blowing up context limits while giving rich context


def parse_uploaded_file(uploaded_file) -> Dict[str, Any]:
    """
    Parse an uploaded Streamlit file and extract text/summary/image data.
    Returns:
        {
            "filename": str,
            "extension": str,
            "file_type": str,
            "size_kb": float,
            "text": str,
            "preview": str,
            "is_image": bool,
            "image_base64": Optional[str],
            "mime_type": Optional[str],
            "success": bool,
            "error": Optional[str]
        }
    """
    filename = uploaded_file.name
    file_bytes = uploaded_file.getvalue()
    size_kb = round(len(file_bytes) / 1024, 2)
    ext = os.path.splitext(filename)[1].lower()

    result = {
        "filename": filename,
        "extension": ext,
        "size_kb": size_kb,
        "text": "",
        "preview": "",
        "is_image": False,
        "image_base64": None,
        "mime_type": None,
        "success": False,
        "error": None
    }

    try:
        # 1. Images
        if ext in [".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp"]:
            result["is_image"] = True
            mime = "image/png" if ext == ".png" else "image/jpeg"
            if ext == ".webp":
                mime = "image/webp"
            elif ext == ".gif":
                mime = "image/gif"

            result["mime_type"] = mime
            result["image_base64"] = base64.b64encode(file_bytes).decode("utf-8")
            result["file_type"] = f"Image ({ext.upper()[1:]})"
            result["text"] = f"[Hình ảnh: {filename} ({size_kb} KB)]"
            result["preview"] = f"Hình ảnh đính kèm: {filename}"
            result["success"] = True
            return result

        # 2. Documents
        elif ext == ".pdf":
            result["text"] = _parse_pdf(file_bytes)
            result["file_type"] = "PDF Document"
        elif ext in [".docx", ".doc"]:
            result["text"] = _parse_docx(file_bytes)
            result["file_type"] = "Word Document"
        elif ext in [".xlsx", ".xls"]:
            result["text"] = _parse_excel(file_bytes)
            result["file_type"] = "Excel Spreadsheet"
        elif ext == ".csv":
            result["text"] = _parse_csv(file_bytes)
            result["file_type"] = "CSV Data"
        elif ext in [".txt", ".md", ".py", ".json", ".js", ".ts", ".html", ".css", ".yaml", ".yml", ".sql", ".sh", ".bat", ".env"]:
            result["text"] = _parse_text(file_bytes)
            result["file_type"] = "Code / Text File"
        else:
            result["text"] = _parse_text(file_bytes)
            result["file_type"] = "Generic File"

        # Check truncation
        raw_len = len(result["text"])
        if raw_len > MAX_CHARS:
            result["text"] = result["text"][:MAX_CHARS] + f"\n\n... [Đã rút gọn vì tệp vượt quá {MAX_CHARS} ký tự] ..."

        # Generate a short preview
        preview_sample = result["text"][:300].strip().replace("\n", " ")
        result["preview"] = (preview_sample + "...") if len(preview_sample) >= 300 else preview_sample
        result["success"] = True

    except Exception as e:
        result["error"] = str(e)
        result["text"] = f"[Không thể đọc tệp {filename}: {str(e)}]"

    return result


def _parse_pdf(file_bytes: bytes) -> str:
    import pypdfium2 as pdfium
    pdf = pdfium.PdfDocument(file_bytes)
    pages_text = []
    total_pages = len(pdf)

    for i in range(min(total_pages, 50)):  # Max 50 pages
        page = pdf[i]
        textpage = page.get_textpage()
        page_content = textpage.get_text_range()
        if page_content.strip():
            pages_text.append(f"--- [Trang {i+1}/{total_pages}] ---\n{page_content.strip()}")

    if not pages_text:
        return "[Tệp PDF không chứa lớp văn bản hoặc là file scan dạng ảnh]"
    return "\n\n".join(pages_text)


def _parse_docx(file_bytes: bytes) -> str:
    import docx
    doc = docx.Document(io.BytesIO(file_bytes))
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paragraphs) if paragraphs else "[Tệp DOCX trống]"


def _parse_excel(file_bytes: bytes) -> str:
    import pandas as pd
    excel_file = io.BytesIO(file_bytes)
    xls = pd.ExcelFile(excel_file)
    sheets_summary = []

    for sheet_name in xls.sheet_names[:5]:  # Up to 5 sheets
        df = pd.read_excel(excel_file, sheet_name=sheet_name)
        rows, cols = df.shape
        summary = [f"=== Trang tính (Sheet): '{sheet_name}' (Số dòng: {rows}, Số cột: {cols}) ==="]
        summary.append(f"Danh sách cột: {list(df.columns)}")
        summary.append("Mẫu 5 dòng đầu:")
        summary.append(df.head(5).to_string(index=False))
        sheets_summary.append("\n".join(summary))

    return "\n\n".join(sheets_summary)


def _parse_csv(file_bytes: bytes) -> str:
    import pandas as pd
    try:
        df = pd.read_csv(io.BytesIO(file_bytes))
    except Exception:
        df = pd.read_csv(io.BytesIO(file_bytes), encoding="latin-1")

    rows, cols = df.shape
    summary = [f"=== CSV File (Số dòng: {rows}, Số cột: {cols}) ==="]
    summary.append(f"Danh sách cột: {list(df.columns)}")
    summary.append("Mẫu 5 dòng đầu:")
    summary.append(df.head(5).to_string(index=False))
    return "\n".join(summary)


def _parse_text(file_bytes: bytes) -> str:
    try:
        return file_bytes.decode("utf-8")
    except UnicodeDecodeError:
        return file_bytes.decode("latin-1", errors="replace")


def format_file_context_for_prompt(file_info: Dict[str, Any]) -> str:
    """Format parsed file data to be injected into LLM context."""
    if file_info.get("is_image"):
        return f"\n\n📎 **[Hình ảnh đính kèm: `{file_info['filename']}` ({file_info.get('size_kb')} KB)]**"

    return (
        f"\n\n📎 **[Tệp đính kèm từ người dùng: `{file_info['filename']}` ({file_info.get('file_type', 'File')}, {file_info.get('size_kb', 0)} KB)]**\n"
        f"```\n"
        f"{file_info['text']}\n"
        f"```\n"
    )
