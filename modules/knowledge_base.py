"""
Persistent RAG Knowledge Base and Vector Retrieval for Codex AI Chatbot.
Chunks documents and performs TF-IDF / Cosine Similarity semantic search using NumPy.
"""
import os
import json
import re
from typing import List, Dict, Any, Tuple
import numpy as np
from collections import Counter

KB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "knowledge_base")
KB_INDEX_FILE = os.path.join(KB_DIR, "index.json")
os.makedirs(KB_DIR, exist_ok=True)


def _tokenize(text: str) -> List[str]:
    """Tokenize text into lowercase words/terms."""
    return re.findall(r"\w+", text.lower())


def _chunk_text(text: str, chunk_size: int = 800, overlap: int = 150) -> List[str]:
    """Split text into overlapping semantic chunks."""
    if not text:
        return []

    # Clean text
    clean = re.sub(r"\s+", " ", text).strip()
    if len(clean) <= chunk_size:
        return [clean]

    chunks = []
    start = 0
    while start < len(clean):
        end = min(start + chunk_size, len(clean))
        # Try to break at a sentence boundary if possible
        if end < len(clean):
            last_period = clean.rfind(". ", start, end)
            if last_period != -1 and last_period > start + chunk_size // 2:
                end = last_period + 1

        chunk = clean[start:end].strip()
        if chunk:
            chunks.append(chunk)

        if end >= len(clean):
            break
        start = max(start + 1, end - overlap)

    return chunks


def load_kb_data() -> Dict[str, Any]:
    """Load the knowledge base index from disk."""
    if os.path.exists(KB_INDEX_FILE):
        try:
            with open(KB_INDEX_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
        except Exception as e:
            print(f"[Error] Failed to load KB: {e}")
    return {"documents": {}, "chunks": []}


def save_kb_data(kb_data: Dict[str, Any]) -> bool:
    """Save the knowledge base index to disk."""
    try:
        with open(KB_INDEX_FILE, "w", encoding="utf-8") as f:
            json.dump(kb_data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"[Error] Failed to save KB: {e}")
        return False


def add_document_to_kb(filename: str, file_type: str, raw_text: str) -> int:
    """
    Chunk and index a document into the Knowledge Base.
    Returns the number of chunks added.
    """
    kb = load_kb_data()
    chunks = _chunk_text(raw_text)

    # Remove any existing chunks for this document
    kb["chunks"] = [c for c in kb.get("chunks", []) if c.get("source") != filename]

    for idx, c_text in enumerate(chunks):
        kb["chunks"].append({
            "source": filename,
            "file_type": file_type,
            "chunk_id": f"{filename}_{idx+1}",
            "chunk_idx": idx + 1,
            "total_chunks": len(chunks),
            "text": c_text
        })

    kb["documents"][filename] = {
        "file_type": file_type,
        "chunk_count": len(chunks),
        "char_count": len(raw_text)
    }

    save_kb_data(kb)
    return len(chunks)


def query_kb(query: str, top_k: int = 3) -> List[Dict[str, Any]]:
    """
    Search the Knowledge Base for the most relevant document chunks.
    Returns list of chunks with relevance scores.
    """
    kb = load_kb_data()
    chunks = kb.get("chunks", [])
    if not chunks or not query.strip():
        return []

    q_tokens = _tokenize(query)
    if not q_tokens:
        return []

    # Build local vocabulary across chunks and query
    all_tokens = list(q_tokens)
    for c in chunks:
        all_tokens.extend(_tokenize(c.get("text", "")))

    vocab = list(set(all_tokens))
    word2idx = {w: i for i, w in enumerate(vocab)}

    def vectorize(text: str) -> np.ndarray:
        vec = np.zeros(len(vocab), dtype=np.float32)
        for w, count in Counter(_tokenize(text)).items():
            if w in word2idx:
                vec[word2idx[w]] = count
        norm = np.linalg.norm(vec)
        return vec / norm if norm > 0 else vec

    q_vec = vectorize(query)

    scored_chunks = []
    for c in chunks:
        c_vec = vectorize(c.get("text", ""))
        score = float(np.dot(q_vec, c_vec))
        if score > 0.05:  # Relevance threshold
            c_copy = dict(c)
            c_copy["score"] = round(score, 3)
            scored_chunks.append(c_copy)

    # Sort descending by similarity score
    scored_chunks.sort(key=lambda x: x["score"], reverse=True)
    return scored_chunks[:top_k]


def format_kb_context_for_prompt(retrieved_chunks: List[Dict[str, Any]]) -> str:
    """Format retrieved knowledge chunks with source citations for LLM prompt."""
    if not retrieved_chunks:
        return ""

    lines = ["\n📚 **[Thông tin trích xuất từ Kho Tri Thức Nội Bộ (Knowledge Base)]**"]
    for i, chunk in enumerate(retrieved_chunks, 1):
        source = chunk.get("source", "Tài liệu")
        idx_str = f"Phần {chunk.get('chunk_idx', 1)}/{chunk.get('total_chunks', 1)}"
        lines.append(f"[{i}] *Nguồn: `{source}` ({idx_str}) - Độ khớp: {chunk.get('score')}*")
        lines.append(f"\"{chunk.get('text', '')}\"\n")

    lines.append("Hãy sử dụng thông tin từ Kho Tri Thức trên để trả lời câu hỏi và kèm trích dẫn nguồn khi cần thiết.\n")
    return "\n".join(lines)


def list_kb_documents() -> Dict[str, Any]:
    kb = load_kb_data()
    return kb.get("documents", {})


def delete_kb_document(filename: str) -> bool:
    kb = load_kb_data()
    if filename in kb.get("documents", {}):
        del kb["documents"][filename]
        kb["chunks"] = [c for c in kb.get("chunks", []) if c.get("source") != filename]
        return save_kb_data(kb)
    return False


def clear_kb() -> bool:
    return save_kb_data({"documents": {}, "chunks": []})
