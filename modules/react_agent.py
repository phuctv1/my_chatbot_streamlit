"""
Autonomous ReAct (Reasoning + Acting) Agent Engine for Codex AI Chatbot.
Enables the model to autonomously plan, invoke local Python tools, search the web,
query the knowledge base, and arrive at verified solutions.
"""
import re
import time
from typing import Dict, Any, List, Tuple, Callable
from modules.ai_service import create_client
from modules.code_runner import execute_python_code
from modules.web_search import search_web, fetch_url_content
from modules.knowledge_base import query_kb

MAX_AGENT_STEPS = 4

REACT_SYSTEM_PROMPT = """Bạn là một Autonomous AI Agent thông minh và có năng lực hành động tự chủ.
Bạn có quyền truy cập vào các công cụ sau:

1. python_sandbox[mã_python]: Thực thi mã Python để tính toán phức tạp, xử lý dữ liệu, chuỗi hoặc logic toán học.
2. web_search[từ_khóa]: Tìm kiếm thông tin thực tế mới nhất trên Internet.
3. url_reader[đường_dẫn_url]: Đọc và trích xuất nội dung văn bản từ một liên kết trang web.
4. knowledge_search[từ_khóa]: Tra cứu thông tin từ Kho Tri Thức nội bộ của người dùng.
5. calculator[biểu_thức_toán]: Tính toán số học chính xác (ví dụ: calculator[sqrt(144) * 25 + 18]).

QUY TRÌNH HÀNH ĐỘNG BẮT BUỘC (ReAct Framework):
Khi người dùng đặt câu hỏi, hãy suy luận và sử dụng định dạng chính xác sau:

Thought: [Suy nghĩ của bạn về việc cần làm gì tiếp theo]
Action: tên_công_cụ[đối_số]

Sau khi bạn đưa ra Action, hệ thống sẽ trả về kết quả dưới dạng:
Observation: [Kết quả thực thi công cụ]

Bạn có thể lặp lại Thought -> Action -> Observation nếu cần thêm thông tin.
Khi đã có đầy đủ câu trả lời, hãy kết luận bằng:
Thought: Tôi đã có đủ thông tin để trả lời hoàn chỉnh.
Final Answer: [Câu trả lời chi tiết, chuẩn xác, đầy đủ cho người dùng bằng tiếng Việt]

LƯU Ý QUAN TRỌNG:
- Chỉ đưa ra MỘT Action duy nhất trong mỗi lượt phản hồi.
- Khi đã sẵn sàng kết luận, luôn bắt đầu bằng 'Final Answer:'.
"""


def _run_tool(tool_name: str, tool_arg: str) -> str:
    """Execute the specified tool with arguments and return observation string."""
    tool_name = tool_name.strip().lower()
    tool_arg = tool_arg.strip()

    try:
        if tool_name == "python_sandbox":
            res = execute_python_code(tool_arg)
            if res["success"]:
                out = res["stdout"] or "[Mã thực thi thành công nhưng không in gì ra stdout]"
                return out[:1500]
            else:
                return f"[Lỗi thực thi: {res.get('error', 'Lỗi')}][:500]"

        elif tool_name == "web_search":
            results = search_web(tool_arg, max_results=3)
            if not results:
                return "[Không tìm thấy kết quả phù hợp trên web]"
            lines = [f"- {r.get('title')}: {r.get('snippet')} ({r.get('url')})" for r in results]
            return "\n".join(lines)[:1500]

        elif tool_name == "url_reader":
            res = fetch_url_content(tool_arg, max_chars=3000)
            if res["success"]:
                return res["text"][:1500]
            else:
                return f"[Không đọc được link: {res.get('error', 'Lỗi')}]"

        elif tool_name == "knowledge_search":
            chunks = query_kb(tool_arg, top_k=2)
            if not chunks:
                return "[Không tìm thấy tài liệu phù hợp trong Kho Tri Thức]"
            lines = [f"- Từ `{c.get('source')}`: {c.get('text')}" for c in chunks]
            return "\n".join(lines)[:1500]

        elif tool_name == "calculator":
            # Safe arithmetic eval
            clean_expr = re.sub(r"[^0-9+\-*/().%\s]", "", tool_arg)
            val = eval(clean_expr, {"__builtins__": {}}, {})
            return f"Kết quả: {val}"

        else:
            return f"[Công cụ không hợp lệ: '{tool_name}']"

    except Exception as e:
        return f"[Lỗi khi chạy công cụ '{tool_name}': {str(e)}]"


def run_react_agent_loop(
    user_prompt: str,
    base_url: str,
    api_key: str,
    model: str = "claude-opus-5-5",
    step_callback: Callable[[Dict[str, Any]], None] = None
) -> Dict[str, Any]:
    """
    Run autonomous ReAct loop up to MAX_AGENT_STEPS.
    Returns:
        {
            "steps": List[Dict[str, Any]],
            "final_answer": str,
            "total_latency_ms": int,
            "success": bool
        }
    """
    client = create_client(base_url, api_key)
    conversation = [
        {"role": "system", "content": REACT_SYSTEM_PROMPT},
        {"role": "user", "content": f"Yêu cầu của người dùng: {user_prompt}"}
    ]

    steps_record = []
    t_start = time.time()
    final_answer = ""

    for step_num in range(1, MAX_AGENT_STEPS + 1):
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=conversation,
                temperature=0.2,
                max_tokens=1500,
                timeout=30.0
            )
            ai_msg = resp.choices[0].message.content or ""
            conversation.append({"role": "assistant", "content": ai_msg})

            # Check if agent produced Final Answer
            if "Final Answer:" in ai_msg:
                final_answer = ai_msg.split("Final Answer:")[-1].strip()
                # Record step if there was thought before final answer
                thought_part = ai_msg.split("Final Answer:")[0].replace("Thought:", "").strip()
                steps_record.append({
                    "step": step_num,
                    "thought": thought_part or "Hoàn tất suy luận và tổng hợp câu trả lời.",
                    "action": None,
                    "observation": None
                })
                break

            # Parse Action: tool_name[arg]
            action_match = re.search(r"Action:\s*([a-zA-Z0-9_]+)\[(.*?)\]", ai_msg, re.DOTALL)
            thought_match = re.search(r"Thought:\s*(.*?)(?=Action:|$)", ai_msg, re.DOTALL)

            thought_text = thought_match.group(1).strip() if thought_match else "Đang phân tích..."

            if action_match:
                tool_name = action_match.group(1).strip()
                tool_arg = action_match.group(2).strip()

                # Execute Tool
                obs = _run_tool(tool_name, tool_arg)

                step_info = {
                    "step": step_num,
                    "thought": thought_text,
                    "action": f"{tool_name}[{tool_arg[:100]}...]" if len(tool_arg) > 100 else f"{tool_name}[{tool_arg}]",
                    "observation": obs
                }
                steps_record.append(step_info)

                if step_callback:
                    step_callback(step_info)

                # Feed observation back to conversation
                obs_text = f"Observation: {obs}"
                conversation.append({"role": "user", "content": obs_text})
            else:
                # No action found, treat message as final answer
                final_answer = ai_msg
                break

        except Exception as e:
            final_answer = f"[Lỗi Agent: {str(e)}]"
            break

    if not final_answer and steps_record:
        final_answer = steps_record[-1].get("thought", "Đã hoàn thành các bước tác tử.")

    total_elapsed = int((time.time() - t_start) * 1000)
    return {
        "steps": steps_record,
        "final_answer": final_answer,
        "total_latency_ms": total_elapsed,
        "success": bool(final_answer and not final_answer.startswith("[Lỗi"))
    }
