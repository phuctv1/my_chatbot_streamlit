# ⚡ Codex AI Chatbot - Titanium Super-App Edition 4.0 (Ultimate)

Hệ thống AI Super-App thế hệ mới được nâng cấp toàn diện lên tầm **Doanh nghiệp & Tác tử Tự hành (Autonomous Agent & Enterprise Architecture)**, tích hợp trực tiếp với endpoint `https://codex.fosta.app/v1` cùng các mô hình hàng đầu (`claude-opus-5-5`, `gpt-6.1-sol`, `gpt-4o`, `claude-3-5-sonnet`, `o1-preview`...).

---

## 🌟 4 Chế Độ Vận Hành Đỉnh Cao (4 Operating Modes)

Bật tắt linh hoạt ngay tại Sidebar:

1. **💬 Standard Chat (Trò chuyện Siêu cấp)**:
   - Streaming tokens thời gian thực, tự động nhận diện liên kết & cào nội dung web.
   - Trợ lý đa phương thức (Multimodal Vision): Phân tích hình ảnh `.png`, `.jpg`, `.webp`.
   - Đọc tài liệu đa định dạng: PDF, Word, Excel, CSV, Code.
   - Trình thực thi Python cục bộ: Chạy mã và vẽ biểu đồ Matplotlib hiển thị ngay trên chat.
   - Claude-style Live Artifacts: Khung vẽ HTML/CSS/JS sandbox & SVG tương tác trực tiếp.
   - Vẽ sơ đồ luồng kiến trúc động với **Mermaid.js** (Flowchart, Sequence, Architecture).
   - Bộ so sánh khác biệt mã nguồn (Git-Style Code Diff).

2. **⚔️ Model Arena (Đấu trường So sánh Song song 2 Mô hình)**:
   - Chạy đồng thời 2 mô hình (ví dụ: `claude-opus-5-5` vs `gpt-6.1-sol`) trên cùng một câu hỏi.
   - So sánh trực quan độ trễ (latency ms), số lượng tokens và tốc độ sinh chữ (tok/s).
   - Bảng điểm bình chọn: 🏆 Model A thắng, 🤝 Hòa, hoặc 🏆 Model B thắng với bộ đếm tỷ số.

3. **🤖 Autonomous ReAct Agent (Tác tử Hành động Tự chủ)**:
   - Hoạt động theo quy trình ReAct (*Thought ➔ Action ➔ Observation ➔ Final Answer*).
   - Agent tự động lập kế hoạch và chủ động gọi các công cụ cục bộ:
     - `python_sandbox`: Chạy code Python tính toán phức tạp hoặc vẽ đồ thị.
     - `web_search`: Tìm kiếm thông tin thực tế trên Internet.
     - `url_reader`: Đọc toàn bộ bài viết từ trang web.
     - `knowledge_search`: Tra cứu tài liệu nội bộ.
     - `calculator`: Tính toán số học chính xác.

4. **👥 AI Council (Hội đồng 3 Mô hình Đồng thuận)**:
   - 3 mô hình AI độc lập phân tích bài toán phức tạp song song.
   - Chủ tịch Hội Đồng (Synthesizer Model) tổng hợp thành báo cáo đúc kết:
     - 🎯 **Điểm Đồng Thuận Cốt Lõi**
     - ⚖️ **Điểm Bất Đồng & Góc Nhìn Trái Chiều**
     - 🏆 **Phương Án Hành Động Tối Ưu Nhất**

---

## 📚 Kho Tri Thức Nội Bộ (RAG Knowledge Base)
- Tab **Kho Tri Thức** ở Sidebar: Cho phép tải lên các tài liệu tham khảo dài hạn (PDF, Word, Code, CSV, Markdown).
- Hệ thống tự động băm nhỏ (chunking), lập chỉ mục và thực hiện **Semantic Search bằng Vector TF-IDF / Cosine Similarity** (sử dụng NumPy).
- Khi bật tùy chọn **📚 Tra cứu Kho Tri Thức**, AI sẽ tự động trích xuất các đoạn thông tin liên quan nhất kèm nguồn trích dẫn cụ thể.

---

## 📁 Cấu Trúc Dự Án Siêu Cấp 4.0

```text
my_chatbot/
├── app.py                  # Ứng dụng Streamlit Super-App 4.0 (Giao diện chính)
├── app_tkinter.py          # Bản Desktop Tkinter Native
├── config.py               # Quản lý cấu hình & danh sách model nâng cấp
├── config.json             # Khóa API & cài đặt thực tế của bạn
├── requirements.txt        # Danh sách thư viện đầy đủ
├── run.bat                 # File nhấp đúp là chạy ngay trên Windows
├── start.ps1               # Script khởi chạy PowerShell
├── start.sh                # Script khởi chạy Linux / macOS
├── Dockerfile              # Dockerfile chuẩn hóa container
├── docker-compose.yml      # Triển khai 1-click qua Docker Compose
├── README.md               # Tài liệu hướng dẫn sử dụng chi tiết
├── modules/
│   ├── react_agent.py      # Tác tử ReAct tự động chạy công cụ (Python, Search, URL)
│   ├── ai_council.py       # Hội đồng 3 Model AI song song & tổng hợp đồng thuận
│   ├── knowledge_base.py   # RAG Vector Base (Băm tài liệu & tìm kiếm ngữ nghĩa)
│   ├── diagram_renderer.py # Render sơ đồ Mermaid.js vector SVG
│   ├── code_diff.py        # So sánh khác biệt code (Git-Style Diff Viewer)
│   ├── arena_mode.py       # Đấu trường so sánh 2 model song song & tính điểm
│   ├── web_search.py       # Tìm kiếm web DDG & đọc nội dung liên kết URL
│   ├── artifacts_preview.py# Live HTML/CSS/JS sandbox canvas & SVG renderer
│   ├── code_runner.py      # Trình thực thi Python sandbox & vẽ biểu đồ Matplotlib
│   ├── context_compactor.py# Nén ngữ cảnh thông minh tiết kiệm 70%+ token
│   ├── prompt_library.py   # Kho template Prompt kỹ thuật mẫu
│   ├── document_parser.py  # Trích xuất PDF, Word, Excel, CSV & Image Base64
│   ├── ai_service.py       # OpenAI Streaming, Latency metrics, <think> & Prompt Enhancer
│   ├── chat_manager.py     # Quản lý đa phiên chat, tìm kiếm từ khóa, Fork chat & Pin
│   └── personas.py         # Thư viện 9 chuyên gia (Dev, Data, UI/UX, Legal, Translator...)
└── data/
    ├── sessions/           # Lưu trữ lịch sử các phiên chat (.json)
    └── knowledge_base/     # Lưu trữ chỉ mục vector Kho Tri Thức nội bộ (.json)
```

---

## 🚀 Hướng Dẫn Khởi Chạy

### 1. Khởi chạy nhanh trên Windows
- Nhấp đúp vào file [run.bat](file:///c:/Users/DEVPhuctv/Desktop/my_chatbot/run.bat).
- Hoặc chạy bằng PowerShell:
  ```powershell
  .\start.ps1
  ```

### 2. Khởi chạy bằng Docker
```bash
docker-compose up -d
```
Ứng dụng sẽ tự động chạy ngầm và mở cổng `http://localhost:8501`.
