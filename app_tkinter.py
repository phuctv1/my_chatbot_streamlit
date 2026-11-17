"""
Codex AI Chatbot - A Modern Desktop AI Chat Client
Built with Python, Tkinter, and OpenAI Python SDK.
"""

import os
import sys
import json
import re
import threading
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

from config import load_config, save_config, POPULAR_MODELS, CONFIG_FILE

# Enable high-DPI scaling on Windows
try:
    import ctypes
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

# Theme Colors (Modern Dark / Catppuccin & Tokyo Night aesthetic)
THEME = {
    "bg_root": "#14151e",
    "bg_main": "#14151e",
    "bg_sidebar": "#1a1b26",
    "bg_chat": "#16161e",
    "bg_card": "#24273a",
    "bg_input": "#1f2335",
    "bg_entry": "#24273a",
    "border": "#2f334d",
    "border_highlight": "#7aa2f7",
    "fg_text": "#c0caf5",
    "fg_heading": "#ffffff",
    "fg_muted": "#7aa2f7",
    "fg_dim": "#565f89",
    "accent_primary": "#7aa2f7",
    "accent_hover": "#89b4fa",
    "btn_primary": "#3b82f6",
    "btn_primary_hover": "#60a5fa",
    "btn_danger": "#f7768e",
    "btn_danger_hover": "#ff9eaf",
    "btn_neutral": "#292e42",
    "btn_neutral_hover": "#3b4261",
    "user_badge": "#7aa2f7",
    "user_bg": "#1e2238",
    "bot_badge": "#9ece6a",
    "bot_bg": "#1a1b26",
    "code_bg": "#101014",
    "code_fg": "#bb9af7",
    "status_ready": "#9ece6a",
    "status_busy": "#e0af68",
    "status_err": "#f7768e",
}


class ChatbotApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Codex AI Chatbot")
        self.root.geometry("1080x760")
        self.root.minsize(860, 600)
        self.root.configure(bg=THEME["bg_root"])

        # Load configuration
        self.config = load_config()

        # State tracking
        self.conversation_history = []  # List of {"role": "user"|"assistant"|"system", "content": "..."}
        self.is_generating = False
        self.stop_event = threading.Event()
        self.sidebar_visible = True
        self.current_stream_response = []
        self.current_bubble_start = "1.0"
        self.last_user_input = ""
        self.input_history = []
        self.history_index = -1

        # Apply ttk styles
        self._setup_styles()

        # Build UI layout
        self._build_ui()

        # Keyboard shortcuts
        self._setup_shortcuts()

        # Check OpenAI SDK
        if OpenAI is None:
            self.append_system_message("⚠️ OpenAI package is not installed. Run 'pip install openai' in your terminal.")

        # Display initial greeting
        self._display_welcome()

    def _setup_styles(self):
        """Configure ttk styles to match the modern dark theme."""
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass

        # Scrollbar
        style.configure("Vertical.TScrollbar",
                        background=THEME["border"],
                        troughcolor=THEME["bg_chat"],
                        bordercolor=THEME["bg_chat"],
                        arrowcolor=THEME["fg_text"],
                        lightcolor=THEME["border"],
                        darkcolor=THEME["border"])
        style.map("Vertical.TScrollbar",
                  background=[("active", THEME["accent_primary"]), ("pressed", THEME["accent_hover"])])

        # Combobox
        style.configure("Dark.TCombobox",
                        fieldbackground=THEME["bg_entry"],
                        background=THEME["border"],
                        foreground=THEME["fg_text"],
                        arrowcolor=THEME["fg_text"],
                        bordercolor=THEME["border"],
                        lightcolor=THEME["border"],
                        darkcolor=THEME["border"])
        style.map("Dark.TCombobox",
                  fieldbackground=[("readonly", THEME["bg_entry"])],
                  selectbackground=[("readonly", THEME["btn_primary"])],
                  selectforeground=[("readonly", "#ffffff")])

    def _build_ui(self):
        """Build the complete application layout."""
        # Main container with two columns: Sidebar & Chat
        self.main_container = tk.Frame(self.root, bg=THEME["bg_root"])
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # ------------------ LEFT SIDEBAR ------------------
        self.sidebar_frame = tk.Frame(self.main_container, bg=THEME["bg_sidebar"], width=300, padx=16, pady=16)
        self.sidebar_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar_frame.pack_propagate(False)

        self._build_sidebar()

        # Split divider
        self.divider = tk.Frame(self.main_container, bg=THEME["border"], width=1)
        self.divider.pack(side=tk.LEFT, fill=tk.Y)

        # ------------------ RIGHT MAIN CHAT AREA ------------------
        self.chat_container = tk.Frame(self.main_container, bg=THEME["bg_main"])
        self.chat_container.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self._build_chat_header()
        self._build_chat_view()
        self._build_input_area()
        self._build_status_bar()

    def _build_sidebar(self):
        """Construct the sidebar content (Branding, New Chat, API Settings, Actions)."""
        # Branding
        brand_frame = tk.Frame(self.sidebar_frame, bg=THEME["bg_sidebar"])
        brand_frame.pack(fill=tk.X, pady=(0, 16))

        title_lbl = tk.Label(brand_frame, text="⚡ Codex AI Chat", font=("Segoe UI", 15, "bold"),
                             fg=THEME["fg_heading"], bg=THEME["bg_sidebar"])
        title_lbl.pack(anchor="w")

        sub_lbl = tk.Label(brand_frame, text="Desktop Assistant Client", font=("Segoe UI", 9),
                           fg=THEME["fg_dim"], bg=THEME["bg_sidebar"])
        sub_lbl.pack(anchor="w")

        # + New Chat Button
        self.new_chat_btn = tk.Button(self.sidebar_frame, text="＋  New Chat", font=("Segoe UI", 10, "bold"),
                                      bg=THEME["btn_primary"], fg="#ffffff", activebackground=THEME["btn_primary_hover"],
                                      activeforeground="#ffffff", relief=tk.FLAT, bd=0, padx=12, pady=8,
                                      cursor="hand2", command=self.clear_conversation)
        self.new_chat_btn.pack(fill=tk.X, pady=(0, 14))

        # Canvas/Scrollable Frame for Settings
        canvas = tk.Canvas(self.sidebar_frame, bg=THEME["bg_sidebar"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.sidebar_frame, orient="vertical", command=canvas.yview)
        self.settings_content = tk.Frame(canvas, bg=THEME["bg_sidebar"])

        self.settings_content.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=self.settings_content, anchor="nw", width=265)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # --- Settings Fields ---
        # Model Selection
        self._create_label(self.settings_content, "MODEL")
        self.model_var = tk.StringVar(value=self.config.get("model", "gpt-6.1-sol"))
        self.model_combo = ttk.Combobox(self.settings_content, textvariable=self.model_var,
                                        values=POPULAR_MODELS, style="Dark.TCombobox", font=("Segoe UI", 9))
        self.model_combo.pack(fill=tk.X, pady=(2, 10))
        self.model_combo.bind("<<ComboboxSelected>>", lambda e: self._on_model_change())

        # API Key Field
        key_header = tk.Frame(self.settings_content, bg=THEME["bg_sidebar"])
        key_header.pack(fill=tk.X)
        self._create_label(key_header, "API KEY", pack=False).pack(side=tk.LEFT)

        self.show_key_var = tk.BooleanVar(value=False)
        self.toggle_key_btn = tk.Button(key_header, text="👁 Show", font=("Segoe UI", 8),
                                        bg=THEME["bg_sidebar"], fg=THEME["fg_muted"], bd=0,
                                        activebackground=THEME["bg_sidebar"], activeforeground=THEME["fg_text"],
                                        cursor="hand2", command=self._toggle_key_visibility)
        self.toggle_key_btn.pack(side=tk.RIGHT)

        self.api_key_entry = tk.Entry(self.settings_content, font=("Segoe UI", 9),
                                      bg=THEME["bg_entry"], fg=THEME["fg_text"],
                                      insertbackground=THEME["fg_text"], bd=0,
                                      highlightthickness=1, highlightbackground=THEME["border"],
                                      highlightcolor=THEME["border_highlight"], show="●")
        self.api_key_entry.insert(0, self.config.get("api_key", ""))
        self.api_key_entry.pack(fill=tk.X, pady=(2, 10), ipady=5)

        # Base URL Field
        self._create_label(self.settings_content, "BASE URL")
        self.base_url_entry = tk.Entry(self.settings_content, font=("Segoe UI", 9),
                                       bg=THEME["bg_entry"], fg=THEME["fg_text"],
                                       insertbackground=THEME["fg_text"], bd=0,
                                       highlightthickness=1, highlightbackground=THEME["border"],
                                       highlightcolor=THEME["border_highlight"])
        self.base_url_entry.insert(0, self.config.get("base_url", "https://codex.fosta.app/v1"))
        self.base_url_entry.pack(fill=tk.X, pady=(2, 10), ipady=5)

        # Temperature Slider
        temp_header = tk.Frame(self.settings_content, bg=THEME["bg_sidebar"])
        temp_header.pack(fill=tk.X)
        self._create_label(temp_header, "TEMPERATURE", pack=False).pack(side=tk.LEFT)
        self.temp_val_lbl = tk.Label(temp_header, text=f"{self.config.get('temperature', 0.7):.2f}",
                                     font=("Segoe UI", 8), fg=THEME["fg_muted"], bg=THEME["bg_sidebar"])
        self.temp_val_lbl.pack(side=tk.RIGHT)

        self.temp_var = tk.DoubleVar(value=float(self.config.get("temperature", 0.7)))
        self.temp_scale = tk.Scale(self.settings_content, variable=self.temp_var, from_=0.0, to=1.5,
                                   resolution=0.05, orient=tk.HORIZONTAL, showvalue=False,
                                   bg=THEME["bg_sidebar"], fg=THEME["fg_text"],
                                   troughcolor=THEME["border"], activebackground=THEME["accent_primary"],
                                   highlightthickness=0, bd=0, command=self._on_temp_change)
        self.temp_scale.pack(fill=tk.X, pady=(2, 10))

        # System Prompt Field
        self._create_label(self.settings_content, "SYSTEM PROMPT")
        self.sys_prompt_text = tk.Text(self.settings_content, height=3, font=("Segoe UI", 9),
                                       bg=THEME["bg_entry"], fg=THEME["fg_text"],
                                       insertbackground=THEME["fg_text"], bd=0,
                                       highlightthickness=1, highlightbackground=THEME["border"],
                                       highlightcolor=THEME["border_highlight"], wrap=tk.WORD)
        self.sys_prompt_text.insert("1.0", self.config.get("system_prompt", ""))
        self.sys_prompt_text.pack(fill=tk.X, pady=(2, 12))

        # Buttons Frame (Save Settings & Test Connection)
        btns_row = tk.Frame(self.settings_content, bg=THEME["bg_sidebar"])
        btns_row.pack(fill=tk.X, pady=(0, 14))

        self.save_btn = tk.Button(btns_row, text="💾 Save", font=("Segoe UI", 9, "bold"),
                                  bg=THEME["btn_neutral"], fg=THEME["fg_text"],
                                  activebackground=THEME["btn_neutral_hover"], activeforeground="#ffffff",
                                  relief=tk.FLAT, bd=0, pady=6, cursor="hand2", command=self.save_settings)
        self.save_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))

        self.test_btn = tk.Button(btns_row, text="⚡ Test", font=("Segoe UI", 9, "bold"),
                                  bg=THEME["btn_neutral"], fg=THEME["fg_text"],
                                  activebackground=THEME["btn_neutral_hover"], activeforeground="#ffffff",
                                  relief=tk.FLAT, bd=0, pady=6, cursor="hand2", command=self.test_connection)
        self.test_btn.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(4, 0))

        # --- Sidebar Footer Actions ---
        footer_frame = tk.Frame(self.sidebar_frame, bg=THEME["bg_sidebar"])
        footer_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(8, 0))

        export_btn = tk.Button(footer_frame, text="📤 Export Conversation", font=("Segoe UI", 9),
                               bg=THEME["bg_sidebar"], fg=THEME["fg_text"],
                               activebackground=THEME["bg_card"], activeforeground="#ffffff",
                               relief=tk.FLAT, bd=1, highlightthickness=1,
                               highlightbackground=THEME["border"], pady=5,
                               cursor="hand2", command=self.export_conversation)
        export_btn.pack(fill=tk.X, pady=(0, 6))

        clear_btn = tk.Button(footer_frame, text="🗑️ Clear Chat History", font=("Segoe UI", 9),
                              bg=THEME["bg_sidebar"], fg=THEME["btn_danger"],
                              activebackground=THEME["bg_card"], activeforeground=THEME["btn_danger_hover"],
                              relief=tk.FLAT, bd=1, highlightthickness=1,
                              highlightbackground=THEME["border"], pady=5,
                              cursor="hand2", command=self.clear_conversation)
        clear_btn.pack(fill=tk.X)

    def _create_label(self, parent, text, pack=True):
        lbl = tk.Label(parent, text=text, font=("Segoe UI", 8, "bold"),
                       fg=THEME["fg_dim"], bg=THEME["bg_sidebar"])
        if pack:
            lbl.pack(anchor="w")
        return lbl

    def _build_chat_header(self):
        """Header above the chat display (Model indicator, status badge, sidebar toggle)."""
        header_frame = tk.Frame(self.chat_container, bg=THEME["bg_main"], height=52, padx=20)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        # Left: Toggle Sidebar button & Active Model badge
        left_box = tk.Frame(header_frame, bg=THEME["bg_main"])
        left_box.pack(side=tk.LEFT, fill=tk.Y)

        self.toggle_side_btn = tk.Button(left_box, text="☰", font=("Segoe UI", 12),
                                         bg=THEME["bg_main"], fg=THEME["fg_text"],
                                         activebackground=THEME["bg_card"], activeforeground="#ffffff",
                                         relief=tk.FLAT, bd=0, padx=8, cursor="hand2",
                                         command=self.toggle_sidebar)
        self.toggle_side_btn.pack(side=tk.LEFT, pady=8, padx=(0, 10))

        self.model_header_lbl = tk.Label(left_box, text=f"Model: {self.model_var.get()}",
                                         font=("Segoe UI", 11, "bold"), fg=THEME["fg_heading"],
                                         bg=THEME["bg_main"])
        self.model_header_lbl.pack(side=tk.LEFT, pady=12)

        # Right: Status Indicator & Message Count
        right_box = tk.Frame(header_frame, bg=THEME["bg_main"])
        right_box.pack(side=tk.RIGHT, fill=tk.Y)

        self.status_dot = tk.Label(right_box, text="●", font=("Segoe UI", 12),
                                   fg=THEME["status_ready"], bg=THEME["bg_main"])
        self.status_dot.pack(side=tk.LEFT, pady=12, padx=(0, 4))

        self.status_lbl = tk.Label(right_box, text="Ready", font=("Segoe UI", 9),
                                   fg=THEME["fg_text"], bg=THEME["bg_main"])
        self.status_lbl.pack(side=tk.LEFT, pady=12, padx=(0, 16))

        self.msg_count_lbl = tk.Label(right_box, text="0 messages", font=("Segoe UI", 9),
                                      fg=THEME["fg_dim"], bg=THEME["bg_main"])
        self.msg_count_lbl.pack(side=tk.LEFT, pady=12)

        # Thin divider below header
        hdr_div = tk.Frame(self.chat_container, bg=THEME["border"], height=1)
        hdr_div.pack(fill=tk.X)

    def _build_chat_view(self):
        """Construct the scrollable rich chat display widget with tags."""
        chat_box = tk.Frame(self.chat_container, bg=THEME["bg_chat"])
        chat_box.pack(fill=tk.BOTH, expand=True)

        self.chat_text = tk.Text(chat_box, bg=THEME["bg_chat"], fg=THEME["fg_text"],
                                 font=("Segoe UI", 10), wrap=tk.WORD, bd=0, padx=20, pady=20,
                                 insertbackground=THEME["fg_text"], selectbackground=THEME["btn_primary"],
                                 selectforeground="#ffffff", state=tk.DISABLED, cursor="arrow")

        scrollbar = ttk.Scrollbar(chat_box, orient="vertical", command=self.chat_text.yview, style="Vertical.TScrollbar")
        self.chat_text.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.chat_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Configure rich text tags
        self.chat_text.tag_configure("user_header", font=("Segoe UI", 10, "bold"),
                                     foreground=THEME["user_badge"], spacing1=12, spacing3=4)
        self.chat_text.tag_configure("user_body", font=("Segoe UI", 10),
                                     foreground="#ffffff", lmargin1=8, lmargin2=8, rmargin=20, spacing3=8)

        self.chat_text.tag_configure("bot_header", font=("Segoe UI", 10, "bold"),
                                     foreground=THEME["bot_badge"], spacing1=12, spacing3=4)
        self.chat_text.tag_configure("bot_body", font=("Segoe UI", 10),
                                     foreground=THEME["fg_text"], lmargin1=8, lmargin2=8, rmargin=20, spacing3=8)

        self.chat_text.tag_configure("timestamp", font=("Segoe UI", 8),
                                     foreground=THEME["fg_dim"])
        self.chat_text.tag_configure("system_msg", font=("Segoe UI", 9, "italic"),
                                     foreground=THEME["fg_dim"], justify="center", spacing1=8, spacing3=8)
        self.chat_text.tag_configure("error_msg", font=("Segoe UI", 9, "bold"),
                                     foreground=THEME["btn_danger"], spacing1=6, spacing3=6)

        # Markdown tags
        self.chat_text.tag_configure("code_block", font=("Consolas", 9),
                                     background=THEME["code_bg"], foreground=THEME["code_fg"],
                                     lmargin1=24, lmargin2=24, rmargin=24, spacing1=4, spacing3=4)
        self.chat_text.tag_configure("inline_code", font=("Consolas", 9),
                                     background=THEME["code_bg"], foreground=THEME["code_fg"])
        self.chat_text.tag_configure("bold_text", font=("Segoe UI", 10, "bold"), foreground="#ffffff")
        self.chat_text.tag_configure("italic_text", font=("Segoe UI", 10, "italic"))

        # Right-click context menu
        self.context_menu = tk.Menu(self.root, tearoff=0, bg=THEME["bg_card"], fg=THEME["fg_text"],
                                    activebackground=THEME["btn_primary"], activeforeground="#ffffff", bd=1)
        self.context_menu.add_command(label="Copy Selected", command=self._copy_selected_text)
        self.context_menu.add_command(label="Select All", command=self._select_all_chat)
        self.chat_text.bind("<Button-3>", self._show_context_menu)

    def _build_input_area(self):
        """Construct the message input box and Send/Stop button."""
        input_container = tk.Frame(self.chat_container, bg=THEME["bg_main"], padx=18, pady=12)
        input_container.pack(fill=tk.X, side=tk.BOTTOM)

        # Bordered Card for Input
        card = tk.Frame(input_container, bg=THEME["bg_input"], bd=0,
                        highlightthickness=1, highlightbackground=THEME["border"],
                        highlightcolor=THEME["border_highlight"])
        card.pack(fill=tk.X)

        # Multi-line Text entry
        self.user_input = tk.Text(card, height=3, font=("Segoe UI", 10),
                                  bg=THEME["bg_input"], fg=THEME["fg_text"],
                                  insertbackground=THEME["fg_text"], bd=0, padx=12, pady=10,
                                  wrap=tk.WORD, selectbackground=THEME["btn_primary"])
        self.user_input.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Button Box on right
        btn_box = tk.Frame(card, bg=THEME["bg_input"], padx=10, pady=10)
        btn_box.pack(side=tk.RIGHT, fill=tk.Y)

        self.send_btn = tk.Button(btn_box, text="Send 🚀", font=("Segoe UI", 9, "bold"),
                                  bg=THEME["btn_primary"], fg="#ffffff",
                                  activebackground=THEME["btn_primary_hover"], activeforeground="#ffffff",
                                  relief=tk.FLAT, bd=0, padx=16, pady=8, cursor="hand2",
                                  command=self.send_message)
        self.send_btn.pack(side=tk.BOTTOM)

        # Key bindings for Input
        self.user_input.bind("<Return>", self._on_enter_pressed)
        self.user_input.bind("<Shift-Return>", lambda e: None)  # Default newline
        self.user_input.bind("<Control-Return>", lambda e: self.user_input.insert(tk.INSERT, "\n"))
        self.user_input.bind("<Up>", self._on_key_up)

        # Placeholder management
        self.placeholder = "Type a message... (Press Enter to send, Shift+Enter for newline)"
        self._add_placeholder()
        self.user_input.bind("<FocusIn>", self._remove_placeholder)
        self.user_input.bind("<FocusOut>", self._restore_placeholder)

    def _build_status_bar(self):
        """Construct a subtle status bar below the input."""
        bar = tk.Frame(self.chat_container, bg=THEME["bg_main"], height=22, padx=18)
        bar.pack(fill=tk.X, side=tk.BOTTOM)

        self.hint_lbl = tk.Label(bar, text="Enter: Send | Shift+Enter: New Line | Ctrl+N: New Chat | Esc: Stop",
                                 font=("Segoe UI", 8), fg=THEME["fg_dim"], bg=THEME["bg_main"])
        self.hint_lbl.pack(side=tk.LEFT)

        self.token_info_lbl = tk.Label(bar, text=f"Endpoint: {self.config.get('base_url', '')}",
                                       font=("Segoe UI", 8), fg=THEME["fg_dim"], bg=THEME["bg_main"])
        self.token_info_lbl.pack(side=tk.RIGHT)

    def _setup_shortcuts(self):
        """Global keyboard shortcuts."""
        self.root.bind("<Control-n>", lambda e: self.clear_conversation())
        self.root.bind("<Control-N>", lambda e: self.clear_conversation())
        self.root.bind("<Control-s>", lambda e: self.export_conversation())
        self.root.bind("<Control-S>", lambda e: self.export_conversation())
        self.root.bind("<Escape>", lambda e: self.stop_generation())
        self.root.bind("<Control-k>", lambda e: self._focus_input())

    def _focus_input(self):
        self.user_input.focus_set()
        return "break"

    # ------------------ PLACEHOLDER & INPUT HANDLING ------------------
    def _add_placeholder(self):
        if not self.user_input.get("1.0", "end-1c"):
            self.user_input.insert("1.0", self.placeholder)
            self.user_input.configure(fg=THEME["fg_dim"])

    def _remove_placeholder(self, event=None):
        if self.user_input.get("1.0", "end-1c") == self.placeholder:
            self.user_input.delete("1.0", tk.END)
            self.user_input.configure(fg=THEME["fg_text"])

    def _restore_placeholder(self, event=None):
        if not self.user_input.get("1.0", "end-1c").strip():
            self._add_placeholder()

    def _on_enter_pressed(self, event):
        """Send message on Enter key unless Shift is pressed."""
        if not (event.state & 0x0001):  # No Shift modifier
            self.send_message()
            return "break"

    def _on_key_up(self, event):
        """Recall previous sent message if input is empty."""
        content = self.user_input.get("1.0", "end-1c")
        if (content == self.placeholder or not content.strip()) and self.input_history:
            if self.history_index < len(self.input_history) - 1:
                self.history_index += 1
                msg = self.input_history[-(self.history_index + 1)]
                self.user_input.delete("1.0", tk.END)
                self.user_input.insert("1.0", msg)
                self.user_input.configure(fg=THEME["fg_text"])
                return "break"

    # ------------------ SIDEBAR & SETTINGS LOGIC ------------------
    def toggle_sidebar(self):
        """Toggle left settings sidebar visibility."""
        if self.sidebar_visible:
            self.sidebar_frame.pack_forget()
            self.divider.pack_forget()
            self.toggle_side_btn.configure(text="☰ Settings")
            self.sidebar_visible = False
        else:
            self.sidebar_frame.pack(side=tk.LEFT, fill=tk.Y, before=self.chat_container)
            self.divider.pack(side=tk.LEFT, fill=tk.Y, before=self.chat_container)
            self.toggle_side_btn.configure(text="☰")
            self.sidebar_visible = True

    def _toggle_key_visibility(self):
        if self.show_key_var.get():
            self.api_key_entry.configure(show="●")
            self.toggle_key_btn.configure(text="👁 Show")
            self.show_key_var.set(False)
        else:
            self.api_key_entry.configure(show="")
            self.toggle_key_btn.configure(text="🙈 Hide")
            self.show_key_var.set(True)

    def _on_model_change(self):
        new_model = self.model_var.get().strip()
        self.model_header_lbl.configure(text=f"Model: {new_model}")

    def _on_temp_change(self, val):
        self.temp_val_lbl.configure(text=f"{float(val):.2f}")

    def save_settings(self):
        """Save settings to config.json and display visual confirmation."""
        api_key = self.api_key_entry.get().strip()
        base_url = self.base_url_entry.get().strip()
        model = self.model_var.get().strip()
        temp = float(self.temp_var.get())
        sys_prompt = self.sys_prompt_text.get("1.0", "end-1c").strip()

        if not base_url:
            base_url = "https://codex.fosta.app/v1"

        self.config["api_key"] = api_key
        self.config["base_url"] = base_url
        self.config["model"] = model
        self.config["temperature"] = temp
        self.config["system_prompt"] = sys_prompt

        success = save_config(self.config)
        self.token_info_lbl.configure(text=f"Endpoint: {base_url}")
        self.model_header_lbl.configure(text=f"Model: {model}")

        if success:
            original_text = self.save_btn.cget("text")
            self.save_btn.configure(text="✅ Saved!", bg=THEME["status_ready"], fg="#14151e")
            self.root.after(1500, lambda: self.save_btn.configure(text=original_text, bg=THEME["btn_neutral"], fg=THEME["fg_text"]))
        else:
            messagebox.showerror("Error", f"Failed to save configuration to {CONFIG_FILE}")

    def test_connection(self):
        """Verify API key and endpoint connectivity with a lightweight ping request."""
        api_key = self.api_key_entry.get().strip()
        base_url = self.base_url_entry.get().strip() or "https://codex.fosta.app/v1"
        model = self.model_var.get().strip() or "gpt-6.1-sol"

        if not api_key or api_key == "YOUR_API_KEY":
            messagebox.showwarning("API Key Missing", "Please enter your API Key before testing the connection.")
            self.api_key_entry.focus_set()
            return

        self.test_btn.configure(text="⏳ Testing...", state=tk.DISABLED)

        def worker():
            import time
            start_t = time.time()
            try:
                client = OpenAI(base_url=base_url, api_key=api_key)
                resp = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": "ping"}],
                    max_tokens=5,
                )
                elapsed = int((time.time() - start_t) * 1000)
                msg = f"Connection Successful! ({elapsed}ms)\n\nEndpoint: {base_url}\nModel '{model}' responded successfully."
                self.root.after(0, lambda: messagebox.showinfo("API Connection OK", msg))
            except Exception as e:
                err = str(e)
                self.root.after(0, lambda: messagebox.showerror("Connection Failed", f"Could not reach {base_url}:\n\n{err}"))
            finally:
                self.root.after(0, lambda: self.test_btn.configure(text="⚡ Test", state=tk.NORMAL))

        threading.Thread(target=worker, daemon=True).start()

    # ------------------ CHAT ACTIONS & LOGIC ------------------
    def _display_welcome(self):
        """Show initial welcome card."""
        welcome_text = (
            "👋 Welcome to Codex AI Chatbot!\n"
            f"Connected to: {self.config.get('base_url', 'https://codex.fosta.app/v1')}\n"
            f"Active Model: {self.config.get('model', 'gpt-6.1-sol')}\n\n"
            "• Enter your API Key in the left sidebar if not already configured.\n"
            "• Press Enter to send, Shift+Enter for a new line.\n"
            "• Ask anything in the message box below to start chatting!"
        )
        self.append_system_message(welcome_text)

    def send_message(self):
        """Triggered when user clicks Send or hits Enter."""
        if self.is_generating:
            return

        text = self.user_input.get("1.0", "end-1c").strip()
        if not text or text == self.placeholder:
            return

        # Check API key
        api_key = self.api_key_entry.get().strip()
        if not api_key or api_key == "YOUR_API_KEY":
            messagebox.showwarning(
                "API Key Required",
                "Please enter your API Key in the sidebar settings before sending a message."
            )
            self.api_key_entry.focus_set()
            return

        # Clear input field
        self.user_input.delete("1.0", tk.END)
        self.input_history.append(text)
        self.history_index = -1

        # Add to conversation history
        self.conversation_history.append({"role": "user", "content": text})
        self._update_msg_counter()

        # Display user message in chat
        now = datetime.now().strftime("%H:%M:%S")
        self._append_user_message("You", now, text)

        # Switch Send button to Stop button
        self._set_generating_state(True)

        # Start background streaming thread
        self.stop_event.clear()
        self.current_stream_response = []
        thread = threading.Thread(target=self._stream_worker, daemon=True)
        thread.start()

    def _stream_worker(self):
        """Background thread executing OpenAI chat completion stream."""
        base_url = self.base_url_entry.get().strip() or "https://codex.fosta.app/v1"
        api_key = self.api_key_entry.get().strip()
        model = self.model_var.get().strip() or "gpt-6.1-sol"
        temp = float(self.temp_var.get())
        sys_prompt = self.sys_prompt_text.get("1.0", "end-1c").strip()

        # Prepare messages payload
        payload = []
        if sys_prompt:
            payload.append({"role": "system", "content": sys_prompt})
        payload.extend(self.conversation_history)

        now = datetime.now().strftime("%H:%M:%S")
        self.root.after(0, self._prepare_assistant_bubble, model, now)

        try:
            client = OpenAI(base_url=base_url, api_key=api_key)

            response_stream = client.chat.completions.create(
                model=model,
                messages=payload,
                temperature=temp,
                stream=True,
            )

            for chunk in response_stream:
                if self.stop_event.is_set():
                    break
                if chunk.choices and chunk.choices[0].delta:
                    content = chunk.choices[0].delta.content
                    if content:
                        self.current_stream_response.append(content)
                        self.root.after(0, self._stream_append_token, content)

            full_text = "".join(self.current_stream_response)
            was_stopped = self.stop_event.is_set()
            self.root.after(0, self._on_generation_finished, full_text, was_stopped)

        except Exception as e:
            err_msg = str(e)
            self.root.after(0, self._on_generation_error, err_msg)

    def _set_generating_state(self, is_generating: bool):
        """Update UI controls during/after generation."""
        self.is_generating = is_generating
        if is_generating:
            self.send_btn.configure(text="⏹ Stop", bg=THEME["btn_danger"],
                                    activebackground=THEME["btn_danger_hover"],
                                    command=self.stop_generation)
            self.status_dot.configure(fg=THEME["status_busy"])
            self.status_lbl.configure(text="Generating...")
        else:
            self.send_btn.configure(text="Send 🚀", bg=THEME["btn_primary"],
                                    activebackground=THEME["btn_primary_hover"],
                                    command=self.send_message)
            self.status_dot.configure(fg=THEME["status_ready"])
            self.status_lbl.configure(text="Ready")
            self.user_input.focus_set()

    def stop_generation(self):
        """Cancel current ongoing stream."""
        if self.is_generating:
            self.stop_event.set()
            self.status_lbl.configure(text="Stopping...")

    def _append_user_message(self, sender: str, timestamp: str, text: str):
        """Render user message into chat view."""
        self.chat_text.configure(state=tk.NORMAL)
        self.chat_text.insert(tk.END, f"\n👤 {sender}  ", "user_header")
        self.chat_text.insert(tk.END, f"[{timestamp}]\n", "timestamp")

        start_idx = self.chat_text.index("end-1c")
        self.chat_text.insert(tk.END, f"{text}\n", "user_body")
        end_idx = self.chat_text.index("end-1c")

        self._format_markdown_in_range(start_idx, end_idx)

        self.chat_text.configure(state=tk.DISABLED)
        self.chat_text.see(tk.END)

    def _prepare_assistant_bubble(self, model: str, timestamp: str):
        """Start assistant bubble header prior to streaming tokens."""
        self.chat_text.configure(state=tk.NORMAL)
        self.chat_text.insert(tk.END, f"\n🤖 {model}  ", "bot_header")
        self.chat_text.insert(tk.END, f"[{timestamp}]\n", "timestamp")
        self.current_bubble_start = self.chat_text.index("end-1c")
        self.chat_text.configure(state=tk.DISABLED)
        self.chat_text.see(tk.END)

    def _stream_append_token(self, token: str):
        """Append incoming streaming token to chat view."""
        self.chat_text.configure(state=tk.NORMAL)
        self.chat_text.insert(tk.END, token, "bot_body")
        self.chat_text.configure(state=tk.DISABLED)
        self.chat_text.see(tk.END)

    def _on_generation_finished(self, full_text: str, was_stopped: bool):
        """Finalize message after stream finishes and apply markdown styling."""
        self.chat_text.configure(state=tk.NORMAL)

        # Apply markdown formatting (code blocks, inline code, bold) to response
        end_idx = self.chat_text.index("end-1c")
        self._format_markdown_in_range(self.current_bubble_start, end_idx)

        if was_stopped:
            self.chat_text.insert(tk.END, "\n[⏹ Stopped by user]\n", "system_msg")
            full_text += "\n[Stopped by user]"
        else:
            self.chat_text.insert(tk.END, "\n")

        # Embed a subtle Copy button for this assistant message
        if full_text.strip():
            self._insert_copy_button(full_text)

        self.chat_text.insert(tk.END, "\n")
        self.chat_text.configure(state=tk.DISABLED)
        self.chat_text.see(tk.END)

        if full_text.strip():
            self.conversation_history.append({"role": "assistant", "content": full_text})
            self._update_msg_counter()

        self._set_generating_state(False)

    def _format_markdown_in_range(self, start_pos: str, end_pos: str):
        """Parse markdown constructs in the given text range and apply formatting tags."""
        try:
            content = self.chat_text.get(start_pos, end_pos)
            if not content:
                return

            # Code blocks ```lang ... ```
            for match in re.finditer(r'```([a-zA-Z0-9_-]*)\n(.*?)```', content, re.DOTALL):
                s_tag = f"{start_pos} + {match.start()} chars"
                e_tag = f"{start_pos} + {match.end()} chars"
                self.chat_text.tag_add("code_block", s_tag, e_tag)

            # Inline code `...`
            for match in re.finditer(r'(?<!`)`([^`\n]+)`(?!`)', content):
                s_tag = f"{start_pos} + {match.start()} chars"
                e_tag = f"{start_pos} + {match.end()} chars"
                self.chat_text.tag_add("inline_code", s_tag, e_tag)

            # Bold **...**
            for match in re.finditer(r'\*\*([^\*\n]+)\*\*', content):
                s_tag = f"{start_pos} + {match.start()} chars"
                e_tag = f"{start_pos} + {match.end()} chars"
                self.chat_text.tag_add("bold_text", s_tag, e_tag)
        except Exception as e:
            # Non-critical styling failure
            pass

    def _insert_copy_button(self, text_to_copy: str):
        """Embed an inline 'Copy' button in the chat stream."""
        btn = tk.Button(self.chat_text, text="📋 Copy", font=("Segoe UI", 8),
                        bg=THEME["bg_card"], fg=THEME["fg_text"],
                        activebackground=THEME["btn_primary"], activeforeground="#ffffff",
                        relief=tk.FLAT, bd=0, padx=6, pady=2, cursor="hand2")
        btn.configure(command=lambda: self._copy_to_clipboard(text_to_copy, btn))
        self.chat_text.window_create(tk.END, window=btn)

    def _copy_to_clipboard(self, text: str, button: tk.Button = None):
        """Copy arbitrary string to clipboard with visual feedback."""
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        if button:
            orig = button.cget("text")
            button.configure(text="Copied! ✔")
            self.root.after(1200, lambda: button.configure(text=orig))

    def _on_generation_error(self, err_msg: str):
        """Handle and display OpenAI API errors cleanly."""
        self.chat_text.configure(state=tk.NORMAL)
        self.chat_text.insert(tk.END, f"\n⚠️ Error: {err_msg}\n\n", "error_msg")
        self.chat_text.configure(state=tk.DISABLED)
        self.chat_text.see(tk.END)

        self.status_dot.configure(fg=THEME["status_err"])
        self.status_lbl.configure(text="Error")
        self._set_generating_state(False)

    def append_system_message(self, text: str):
        """Append informational system card into chat view."""
        self.chat_text.configure(state=tk.NORMAL)
        self.chat_text.insert(tk.END, f"\n{text}\n\n", "system_msg")
        self.chat_text.configure(state=tk.DISABLED)
        self.chat_text.see(tk.END)

    def clear_conversation(self):
        """Clear current conversation history and wipe chat screen."""
        if self.is_generating:
            self.stop_generation()

        self.conversation_history.clear()
        self.chat_text.configure(state=tk.NORMAL)
        self.chat_text.delete("1.0", tk.END)
        self.chat_text.configure(state=tk.DISABLED)

        self._update_msg_counter()
        self._display_welcome()

    def export_conversation(self):
        """Export full chat history to Markdown (.md) or Text (.txt)."""
        if not self.conversation_history:
            messagebox.showinfo("Export Chat", "No conversation history to export.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".md",
            filetypes=[("Markdown files", "*.md"), ("Text files", "*.txt"), ("All files", "*.*")],
            title="Export Chat History",
            initialfile=f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        )
        if not file_path:
            return

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(f"# Codex AI Chat Export\n")
                f.write(f"- Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"- Model: {self.model_var.get()}\n")
                f.write(f"- Base URL: {self.base_url_entry.get()}\n\n---\n\n")

                for msg in self.conversation_history:
                    role = msg.get("role", "user")
                    content = msg.get("content", "")
                    if role == "user":
                        f.write(f"### 👤 User\n{content}\n\n")
                    elif role == "assistant":
                        f.write(f"### 🤖 Assistant ({self.model_var.get()})\n{content}\n\n")
                    elif role == "system":
                        f.write(f"> **System Prompt:** {content}\n\n")

            messagebox.showinfo("Export Successful", f"Conversation saved to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Export Failed", f"Could not write file: {e}")

    def _update_msg_counter(self):
        count = len(self.conversation_history)
        self.msg_count_lbl.configure(text=f"{count} message{'s' if count != 1 else ''}")

    # ------------------ CONTEXT MENU ------------------
    def _show_context_menu(self, event):
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def _copy_selected_text(self):
        try:
            selected = self.chat_text.get(tk.SEL_FIRST, tk.SEL_LAST)
            self._copy_to_clipboard(selected)
        except tk.TclError:
            pass

    def _select_all_chat(self):
        self.chat_text.tag_add(tk.SEL, "1.0", tk.END)
        self.chat_text.mark_set(tk.INSERT, "1.0")
        self.chat_text.see(tk.INSERT)


def main():
    root = tk.Tk()
    app = ChatbotApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
