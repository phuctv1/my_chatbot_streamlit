"""
Live Web Search and URL Content Reader for Codex AI Chatbot.
Provides real-time web retrieval and link summarization without external API keys.
"""
import re
import urllib.request
import urllib.parse
from typing import List, Dict, Any, Optional

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"


def detect_urls(text: str) -> List[str]:
    """Extract http/https URLs from a string."""
    pattern = r"https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[^\s]*"
    return re.findall(pattern, text)


def fetch_url_content(url: str, max_chars: int = 12000) -> Dict[str, Any]:
    """
    Fetch and clean text content from a public web page URL.
    Returns:
        {"url": str, "title": str, "text": str, "success": bool, "error": Optional[str]}
    """
    result = {
        "url": url,
        "title": "",
        "text": "",
        "success": False,
        "error": None
    }

    try:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=10) as resp:
            content_type = resp.headers.get("Content-Type", "").lower()
            charset = "utf-8"
            if "charset=" in content_type:
                charset = content_type.split("charset=")[-1].split(";")[0].strip()

            raw_html = resp.read().decode(charset, errors="replace")

        # Extract title
        title_match = re.search(r"<title[^>]*>(.*?)</title>", raw_html, re.IGNORECASE | re.DOTALL)
        result["title"] = title_match.group(1).strip() if title_match else url

        # Remove scripts, styles, navigations
        clean_html = re.sub(r"<(script|style|nav|footer|header|aside)[^>]*>.*?</\1>", " ", raw_html, flags=re.IGNORECASE | re.DOTALL)
        # Remove all other HTML tags
        clean_text = re.sub(r"<[^>]+>", " ", clean_html)
        # Unescape and normalize whitespaces
        clean_text = re.sub(r"\s+", " ", clean_text).strip()

        if len(clean_text) > max_chars:
            clean_text = clean_text[:max_chars] + f"\n... [Đã rút gọn vì trang vượt quá {max_chars} ký tự] ..."

        result["text"] = clean_text
        result["success"] = True

    except Exception as e:
        result["error"] = str(e)

    return result


def search_web(query: str, max_results: int = 4) -> List[Dict[str, str]]:
    """
    Search DuckDuckGo Lite / HTML and parse search result snippets.
    Returns list of {"title": str, "url": str, "snippet": str}
    """
    results = []
    try:
        encoded_q = urllib.parse.quote_plus(query)
        search_url = f"https://html.duckduckgo.com/html/?q={encoded_q}"
        req = urllib.request.Request(search_url, headers={"User-Agent": USER_AGENT})

        with urllib.request.urlopen(req, timeout=8) as resp:
            html = resp.read().decode("utf-8", errors="replace")

        # Extract result blocks
        pattern = r'<a class="result__url"[^>]*href="([^"]+)"[^>]*>(.*?)</a>.*?<a class="result__snippet"[^>]*>(.*?)</a>'
        matches = re.findall(pattern, html, re.DOTALL)

        for match in matches[:max_results]:
            raw_url, raw_title, raw_snippet = match
            clean_title = re.sub(r"<[^>]+>", "", raw_title).strip()
            clean_snippet = re.sub(r"<[^>]+>", "", raw_snippet).strip()

            # Clean DDG redirect URL if present
            actual_url = raw_url
            if "uddg=" in raw_url:
                actual_url = urllib.parse.unquote(raw_url.split("uddg=")[-1].split("&")[0])

            results.append({
                "title": clean_title,
                "url": actual_url,
                "snippet": clean_snippet
            })

    except Exception as e:
        # Graceful fallback if network is restricted or offline
        results.append({
            "title": "Lỗi tìm kiếm Web",
            "url": "",
            "snippet": f"Không thể kết nối tới máy chủ tìm kiếm: {str(e)}"
        })

    return results


def format_search_results_for_prompt(query: str, results: List[Dict[str, str]]) -> str:
    """Format search results to be injected into LLM context."""
    if not results or (len(results) == 1 and results[0].get("title") == "Lỗi tìm kiếm Web"):
        return ""

    lines = [f"\n🌐 **[Kết quả Tìm kiếm Web thời gian thực cho: '{query}']**"]
    for i, res in enumerate(results, 1):
        lines.append(f"{i}. **{res.get('title', 'Nguồn')}** ({res.get('url', '')}):\n   {res.get('snippet', '')}")
    lines.append("Hãy sử dụng thông tin tìm kiếm phía trên để trả lời câu hỏi của người dùng một cách chính xác và cập nhật nhất.\n")
    return "\n".join(lines)
