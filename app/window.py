
import customtkinter as ctk
import threading

from tkinter import messagebox

from app import theme
from app.orb import JarvisOrb
from app.ai_engine import ask_jarvis
from app.voice_engine import jarvis_voice
from app.automation import JarvisAutomation

from app.memory import (
    start_new_conversation,
    get_all_conversations,
    get_conversation_history,
    store_message,
    update_chat_title,
    detect_personal_memory,
    remove_conversation
)

from app.memory_window import MemoryManagerWindow


class JarvisWindow(ctk.CTk):

    def __init__(self):

        super().__init__()

        self.title("JARVIS | AI Desktop Assistant")
        self.geometry("1250x800")
        self.minsize(1050, 700)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.configure(fg_color=theme.BG)

        self.listening = False
        self.is_generating = False

        self.conversation_number = 1
        self.current_conversation_id = None

        # PC automation engine
        self.automation = JarvisAutomation()

        self.create_sidebar()
        self.create_main_area()

        self.load_latest_conversation()

    # ==========================================
    # SIDEBAR
    # ==========================================

    def create_sidebar(self):

        self.sidebar = ctk.CTkFrame(
            self,
            width=245,
            corner_radius=0,
            fg_color=theme.SIDEBAR
        )

        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        ctk.CTkLabel(
            self.sidebar,
            text="J.A.R.V.I.S",
            font=("Arial", 27, "bold"),
            text_color=theme.ACCENT
        ).pack(pady=(30, 5))

        ctk.CTkLabel(
            self.sidebar,
            text="PERSONAL AI ASSISTANT",
            font=("Arial", 10, "bold"),
            text_color=theme.MUTED
        ).pack(pady=(0, 35))

        ctk.CTkButton(
            self.sidebar,
            text="+  New Conversation",
            height=42,
            corner_radius=10,
            fg_color=theme.ACCENT_DARK,
            hover_color="#075E85",
            font=("Arial", 13, "bold"),
            command=self.new_conversation
        ).pack(padx=15, fill="x", pady=5)

        ctk.CTkLabel(
            self.sidebar,
            text="RECENT CONVERSATIONS",
            text_color=theme.MUTED,
            font=("Arial", 11, "bold")
        ).pack(anchor="w", padx=20, pady=(35, 12))

        self.history = ctk.CTkScrollableFrame(
            self.sidebar,
            fg_color="transparent"
        )

        self.history.pack(fill="both", expand=True, padx=5)

        ctk.CTkFrame(
            self.sidebar,
            height=1,
            fg_color="#24364B"
        ).pack(fill="x", padx=15, pady=10)

        ctk.CTkButton(
            self.sidebar,
            text="🧠  Manage Memories",
            height=40,
            anchor="w",
            fg_color="transparent",
            hover_color=theme.PANEL,
            text_color=theme.TEXT,
            command=self.open_memory_manager
        ).pack(fill="x", padx=15, pady=(0, 15))

    # ==========================================
    # MAIN DASHBOARD
    # ==========================================

    def create_main_area(self):

        self.main = ctk.CTkFrame(
            self,
            fg_color=theme.BG,
            corner_radius=0
        )

        self.main.pack(
            side="left",
            fill="both",
            expand=True,
            padx=22,
            pady=15
        )

        self.create_header()
        self.create_orb_section()
        self.create_chat_section()
        self.create_input_section()

    # ==========================================
    # HEADER
    # ==========================================

    def create_header(self):

        header = ctk.CTkFrame(
            self.main,
            fg_color="transparent"
        )

        header.pack(fill="x", pady=(5, 15))

        ctk.CTkLabel(
            header,
            text="JARVIS CONTROL CENTER",
            font=("Arial", 20, "bold"),
            text_color=theme.TEXT
        ).pack(side="left")

        self.system_status = ctk.CTkLabel(
            header,
            text="● SYSTEM ONLINE",
            font=("Arial", 12, "bold"),
            text_color=theme.SUCCESS
        )

        self.system_status.pack(side="right")

    # ==========================================
    # JARVIS ORB
    # ==========================================

    def create_orb_section(self):

        orb_frame = ctk.CTkFrame(
            self.main,
            fg_color=theme.PANEL,
            corner_radius=20
        )

        orb_frame.pack(fill="x", pady=(0, 15))

        self.orb = JarvisOrb(orb_frame)
        self.orb.pack(pady=(10, 0))

        ctk.CTkLabel(
            orb_frame,
            text="J.A.R.V.I.S",
            font=("Arial", 23, "bold"),
            text_color=theme.ACCENT
        ).pack(pady=(0, 5))

        self.orb_status = ctk.CTkLabel(
            orb_frame,
            text="SYSTEM IDLE",
            font=("Arial", 11, "bold"),
            text_color=theme.MUTED
        )

        self.orb_status.pack(pady=(0, 15))

    # ==========================================
    # CHAT SECTION
    # ==========================================

    def create_chat_section(self):

        ctk.CTkLabel(
            self.main,
            text="CONVERSATION",
            font=("Arial", 12, "bold"),
            text_color=theme.MUTED
        ).pack(anchor="w", pady=(5, 8))

        self.chat = ctk.CTkScrollableFrame(
            self.main,
            fg_color=theme.PANEL,
            corner_radius=15
        )

        self.chat.pack(fill="both", expand=True, pady=(0, 10))

    # ==========================================
    # MESSAGE INPUT
    # ==========================================

    def create_input_section(self):

        input_frame = ctk.CTkFrame(
            self.main,
            fg_color="transparent"
        )

        input_frame.pack(fill="x", pady=(0, 5))

        self.entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="Type a message to JARVIS...",
            height=48,
            font=("Arial", 14),
            corner_radius=12,
            border_color=theme.ACCENT_DARK,
            fg_color=theme.PANEL,
            text_color=theme.TEXT
        )

        self.entry.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0, 8)
        )

        self.entry.bind(
            "<Return>",
            lambda event: self.send_message()
        )

        self.send_button = ctk.CTkButton(
            input_frame,
            text="Send",
            width=85,
            height=48,
            corner_radius=12,
            fg_color=theme.ACCENT_DARK,
            hover_color="#075E85",
            command=self.send_message
        )

        self.send_button.pack(side="left", padx=4)

        self.mic_button = ctk.CTkButton(
            input_frame,
            text="🎙 Start Listening",
            width=155,
            height=48,
            corner_radius=12,
            fg_color="#164C64",
            hover_color="#087FAD",
            command=self.toggle_listening
        )

        self.mic_button.pack(side="left", padx=(4, 0))

    # ==========================================
    # DISPLAY MESSAGES
    # ==========================================

    def add_message(self, sender, message):

        color = (
            theme.USER_BUBBLE
            if sender == "YOU"
            else theme.AI_BUBBLE
        )

        bubble = ctk.CTkFrame(
            self.chat,
            fg_color=color,
            corner_radius=12
        )

        bubble.pack(fill="x", padx=12, pady=6)

        ctk.CTkLabel(
            bubble,
            text=sender,
            font=("Arial", 11, "bold"),
            text_color=theme.ACCENT
        ).pack(anchor="w", padx=12, pady=(8, 2))

        ctk.CTkLabel(
            bubble,
            text=message,
            font=("Arial", 13),
            text_color=theme.TEXT,
            wraplength=650,
            justify="left"
        ).pack(anchor="w", padx=12, pady=(2, 10))

        self.chat._parent_canvas.yview_moveto(1.0)

    # ==========================================
    # REFRESH CONVERSATION LIST
    # ==========================================

    def refresh_history(self):

        for widget in self.history.winfo_children():
            widget.destroy()

        conversations = get_all_conversations()

        if not conversations:

            ctk.CTkLabel(
                self.history,
                text="No conversations yet.",
                text_color=theme.MUTED
            ).pack(pady=15)

            return

        for conversation in conversations:

            conversation_id = conversation["id"]
            title = conversation["title"]

            if len(title) > 21:
                title = title[:21] + "..."

            row = ctk.CTkFrame(
                self.history,
                fg_color="transparent"
            )

            row.pack(fill="x", padx=3, pady=3)

            ctk.CTkButton(
                row,
                text="•  " + title,
                anchor="w",
                height=35,
                fg_color=(
                    theme.PANEL
                    if conversation_id == self.current_conversation_id
                    else "transparent"
                ),
                hover_color=theme.PANEL,
                text_color=theme.TEXT,
                font=("Arial", 11),
                command=lambda cid=conversation_id:
                    self.load_conversation(cid)
            ).pack(side="left", fill="x", expand=True, padx=(0, 3))

            ctk.CTkButton(
                row,
                text="✕",
                width=30,
                height=35,
                fg_color="transparent",
                hover_color="#8C293B",
                text_color="#F87171",
                font=("Arial", 12, "bold"),
                command=lambda cid=conversation_id:
                    self.delete_chat(cid)
            ).pack(side="right")

    # ==========================================
    # DELETE CONVERSATION
    # ==========================================

    def delete_chat(self, conversation_id):

        if self.is_generating:

            messagebox.showwarning(
                "JARVIS Busy",
                "Please wait until JARVIS finishes its response.",
                parent=self
            )

            return

        confirm = messagebox.askyesno(
            "Delete Conversation",
            "Are you sure you want to delete this conversation?\n\n"
            "All messages inside this conversation will also be deleted.",
            parent=self
        )

        if not confirm:
            return

        remove_conversation(conversation_id)

        if conversation_id == self.current_conversation_id:

            self.current_conversation_id = None
            self.new_conversation()

        else:

            self.refresh_history()

    # ==========================================
    # LOAD LATEST CONVERSATION
    # ==========================================

    def load_latest_conversation(self):

        conversations = get_all_conversations()

        if conversations:

            latest_id = conversations[0]["id"]
            self.load_conversation(latest_id)

        else:

            self.new_conversation()

    # ==========================================
    # LOAD SELECTED CONVERSATION
    # ==========================================

    def load_conversation(self, conversation_id):

        if self.is_generating:
            return

        self.current_conversation_id = conversation_id

        for widget in self.chat.winfo_children():
            widget.destroy()

        messages = get_conversation_history(
            conversation_id,
            limit=1000
        )

        if not messages:

            self.add_message(
                "JARVIS",
                "Hello! I am JARVIS. How can I help you?"
            )

        else:

            for message in messages:

                sender = (
                    "YOU"
                    if message["role"] == "user"
                    else "JARVIS"
                )

                self.add_message(sender, message["content"])

        self.refresh_history()

    # ==========================================
    # SEND MESSAGE
    # ==========================================

    def send_message(self):

        message = self.entry.get().strip()

        if not message or self.is_generating:
            return

        if self.current_conversation_id is None:
            return

        conversation_id = self.current_conversation_id

        self.add_message("YOU", message)
        self.entry.delete(0, "end")

        detect_personal_memory(message)

        previous_messages = get_conversation_history(
            conversation_id,
            limit=1
        )

        if not previous_messages:

            update_chat_title(
                conversation_id,
                message[:35]
            )

            self.refresh_history()

        self.is_generating = True

        self.send_button.configure(
            state="disabled",
            text="Thinking..."
        )

        self.entry.configure(state="disabled")

        self.orb.set_state("thinking")

        self.orb_status.configure(
            text="JARVIS IS THINKING...",
            text_color="#A855F7"
        )

        threading.Thread(
            target=self.process_user_request,
            args=(message, conversation_id),
            daemon=True
        ).start()

    # ==========================================
    # UNDERSTAND USER REQUEST
    # ==========================================

    def process_user_request(self, message, conversation_id):

        try:

            # First check whether the user wants PC automation.
            plan = self.automation.understand_request(message)

            actions = plan.get("actions", [])

            if actions:

                # Ask for confirmation on the main GUI thread.
                self.after(
                    0,
                    lambda: self.confirm_automation(
                        message,
                        plan,
                        conversation_id
                    )
                )

                return

            # If no PC action was identified, use normal JARVIS AI.
            answer = ask_jarvis(
                message,
                conversation_id
            )

        except Exception as error:

            answer = (
                "Sorry, I encountered an error.\n\n"
                f"Error: {error}"
            )

        self.after(
            0,
            lambda: self.display_ai_response(
                message,
                answer,
                conversation_id
            )
        )

    # ==========================================
    # ASK USER FOR AUTOMATION CONFIRMATION
    # ==========================================

    def confirm_automation(
        self,
        user_message,
        plan,
        conversation_id
    ):

        actions = plan.get("actions", [])

        action_list = "\n".join(
            f"{number}. {self.automation.describe_action(action)}"
            for number, action in enumerate(actions, start=1)
        )

        confirmation_text = (
            "JARVIS wants to perform the following actions:\n\n"
            f"{action_list}\n\n"
            "Do you want to allow these actions?"
        )

        approved = messagebox.askyesno(
            "JARVIS - Action Confirmation",
            confirmation_text,
            parent=self
        )

        if not approved:

            answer = (
                "Okay! I will not perform those actions. "
                "Your PC has not been changed."
            )

            self.display_ai_response(
                user_message,
                answer,
                conversation_id
            )

            return

        # Execute approved actions in a background thread.
        self.orb_status.configure(
            text="EXECUTING APPROVED ACTIONS...",
            text_color=theme.ACCENT
        )

        threading.Thread(
            target=self.execute_automation,
            args=(user_message, plan, conversation_id),
            daemon=True
        ).start()

    # ==========================================
    # EXECUTE APPROVED AUTOMATION
    # ==========================================

    def execute_automation(
        self,
        user_message,
        plan,
        conversation_id
    ):

        try:

            results = self.automation.execute_plan(plan)

            answer = "\n".join(
                f"• {result}" for result in results
            )

        except Exception as error:

            answer = (
                "I encountered a problem while performing "
                f"the approved actions:\n{error}"
            )

        self.after(
            0,
            lambda: self.display_ai_response(
                user_message,
                answer,
                conversation_id
            )
        )

    # ==========================================
    # DISPLAY AI RESPONSE
    # ==========================================

    def display_ai_response(
        self,
        user_message,
        answer,
        conversation_id
    ):

        store_message(
            conversation_id,
            "user",
            user_message
        )

        store_message(
            conversation_id,
            "assistant",
            answer
        )

        if conversation_id == self.current_conversation_id:

            self.add_message("JARVIS", answer)

        # Speak the response using Kokoro.
        jarvis_voice.speak(answer)

        self.is_generating = False

        self.send_button.configure(
            state="normal",
            text="Send"
        )

        self.entry.configure(state="normal")
        self.entry.focus()

        self.refresh_history()

        if self.listening:

            self.orb.set_state("listening")

            self.orb_status.configure(
                text="LISTENING MODE (MIC NOT CONNECTED)",
                text_color=theme.ACCENT
            )

        else:

            self.orb.set_state("idle")

            self.orb_status.configure(
                text="SYSTEM IDLE",
                text_color=theme.MUTED
            )

    # ==========================================
    # NEW CONVERSATION
    # ==========================================

    def new_conversation(self):

        if self.is_generating:
            return

        self.conversation_number += 1

        conversation_id = start_new_conversation(
            f"Conversation {self.conversation_number}"
        )

        self.current_conversation_id = conversation_id

        for widget in self.chat.winfo_children():
            widget.destroy()

        self.add_message(
            "JARVIS",
            "New conversation started. How can I help you?"
        )

        self.refresh_history()

    # ==========================================
    # OPEN MEMORY MANAGER
    # ==========================================

    def open_memory_manager(self):

        MemoryManagerWindow(self)

    # ==========================================
    # MICROPHONE STATUS
    # ==========================================

    def toggle_listening(self):

        self.listening = not self.listening

        if self.listening:

            self.orb.set_state("listening")

            self.orb_status.configure(
                text="LISTENING MODE (MIC NOT CONNECTED)",
                text_color=theme.ACCENT
            )

            self.mic_button.configure(
                text="■ Stop Listening",
                fg_color="#8C293B",
                hover_color="#641D2C"
            )

        else:

            if not self.is_generating:

                self.orb.set_state("idle")

                self.orb_status.configure(
                    text="SYSTEM IDLE",
                    text_color=theme.MUTED
                )

            self.mic_button.configure(
                text="🎙 Start Listening",
                fg_color="#164C64",
                hover_color="#087FAD"
            )
