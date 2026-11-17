"""
Configuration manager for the Codex AI Chatbot.
Loads and persists user settings from config.json or environment variables.
"""
import json
import os
from typing import Dict, Any

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

DEFAULT_CONFIG: Dict[str, Any] = {
    "api_key": "",
    "base_url": "https://codex.fosta.app/v1",
    "model": "claude-opus-5-5",
    "temperature": 0.5,
    "max_tokens": 4096,
    "system_prompt": "You are a helpful, respectful, and intelligent AI assistant. Answer clearly and concisely.",
    "theme": "dark"
}

POPULAR_MODELS = [
    "claude-opus-5-5",
    "gpt-6.1-sol",
    "gpt-4o",
    "gpt-4o-mini",
    "claude-3-5-sonnet",
    "o1-preview",
    "o3-mini",
    "gemini-1.5-pro",
]

def load_config() -> Dict[str, Any]:
    """Load configuration from config.json, falling back to defaults and env vars."""
    config = dict(DEFAULT_CONFIG)

    # 1. Try to load from config.json
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    config.update(data)
        except Exception as e:
            print(f"[Warning] Failed to read config.json: {e}")

    # 2. Check environment variables as fallback if not set in config
    if not config.get("api_key"):
        env_key = os.environ.get("OPENAI_API_KEY")
        if env_key:
            config["api_key"] = env_key

    env_base = os.environ.get("OPENAI_BASE_URL")
    if env_base:
        config["base_url"] = env_base

    return config

def save_config(config_data: Dict[str, Any]) -> bool:
    """Save configuration dictionary to config.json."""
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"[Error] Failed to save config.json: {e}")
        return False
