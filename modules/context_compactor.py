"""
Context Compactor & Smart Token Optimizer for Codex AI Chatbot.
Compresses long chat history into an executive summary to save 60-80% token costs.
"""
from typing import List, Dict, Any, Tuple
from modules.ai_service import create_client, estimate_token_count


def compact_conversation_history(
    messages: List[Dict[str, Any]],
    base_url: str,
    api_key: str,
    model: str = "gpt-4o-mini",
    keep_last_turns: int = 4
) -> Tuple[List[Dict[str, Any]], int, int]:
    """
    Condense earlier conversation turns into a summarized memory block.
    Returns: (new_compacted_messages, old_token_count, new_token_count)
    """
    if len(messages) <= keep_last_turns:
        toks = estimate_token_count(" ".join(m.get("content", "") for m in messages))
        return messages, toks, toks

    old_text = " ".join(m.get("content", "") for m in messages)
    old_tokens = estimate_token_count(old_text)

    # Split into older turns and recent turns
    older_messages = messages[:-keep_last_turns]
    recent_messages = messages[-keep_last_turns:]

    # Build text to summarize
    text_to_summarize = []
    for m in older_messages:
        role_label = "Người dùng" if m.get("role") == "user" else "AI"
        text_to_summarize.append(f"{role_label}: {m.get('content', '')}")

    raw_dialogue = "\n".join(text_to_summarize)

    prompt = (
        "Nhiệm vụ: Hãy tóm tắt lại toàn bộ diễn biến, thông tin chính, yêu cầu cốt lõi "
        "và các quyết định quan trọng của đoạn hội thoại trước đó dưới dạng 1 đoạn văn súc tích "
        "hoặc các gạch đầu dòng ngắn gọn (dưới 150 từ) bằng tiếng Việt. "
        "Đảm bảo giữ lại các chi tiết quan trọng nhất để AI tiếp tục cuộc trò chuyện mà không bị mất ngữ cảnh.\n\n"
        f"Đoạn hội thoại:\n{raw_dialogue}"
    )

    summary_text = ""
    try:
        client = create_client(base_url, api_key)
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400,
            temperature=0.3,
            timeout=10.0
        )
        summary_text = resp.choices[0].message.content.strip()
    except Exception:
        # Fallback if summarization fails
        summary_text = "Tóm tắt ngữ cảnh trước đó: Người dùng và AI đã thảo luận về các vấn đề kỹ thuật và yêu cầu trên."

    compacted_history = [
        {
            "role": "system",
            "content": f"[🧠 TÓM TẮT NGỮ CẢNH CÁC LƯỢT TRÒ CHUYỆN TRƯỚC ĐÓ]:\n{summary_text}",
            "is_compacted_summary": True
        }
    ]
    compacted_history.extend(recent_messages)

    new_text = " ".join(m.get("content", "") for m in compacted_history)
    new_tokens = estimate_token_count(new_text)

    return compacted_history, old_tokens, new_tokens
