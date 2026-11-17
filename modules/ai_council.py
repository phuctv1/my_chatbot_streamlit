"""
AI Council & Multi-Model Consensus Engine for Codex AI Chatbot.
Orchestrates 3 distinct AI models in parallel to analyze complex problems,
cross-verify arguments, and synthesize a unified, robust consensus recommendation.
"""
import time
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any, Tuple
from modules.ai_service import create_client, estimate_token_count
from modules.arena_mode import run_single_model_inference


def run_ai_council(
    user_prompt: str,
    base_url: str,
    api_key: str,
    council_models: List[str] = None,
    synthesizer_model: str = "claude-opus-5-5"
) -> Dict[str, Any]:
    """
    Run 3 AI models concurrently on the same prompt, then synthesize their findings.
    Returns:
        {
            "council_results": List[Dict[str, Any]],
            "synthesis": str,
            "total_latency_ms": int,
            "success": bool
        }
    """
    if not council_models or len(council_models) < 2:
        council_models = ["claude-opus-5-5", "gpt-6.1-sol", "gpt-4o"]

    models_to_run = council_models[:3]
    t_start = time.time()

    # Phase 1: Parallel Deliberation of Council Members
    messages = [{"role": "user", "content": user_prompt}]
    council_results = []

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [
            executor.submit(
                run_single_model_inference,
                m, base_url, api_key, messages, temperature=0.5, max_tokens=2048
            )
            for m in models_to_run
        ]
        for f in futures:
            council_results.append(f.result())

    # Phase 2: Synthesis of Council Perspectives
    synthesis_prompt = [
        {"role": "system", "content": (
            "Bạn là Chủ tịch Hội đồng AI cấp cao (AI Council Chair). "
            "Dưới đây là ý kiến độc lập từ các mô hình AI thành viên về cùng một vấn đề của người dùng. "
            "Nhiệm vụ: Hãy phân tích, đối chiếu và tổng hợp thành một báo cáo đúc kết chất lượng cao bằng tiếng Việt theo cấu trúc sau:\n"
            "1. 🎯 ĐIỂM ĐỒNG THUẬN CAO NHẤT (Các nguyên lý, giải pháp mà cả hội đồng đều nhất trí)\n"
            "2. ⚖️ ĐIỂM KHÁC BIỆT & GÓC NHÌN BỔ TRỢ (Các so sánh, đánh đổi, rủi ro mà từng thành viên cảnh báo)\n"
            "3. 🏆 PHƯƠNG ÁN HÀNH ĐỘNG TỐI ƯU NHẤT (Kết luận chỉ đạo hành động cụ thể, chi tiết, kèm code/hướng dẫn nếu có)"
        )},
        {"role": "user", "content": (
            f"VẤN ĐỀ CỦA NGƯỜI DÙNG: \"{user_prompt}\"\n\n"
            f"--- [Ý KIẾN THÀNH VIÊN 1: {council_results[0].get('model')}] ---\n{council_results[0].get('content')}\n\n"
            f"--- [Ý KIẾN THÀNH VIÊN 2: {council_results[1].get('model')}] ---\n{council_results[1].get('content')}\n\n"
            f"--- [Ý KIẾN THÀNH VIÊN 3: {council_results[2].get('model') if len(council_results) > 2 else 'N/A'}] ---\n{council_results[2].get('content') if len(council_results) > 2 else ''}\n\n"
            "Hãy tổng hợp và đưa ra báo cáo kết luận cuối cùng của Hội Đồng AI."
        )}
    ]

    synthesis_text = ""
    try:
        client = create_client(base_url, api_key)
        synth_resp = client.chat.completions.create(
            model=synthesizer_model,
            messages=synthesis_prompt,
            temperature=0.3,
            max_tokens=3000,
            timeout=40.0
        )
        synthesis_text = synth_resp.choices[0].message.content or ""
    except Exception as e:
        synthesis_text = f"[Lỗi khi tổng hợp ý kiến Hội Đồng: {str(e)}]"

    total_latency = int((time.time() - t_start) * 1000)

    return {
        "council_results": council_results,
        "synthesis": synthesis_text,
        "total_latency_ms": total_latency,
        "success": bool(synthesis_text and not synthesis_text.startswith("[Lỗi"))
    }
