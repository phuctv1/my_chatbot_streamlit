"""
Curated Prompt Library and Engineering Templates for Codex AI Chatbot.
"""
from typing import Dict, List, Any

PROMPT_CATEGORIES: Dict[str, List[Dict[str, Any]]] = {
    "💻 Lập trình & Kỹ thuật": [
        {
            "title": "Tối ưu & Tái cấu trúc Code (Refactor)",
            "icon": "⚡",
            "desc": "Tối ưu hóa mã nguồn theo Clean Code, SOLID và cải thiện hiệu năng Big O.",
            "prompt": "Hãy phân tích, tối ưu và tái cấu trúc (refactor) đoạn mã nguồn dưới đây. Giải thích rõ các điểm cải tiến về độ phức tạp (Big O), type hints và cách xử lý ngoại lệ:\n\n```python\n# Dán code vào đây\n```"
        },
        {
            "title": "Thiết kế RESTful API chuẩn quốc tế",
            "icon": "🌐",
            "desc": "Xây dựng schema và endpoints chuẩn mực kèm Pydantic v2 validation.",
            "prompt": "Hãy thiết kế cấu trúc RESTful API hoàn chỉnh bằng Python (FastAPI/Pydantic) cho hệ thống [Điền tên dịch vụ/nghiệp vụ]. Bao gồm các phương thức GET, POST, PUT, DELETE, cơ chế xác thực JWT và xử lý phân trang (pagination)."
        },
        {
            "title": "Viết Bộ Unit Test Toàn diện",
            "icon": "🧪",
            "desc": "Tạo test suite với pytest bao gồm mock, edge cases và boundary values.",
            "prompt": "Hãy viết một bộ kiểm thử đơn vị (Unit Tests) toàn diện bằng pytest cho hàm/module sau. Đảm bảo bao quát các trường hợp biên (edge cases), dữ liệu hợp lệ, dữ liệu lỗi và sử dụng mock khi cần thiết:\n\n```python\n# Dán hàm cần test\n```"
        },
        {
            "title": "Debug & Tìm lỗ hổng Bảo mật (Security Audit)",
            "icon": "🛡️",
            "desc": "Kiểm tra lỗ hổng OWASP, SQL Injection, XSS, Buffer Overflow.",
            "prompt": "Hãy đóng vai trò chuyên gia an toàn thông tin (Security Auditor). Hãy rà soát đoạn mã nguồn dưới đây để tìm các lỗ hổng bảo mật (OWASP Top 10, SQL injection, memory leak, auth bypass) và đề xuất bản vá code an toàn:\n\n```python\n# Dán code vào đây\n```"
        }
    ],
    "📊 Khoa học Dữ liệu & Phân tích": [
        {
            "title": "Phân tích Khám phá Dữ liệu (EDA Pipeline)",
            "icon": "📈",
            "desc": "Quy trình EDA chuẩn với Pandas, thống kê mô tả và phát hiện ngoại lai.",
            "prompt": "Hãy viết một script Python hoàn chỉnh thực hiện Exploratory Data Analysis (EDA) cho bộ dữ liệu có các trường [Mô tả các cột]. Script cần: xử lý missing values, tính toán tương quan (correlation matrix), phát hiện outliers bằng IQR và vẽ biểu đồ phân phối bằng matplotlib/seaborn."
        },
        {
            "title": "Tối ưu Câu lệnh Truy vấn SQL phức tạp",
            "icon": "🗄️",
            "desc": "Tối ưu JOIN, Indexing, Window functions và CTE.",
            "prompt": "Hãy phân tích và tối ưu hóa câu lệnh SQL dưới đây để đạt tốc độ truy vấn cao nhất trên tập dữ liệu hàng triệu dòng. Giải thích kế hoạch thực thi (EXPLAIN plan) và cách tạo Index tối ưu:\n\n```sql\n-- Dán câu lệnh SQL\n```"
        },
        {
            "title": "Xây dựng Mô hình Machine Learning Baseline",
            "icon": "🤖",
            "desc": "Pipeline từ tiền xử lý, huấn luyện, cross-validation đến đánh giá metric.",
            "prompt": "Hãy xây dựng một pipeline Machine Learning hoàn chỉnh bằng Scikit-Learn cho bài toán [Phân loại / Dự đoán]. Bao gồm: Feature scaling, xử lý mất cân bằng dữ liệu, Stratified K-Fold, huấn luyện mô hình XGBoost/RandomForest và báo cáo ROC-AUC, F1-score."
        }
    ],
    "✍️ Sáng tạo & Marketing": [
        {
            "title": "Kịch bản Video Ngắn Viral (TikTok/Reels)",
            "icon": "🎬",
            "desc": "Kịch bản 45 giây với Hook 3 giây đầu, Body giữ chân và CTA mạnh.",
            "prompt": "Hãy viết một kịch bản video ngắn (TikTok/Reels/Shorts) độ dài 45-60 giây về chủ đề [Chủ đề]. Cấu trúc gồm: \n1. Hook (3 giây đầu gây tò mò cực độ)\n2. Thân bài (3 giá trị đắt giá, nhịp điệu nhanh)\n3. Kêu gọi hành động (CTA) tự nhiên."
        },
        {
            "title": "Bài viết Chuẩn SEO Chuyên sâu",
            "icon": "📝",
            "desc": "Bài viết 1500 từ chuẩn SEO với từ khóa mục tiêu, H2, H3 và FAQ Schema.",
            "prompt": "Hãy viết một bài viết chuyên sâu chuẩn SEO về chủ đề [Chủ đề], từ khóa chính là [Từ khóa]. Cấu trúc bao gồm: Tiêu đề H1 hấp dẫn, Meta Description, các thẻ H2/H3 logic, giọng văn chuyên gia nhưng dễ hiểu, kèm phần Câu hỏi thường gặp (FAQ)."
        },
        {
            "title": "Chiến dịch Email B2B Chốt Deal",
            "icon": "📧",
            "desc": "Chuỗi 3 email tiếp cận khách hàng doanh nghiệp theo mô hình Cold Outreach.",
            "prompt": "Hãy soạn chuỗi 3 email Cold Outreach tiếp cận khách hàng doanh nghiệp (B2B) để giới thiệu sản phẩm [Tên sản phẩm]. Tỷ lệ mở cao, tập trung giải quyết nỗi đau (Pain Point) và đề xuất lịch hẹn demo ngắn 15 phút."
        }
    ],
    "🎓 Học tập & Tư duy": [
        {
            "title": "Giải thích theo Phương pháp Feynman (ELI5)",
            "icon": "🧠",
            "desc": "Giải thích khái niệm phức tạp nhất bằng ví dụ đời thường mà đứa trẻ 10 tuổi cũng hiểu.",
            "prompt": "Hãy giải thích khái niệm [Khái niệm phức tạp, ví dụ: Quantum Computing, Blockchain, Neural Networks] theo phương pháp Feynman. Dùng các phép so sánh (analogy) đời thường, trực quan, không dùng thuật ngữ cao siêu để người mới bắt đầu có thể nắm bắt ngay lập tức."
        },
        {
            "title": "Phỏng vấn Giả lập (Mock Interview)",
            "icon": "👔",
            "desc": "Đóng vai người phỏng vấn khó tính và đánh giá câu trả lời từng vòng.",
            "prompt": "Hãy đóng vai Trưởng phòng Công nghệ (CTO) đang phỏng vấn tôi cho vị trí [Tên vị trí]. Hãy lần lượt đặt từng câu hỏi chuyên môn và tình huống từ dễ đến khó. Sau mỗi câu trả lời của tôi, hãy nhận xét ưu/nhược điểm và chấm điểm trước khi sang câu hỏi tiếp theo."
        }
    ]
}


def get_all_categories() -> List[str]:
    return list(PROMPT_CATEGORIES.keys())


def get_prompts_by_category(category: str) -> List[Dict[str, Any]]:
    return PROMPT_CATEGORIES.get(category, [])
