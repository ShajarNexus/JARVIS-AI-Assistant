
import customtkinter as ctk
from tkinter import messagebox

from app.memory import (
    get_all_personal_facts,
    update_personal_fact,
    forget_personal_fact
)


class MemoryManagerWindow(ctk.CTkToplevel):

    def __init__(self, parent):

        super().__init__(parent)

        self.parent = parent
        self.selected_memory = None

        self.title("JARVIS | Memory Manager")
        self.geometry("750x600")
        self.minsize(650, 500)

        self.configure(fg_color="#101827")

        self.create_interface()
        self.load_memories()

        self.transient(parent)

    # ======================================
    # CREATE INTERFACE
    # ======================================

    def create_interface(self):

        header = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        header.pack(
            fill="x",
            padx=25,
            pady=(20, 10)
        )

        ctk.CTkLabel(
            header,
            text="PERSONAL MEMORY MANAGER",
            font=("Arial", 22, "bold"),
            text_color="#22D3EE"
        ).pack(anchor="w")

        ctk.CTkLabel(
            header,
            text="View, update, and forget information JARVIS remembers.",
            font=("Arial", 12),
            text_color="#94A3B8"
        ).pack(anchor="w", pady=5)

        self.content = ctk.CTkFrame(
            self,
            fg_color="#172235",
            corner_radius=15
        )

        self.content.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=10
        )

        ctk.CTkLabel(
            self.content,
            text="SAVED MEMORIES",
            font=("Arial", 13, "bold"),
            text_color="#E2E8F0"
        ).pack(
            anchor="w",
            padx=15,
            pady=(15, 8)
        )

        self.memory_list = ctk.CTkScrollableFrame(
            self.content,
            fg_color="#101827",
            height=200
        )

        self.memory_list.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=5
        )

        # Edit section

        self.edit_frame = ctk.CTkFrame(
            self.content,
            fg_color="transparent"
        )

        self.edit_frame.pack(
            fill="x",
            padx=15,
            pady=15
        )

        ctk.CTkLabel(
            self.edit_frame,
            text="EDIT SELECTED MEMORY",
            font=("Arial", 13, "bold"),
            text_color="#22D3EE"
        ).pack(anchor="w", pady=(0, 10))

        ctk.CTkLabel(
            self.edit_frame,
            text="Category",
            text_color="#CBD5E1"
        ).pack(anchor="w")

        self.category_entry = ctk.CTkEntry(
            self.edit_frame,
            placeholder_text="Example: learning"
        )

        self.category_entry.pack(
            fill="x",
            pady=5
        )

        ctk.CTkLabel(
            self.edit_frame,
            text="Memory / Fact",
            text_color="#CBD5E1"
        ).pack(anchor="w")

        self.fact_entry = ctk.CTkEntry(
            self.edit_frame,
            placeholder_text="Enter memory"
        )

        self.fact_entry.pack(
            fill="x",
            pady=5
        )

        # Action buttons

        buttons = ctk.CTkFrame(
            self.content,
            fg_color="transparent"
        )

        buttons.pack(
            fill="x",
            padx=15,
            pady=(5, 15)
        )

        ctk.CTkButton(
            buttons,
            text="Update Memory",
            fg_color="#087FAD",
            hover_color="#075E85",
            command=self.update_selected_memory
        ).pack(
            side="left",
            expand=True,
            fill="x",
            padx=4
        )

        ctk.CTkButton(
            buttons,
            text="Forget Memory",
            fg_color="#8C293B",
            hover_color="#641D2C",
            command=self.delete_selected_memory
        ).pack(
            side="left",
            expand=True,
            fill="x",
            padx=4
        )

        ctk.CTkButton(
            buttons,
            text="Refresh",
            fg_color="#334155",
            hover_color="#475569",
            command=self.load_memories
        ).pack(
            side="left",
            expand=True,
            fill="x",
            padx=4
        )

    # ======================================
    # LOAD MEMORIES
    # ======================================

    def load_memories(self):

        for widget in self.memory_list.winfo_children():
            widget.destroy()

        self.selected_memory = None

        self.category_entry.delete(0, "end")
        self.fact_entry.delete(0, "end")

        memories = get_all_personal_facts()

        if not memories:

            ctk.CTkLabel(
                self.memory_list,
                text="No saved memories yet.",
                text_color="#94A3B8"
            ).pack(pady=20)

            return

        for memory in memories:

            category = memory["category"]
            fact = memory["fact"]

            ctk.CTkButton(
                self.memory_list,
                text=f"{category.upper()}\n{fact}",
                anchor="w",
                height=55,
                fg_color="#1E293B",
                hover_color="#334155",
                text_color="#E2E8F0",
                command=lambda item=memory:
                    self.select_memory(item)
            ).pack(
                fill="x",
                padx=5,
                pady=4
            )

    # ======================================
    # SELECT MEMORY
    # ======================================

    def select_memory(self, memory):

        self.selected_memory = memory

        self.category_entry.delete(0, "end")
        self.category_entry.insert(0, memory["category"])

        self.fact_entry.delete(0, "end")
        self.fact_entry.insert(0, memory["fact"])

    # ======================================
    # UPDATE MEMORY
    # ======================================

    def update_selected_memory(self):

        if not self.selected_memory:

            messagebox.showwarning(
                "Select Memory",
                "Please select a memory first.",
                parent=self
            )

            return

        category = self.category_entry.get().strip()
        fact = self.fact_entry.get().strip()

        if not category or not fact:

            messagebox.showwarning(
                "Missing Information",
                "Category and memory cannot be empty.",
                parent=self
            )

            return

        success = update_personal_fact(
            self.selected_memory["id"],
            category,
            fact
        )

        if success:

            messagebox.showinfo(
                "Success",
                "Memory updated successfully.",
                parent=self
            )

            self.load_memories()

        else:

            messagebox.showerror(
                "Update Failed",
                "Memory could not be updated. Check for duplicate entries.",
                parent=self
            )

    # ======================================
    # DELETE MEMORY
    # ======================================

    def delete_selected_memory(self):

        if not self.selected_memory:

            messagebox.showwarning(
                "Select Memory",
                "Please select a memory first.",
                parent=self
            )

            return

        confirm = messagebox.askyesno(
            "Forget Memory",
            "Are you sure you want JARVIS to forget this information?",
            parent=self
        )

        if not confirm:
            return

        forget_personal_fact(
            self.selected_memory["id"]
        )

        messagebox.showinfo(
            "Success",
            "Memory deleted successfully.",
            parent=self
        )

        self.load_memories()
