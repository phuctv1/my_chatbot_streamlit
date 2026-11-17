"""
Model Arena Engine (Dual-Model Parallel Inference & Side-by-Side Comparison).
Runs two models concurrently on the same prompt to compare answers, latency, and tokens.
"""
import time
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any, Tuple
from modules.ai_service import create_client, estimate_token_count


def run_single_model_inference(
    model: str,
    base_url: str,
    api_key: str,
    messages: List[Dict[str, Any]],
    temperature: float = 0.7,
    max_tokens: int = 2048
) -> Dict[str, Any]:
    """Execute a single model completion and record performance metrics."""
    result = {
        "model": model,
        "content": "",
        "latency_ms": 0,
        "tokens": 0,
        "speed": 0.0,
        "success": False,
        "error": None
    }

    t_start = time.time()
    try:
        client = create_client(base_url, api_key)
        resp = client.chat.completions.create(
            model=model.strip(),
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=40.0
        )
        elapsed = max(0.01, time.time() - t_start)
        content = resp.choices[0].message.content or ""
        tokens = estimate_token_count(content)

        result["content"] = content
        result["latency_ms"] = int(elapsed * 1000)
        result["tokens"] = tokens
        result["speed"] = round(tokens / elapsed, 1)
        result["success"] = True

    except Exception as e:
        elapsed = max(0.01, time.time() - t_start)
        result["latency_ms"] = int(elapsed * 1000)
        result["error"] = str(e)

    return result


def run_parallel_arena_inference(
    model_a: str,
    model_b: str,
    base_url: str,
    api_key: str,
    messages: List[Dict[str, Any]],
    temperature: float = 0.7,
    max_tokens: int = 2048
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Run Model A and Model B in parallel threads on the exact same payload.
    Returns: (result_a, result_b)
    """
    with ThreadPoolExecutor(max_workers=2) as executor:
        future_a = executor.submit(
            run_single_model_inference,
            model_a, base_url, api_key, messages, temperature, max_tokens
        )
        future_b = executor.submit(
            run_single_model_inference,
            model_b, base_url, api_key, messages, temperature, max_tokens
        )

        result_a = future_a.result()
        result_b = future_b.result()

    return result_a, result_b
