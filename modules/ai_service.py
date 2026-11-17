"""
AI Service layer wrapping OpenAI chat completions with performance metrics,
multimodal image support, reasoning thought extraction, and prompt enhancement.
"""
import time
import re
from typing import List, Dict, Any, Tuple, Optional
from openai import OpenAI


def create_client(base_url: str, api_key: str) -> OpenAI:
    """Create and return an OpenAI client instance."""
    return OpenAI(base_url=base_url.strip(), api_key=api_key.strip())


def test_api_connection(base_url: str, api_key: str, model: str) -> Tuple[bool, str, int]:
    """
    Test connection with the specified model and endpoint.
    Returns: (is_success, message_or_error, latency_ms)
    """
    start_t = time.time()
    try:
        client = create_client(base_url, api_key)
        resp = client.chat.completions.create(
            model=model.strip(),
            messages=[{"role": "user", "content": "ping"}],
            max_tokens=5,
            timeout=10.0,
        )
        latency = int((time.time() - start_t) * 1000)
        return True, f"Kết nối thành công tới model '{model}'!", latency
    except Exception as e:
        latency = int((time.time() - start_t) * 1000)
        return False, str(e), latency


def estimate_token_count(text: str) -> int:
    """Fast conservative heuristic for token count (~4 characters per token)."""
    if not text:
        return 0
    words = len(text.split())
    chars = len(text)
    return max(1, int((words * 1.3 + chars / 4) / 2))


def extract_thought_process(text: str) -> Tuple[Optional[str], str]:
    """
    Extract chain-of-thought <think>...</think> from response text.
    Returns: (thought_content or None, clean_answer_text)
    """
    if not text:
        return None, ""

    match = re.search(r"<think>(.*?)</think>", text, re.DOTALL)
    if match:
        thought = match.group(1).strip()
        clean = (text[:match.start()] + text[match.end():]).strip()
        return thought, clean
    return None, text


def prepare_messages_payload(
    conversation_history: List[Dict[str, Any]],
    system_prompt: str = "",
    user_memory: str = ""
) -> List[Dict[str, Any]]:
    """
    Format and build the message list payload for OpenAI API.
    Supports text, attached documents, and multimodal base64 images.
    """
    payload = []

    # Combine system prompt with user memory if present
    full_system = system_prompt.strip()
    if user_memory and user_memory.strip():
        full_system += f"\n\n[Thông tin người dùng & Sở thích cá nhân]:\n{user_memory.strip()}"

    if full_system:
        payload.append({"role": "system", "content": full_system})

    for msg in conversation_history:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        file_info = msg.get("file_info")

        # 1. If message has an image attached -> Use Multimodal payload
        if role == "user" and file_info and file_info.get("is_image") and file_info.get("image_base64"):
            mime = file_info.get("mime_type", "image/jpeg")
            b64_str = file_info.get("image_base64")
            image_url = f"data:{mime};base64,{b64_str}"

            user_text = content
            if msg.get("file_context"):
                user_text = f"{msg['file_context']}\n\n{content}"

            payload.append({
                "role": "user",
                "content": [
                    {"type": "text", "text": user_text or "Hãy phân tích hình ảnh này."},
                    {"type": "image_url", "image_url": {"url": image_url}}
                ]
            })

        # 2. Regular text message or text file context
        else:
            final_content = content
            if msg.get("file_context"):
                final_content = f"{msg['file_context']}\n\n{content}"
            payload.append({"role": role, "content": final_content})

    return payload


def enhance_user_prompt(
    raw_prompt: str,
    base_url: str,
    api_key: str,
    model: str = "gpt-4o-mini"
) -> str:
    """
    Use LLM to rewrite a rough user prompt into an optimized, high-impact prompt.
    """
    if not raw_prompt or len(raw_prompt.strip()) < 3:
        return raw_prompt

    meta_prompt = (
        "Bạn là một AI Prompt Engineer hàng đầu. "
        "Nhiệm vụ: Hãy viết lại câu hỏi / yêu cầu dưới đây của người dùng thành một Prompt chi tiết, "
        "rõ ràng, có cấu trúc logic, đặt đúng ngữ cảnh và yêu cầu định dạng đầu ra chuẩn mực. "
        "Chỉ trả về nội dung Prompt đã tối ưu bằng tiếng Việt, không giải thích dài dòng.\n\n"
        f"Yêu cầu ban đầu: \"{raw_prompt}\""
    )

    try:
        client = create_client(base_url, api_key)
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": meta_prompt}],
            temperature=0.7,
            max_tokens=500,
            timeout=8.0
        )
        enhanced = resp.choices[0].message.content
        return enhanced.strip() if enhanced else raw_prompt
    except Exception:
        # Fallback if call fails
        return raw_prompt
