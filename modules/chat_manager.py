"""
Multi-session Chat Manager for Codex AI Chatbot.
Persists and manages conversation sessions on disk (JSON format).
"""
import os
import json
import uuid
import re
from datetime import datetime
from typing import Dict, List, Any, Optional

SESSIONS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "sessions")
os.makedirs(SESSIONS_DIR, exist_ok=True)


def generate_session_id() -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    short_uuid = uuid.uuid4().hex[:6]
    return f"session_{timestamp}_{short_uuid}"


def get_session_file_path(session_id: str) -> str:
    # Sanitize session_id to prevent path traversal
    safe_id = re.sub(r'[^a-zA-Z0-9_-]', '', session_id)
    return os.path.join(SESSIONS_DIR, f"{safe_id}.json")


def create_new_session(title: str = "Cuộc trò chuyện mới", model: str = "claude-opus-5-5", persona: str = "general") -> Dict[str, Any]:
    """Create a new chat session and save it to disk."""
    session_id = generate_session_id()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    session_data = {
        "id": session_id,
        "title": title,
        "created_at": now_str,
        "updated_at": now_str,
        "model": model,
        "persona": persona,
        "messages": [],
        "pinned_messages": [],
        "stats": {
            "total_tokens": 0,
            "message_count": 0
        }
    }

    save_session(session_data)
    return session_data


def save_session(session_data: Dict[str, Any]) -> bool:
    """Save session data to JSON file."""
    try:
        session_id = session_data.get("id")
        if not session_id:
            return False

        session_data["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if "messages" in session_data:
            if "stats" not in session_data:
                session_data["stats"] = {}
            session_data["stats"]["message_count"] = len(session_data["messages"])

        file_path = get_session_file_path(session_id)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(session_data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"[Error] Failed to save session {session_data.get('id')}: {e}")
        return False


def load_session(session_id: str) -> Optional[Dict[str, Any]]:
    """Load a session by its ID."""
    try:
        file_path = get_session_file_path(session_id)
        if not os.path.exists(file_path):
            return None

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict):
                return data
    except Exception as e:
        print(f"[Error] Failed to load session {session_id}: {e}")
    return None


def list_sessions(search_query: str = "") -> List[Dict[str, Any]]:
    """Return a list of all saved sessions sorted by last updated descending, with optional keyword filter."""
    sessions = []
    if not os.path.exists(SESSIONS_DIR):
        return sessions

    q_clean = search_query.strip().lower()

    for filename in os.listdir(SESSIONS_DIR):
        if filename.endswith(".json"):
            file_path = os.path.join(SESSIONS_DIR, filename)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict) and "id" in data:
                        title = data.get("title", "Cuộc trò chuyện")
                        msgs = data.get("messages", [])

                        # Match query in title or in message contents
                        if q_clean:
                            matched = (q_clean in title.lower())
                            if not matched:
                                for m in msgs:
                                    if q_clean in m.get("content", "").lower():
                                        matched = True
                                        break
                            if not matched:
                                continue

                        sessions.append({
                            "id": data.get("id"),
                            "title": title,
                            "created_at": data.get("created_at", ""),
                            "updated_at": data.get("updated_at", ""),
                            "model": data.get("model", ""),
                            "persona": data.get("persona", "general"),
                            "message_count": len(msgs)
                        })
            except Exception:
                continue

    # Sort descending by updated_at
    sessions.sort(key=lambda s: s.get("updated_at", ""), reverse=True)
    return sessions


def delete_session(session_id: str) -> bool:
    """Delete a session file from disk."""
    try:
        file_path = get_session_file_path(session_id)
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
    except Exception as e:
        print(f"[Error] Failed to delete session {session_id}: {e}")
    return False


def rename_session(session_id: str, new_title: str) -> bool:
    """Rename an existing session."""
    session = load_session(session_id)
    if session:
        session["title"] = new_title.strip() or "Cuộc trò chuyện"
        return save_session(session)
    return False


def duplicate_session(session_id: str) -> Optional[Dict[str, Any]]:
    """Clone an existing session into a new forked session."""
    original = load_session(session_id)
    if not original:
        return None

    new_id = generate_session_id()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cloned = dict(original)
    cloned["id"] = new_id
    cloned["title"] = f"{original.get('title', 'Chat')} (Bản sao)"
    cloned["created_at"] = now_str
    cloned["updated_at"] = now_str
    # Deep copy messages
    cloned["messages"] = [dict(m) for m in original.get("messages", [])]

    save_session(cloned)
    return cloned


def auto_title_session(session_data: Dict[str, Any], user_first_prompt: str):
    """Generate a neat session title from user's first prompt if title is default."""
    current_title = session_data.get("title", "")
    if current_title in ["Cuộc trò chuyện mới", "New Chat", ""]:
        cleaned = user_first_prompt.strip().replace("\n", " ")
        if len(cleaned) > 36:
            cleaned = cleaned[:33] + "..."
        session_data["title"] = cleaned
        save_session(session_data)


def pin_message(session_id: str, message: Dict[str, Any]) -> bool:
    """Pin a high-value message to the session's pinned bookmarks."""
    session = load_session(session_id)
    if session:
        if "pinned_messages" not in session:
            session["pinned_messages"] = []
        if not any(p.get("content") == message.get("content") for p in session["pinned_messages"]):
            session["pinned_messages"].append(dict(message))
            return save_session(session)
    return False


def unpin_message(session_id: str, pin_index: int) -> bool:
    """Remove a message from the session's pinned bookmarks."""
    session = load_session(session_id)
    if session and "pinned_messages" in session:
        if 0 <= pin_index < len(session["pinned_messages"]):
            session["pinned_messages"].pop(pin_index)
            return save_session(session)
    return False
