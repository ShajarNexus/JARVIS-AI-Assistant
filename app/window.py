
import customtkinter as ctk
import threading
from tkinter import messagebox

from app import theme
from app.orb import JarvisOrb
from app.ai_engine import ask_jarvis
from app.voice_engine import jarvis_voice
from app.speech_engine import jarvis_speech
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
        self.is_closing = False

        self.awaiting_voice_confirmation = False
        self.pending_automation = None

        self.conversation_number = 1
        self.current_conversation_id = None

        self.automation = JarvisAutomation()

        jarvis_speech.on_text = self.on_speech_recognized
        jarvis_voice.on_speech_finished = self.on_voice_finished

        self.create_sidebar()
        self.create_main_area()
        self.load_latest_conversation()

        self.protocol("WM_DELETE_WINDOW", self.close_application)

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

        self.stop_button = ctk.CTkButton(
            input_frame,
            text="■ Stop Speaking",
            width=135,
            height=48,
            corner_radius=12,
            fg_color="#8C293B",
            hover_color="#641D2C",
            command=self.stop_speaking,
            state="disabled"
        )

        self.stop_button.pack(side="left", padx=(8, 0))

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

    def load_latest_conversation(self):

        conversations = get_all_conversations()

        if conversations:

            latest_id = conversations[0]["id"]
            self.load_conversation(latest_id)

        else:

            self.new_conversation()

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

    def send_message(self):

        message = self.entry.get().strip()

        if not message:
            return

        self.entry.delete(0, "end")
        self.submit_message(message)

    def on_speech_recognized(self, message):

        if self.is_closing:
            return

        try:

            self.after(
                0,
                lambda: self.handle_recognized_speech(message)
            )

        except Exception:
            pass

    def handle_recognized_speech(self, message):

        if self.is_closing:
            return

        if not self.listening:
            return

        if self.is_generating:
            return

        jarvis_speech.stop()
        self.submit_message(message)

    def submit_message(self, message):

        if not message or self.is_generating:
            return

        if self.current_conversation_id is None:
            return

        if jarvis_speech.is_listening:
            jarvis_speech.stop()

        conversation_id = self.current_conversation_id

        self.add_message("YOU", message)
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

    def process_user_request(self, message, conversation_id):

        try:

            plan = self.automation.understand_request(message)
            actions = plan.get("actions", [])

            if actions:

                self.after(
                    0,
                    lambda: self.confirm_automation(
                        message,
                        plan,
                        conversation_id
                    )
                )

                return

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
    # VOICE-BASED AUTOMATION CONFIRMATION
    # ==========================================

    def confirm_automation(
        self,
        user_message,
        plan,
        conversation_id
    ):

        actions = plan.get("actions", [])

        if not actions:

            self.display_ai_response(
                user_message,
                "I could not identify an action to perform.",
                conversation_id
            )

            return

        action_list = "; ".join(
            self.automation.describe_action(action)
            for action in actions
        )

        question = (
            f"I am ready to {action_list}. "
            "Do you want me to proceed? Please say yes or no."
        )

        self.pending_automation = (
            user_message,
            plan,
            conversation_id
        )

        self.awaiting_voice_confirmation = True

        self.orb.set_state("thinking")

        self.orb_status.configure(
            text="WAITING FOR YOUR VOICE CONFIRMATION...",
            text_color=theme.ACCENT
        )

        self.add_message("JARVIS", question)

        try:

            jarvis_voice.speak(question)
            self.stop_button.configure(state="normal")

        except Exception as error:

            print("Could not speak confirmation question:", error)

            self.awaiting_voice_confirmation = False
            self.pending_automation = None

            self.display_ai_response(
                user_message,
                "I could not ask for voice confirmation. "
                "The action was cancelled for safety.",
                conversation_id
            )

    def on_voice_confirmation_result(self, recognized_text):

        if self.is_closing:
            return

        try:

            self.after(
                0,
                lambda: self.finish_voice_confirmation(recognized_text)
            )

        except Exception:
            pass

    def finish_voice_confirmation(self, recognized_text):

        if self.is_closing or not self.awaiting_voice_confirmation:
            return

        normalized = (recognized_text or "").strip().lower()
        normalized = normalized.strip(" .,!?:;\"'")

        affirmative_answers = {
            "yes", "yeah", "yep", "ok", "okay", "sure",
            "confirm", "confirmed", "proceed", "do it"
        }

        negative_answers = {
            "no", "nope", "cancel", "stop", "don't", "dont"
        }

        pending = self.pending_automation

        self.pending_automation = None
        self.awaiting_voice_confirmation = False

        if pending is None:
            return

        user_message, plan, conversation_id = pending

        if normalized in affirmative_answers:

            self.orb_status.configure(
                text="VOICE CONFIRMATION ACCEPTED...",
                text_color=theme.SUCCESS
            )

            threading.Thread(
                target=self.execute_automation,
                args=(user_message, plan, conversation_id),
                daemon=True
            ).start()

            return

        if normalized in negative_answers:

            answer = (
                "Okay! You said no. I cancelled the requested action. "
                "Your PC has not been changed."
            )

        elif normalized:

            answer = (
                f"I heard '{recognized_text}', but it was not a clear yes or no. "
                "For safety, I cancelled the action. You can ask me again."
            )

        else:

            answer = (
                "I did not hear a clear confirmation in time. "
                "For safety, I cancelled the action. You can ask me again."
            )

        self.display_ai_response(
            user_message,
            answer,
            conversation_id
        )

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

        jarvis_voice.speak(answer)

        self.stop_button.configure(state="normal")

        self.is_generating = False

        self.send_button.configure(
            state="normal",
            text="Send"
        )

        self.entry.configure(state="normal")
        self.entry.focus()

        self.refresh_history()

        if self.listening:

            self.orb.set_state("thinking")

            self.orb_status.configure(
                text="JARVIS IS SPEAKING...",
                text_color="#A855F7"
            )

        else:

            self.orb.set_state("idle")

            self.orb_status.configure(
                text="SYSTEM IDLE",
                text_color=theme.MUTED
            )

    # ==========================================
    # STOP SPEAKING
    # ==========================================

    def stop_speaking(self):

        if self.is_closing:
            return

        try:

            jarvis_voice.stop_speaking()

            self.stop_button.configure(state="disabled")

            if self.awaiting_voice_confirmation:

                self.awaiting_voice_confirmation = False
                self.pending_automation = None

                self.orb.set_state("idle")
                self.orb_status.configure(
                    text="ACTION CANCELLED",
                    text_color=theme.MUTED
                )

                return

            if self.listening:

                self.orb_status.configure(
                    text="RESUMING LISTENING...",
                    text_color=theme.ACCENT
                )

                self.after(250, self.resume_listening)

            else:

                self.orb.set_state("idle")

                self.orb_status.configure(
                    text="SPEAKING STOPPED",
                    text_color=theme.MUTED
                )

        except Exception as error:

            print("Stop speaking error:", error)

    # ==========================================
    # KOKORO SPEECH FINISHED
    # ==========================================

    def on_voice_finished(self):

        if self.is_closing:
            return

        try:

            self.after(
                0,
                self.handle_voice_finished
            )

        except Exception:
            pass

    def handle_voice_finished(self):

        if self.is_closing:
            return

        if self.awaiting_voice_confirmation:

            self.stop_button.configure(state="disabled")

            self.orb.set_state("listening")

            self.orb_status.configure(
                text="SAY YES OR NO...",
                text_color=theme.ACCENT
            )

            try:

                jarvis_speech.start_confirmation(
                    self.on_voice_confirmation_result,
                    timeout=8
                )

            except Exception as error:

                print("Could not start voice confirmation:", error)
                self.finish_voice_confirmation(None)

            return

        self.stop_button.configure(state="disabled")

        if self.listening:

            self.resume_listening()

        elif not self.is_generating:

            self.orb.set_state("idle")

            self.orb_status.configure(
                text="SYSTEM IDLE",
                text_color=theme.MUTED
            )

    def resume_listening(self):

        if self.is_closing:
            return

        if not self.listening:
            return

        if self.is_generating:
            return

        if jarvis_speech.is_listening:
            return

        if jarvis_speech.is_confirming:
            return

        self.start_microphone()

    def start_microphone(self):

        if not self.listening:
            return

        if self.is_generating:
            return

        jarvis_speech.start()

        self.orb.set_state("listening")

        self.orb_status.configure(
            text="LISTENING... SPEAK NATURALLY",
            text_color=theme.ACCENT
        )

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

    def open_memory_manager(self):

        MemoryManagerWindow(self)

    def toggle_listening(self):

        if not self.listening:

            self.listening = True

            self.mic_button.configure(
                text="■ Stop Listening",
                fg_color="#8C293B",
                hover_color="#641D2C"
            )

            if self.is_generating:

                self.orb_status.configure(
                    text="WAITING FOR JARVIS TO FINISH...",
                    text_color=theme.ACCENT
                )

                return

            self.start_microphone()

        else:

            self.listening = False

            jarvis_speech.stop()

            self.mic_button.configure(
                text="🎙 Start Listening",
                fg_color="#164C64",
                hover_color="#087FAD"
            )

            if not self.is_generating:

                self.orb.set_state("idle")

                self.orb_status.configure(
                    text="SYSTEM IDLE",
                    text_color=theme.MUTED
                )

    def close_application(self):

        self.is_closing = True
        self.listening = False

        jarvis_speech.stop()

        try:
            jarvis_voice.stop_speaking()
        except Exception:
            pass

        self.destroy()
