import os
import threading
import tkinter as tk
from tkinter import ttk, messagebox

import requests


GEMINI_API_URL = (
    "https://generativelanguage.googleapis.com/v1beta/"
    "models/gemini-3.1-flash-lite:generateContent"
)

LANGUAGES = {
    "English": "English",
    "Urdu": "Urdu",
    "Arabic": "Arabic",
    "Hindi": "Hindi",
    "French": "French",
    "German": "German",
    "Spanish": "Spanish",
    "Chinese": "Chinese",
    "Italian": "Italian",
    "Portuguese": "Portuguese",
    "Russian": "Russian",
    "Japanese": "Japanese",
    "Korean": "Korean",
    "Turkish": "Turkish",
    "Dutch": "Dutch",
    "Bengali": "Bengali",
    "Persian": "Persian",
    "Punjabi": "Punjabi",
}


class TranslationTool:
    def __init__(self, root):
        self.root = root

        self.root.title("TranslateX | AI Translation Tool")
        self.root.geometry("1100x760")
        self.root.minsize(900, 650)
        self.root.configure(bg="#0b1020")

        self.bg = "#0b1020"
        self.card = "#121a2b"
        self.card2 = "#172137"
        self.border = "#273451"
        self.white = "#f8fafc"
        self.muted = "#94a3b8"
        self.accent = "#7c3aed"
        self.accent_hover = "#8b5cf6"
        self.success = "#22c55e"
        self.danger = "#ef4444"

        self.setup_styles()
        self.build_ui()

        self.root.bind(
            "<Control-Return>",
            lambda event: self.start_translation()
        )

    # =========================================================
    # STYLES
    # =========================================================

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "Language.TCombobox",
            fieldbackground=self.card2,
            background=self.card2,
            foreground=self.white,
            bordercolor=self.border,
            arrowcolor=self.white,
            padding=10,
        )

        style.map(
            "Language.TCombobox",
            fieldbackground=[("readonly", self.card2)],
            foreground=[("readonly", self.white)],
        )

    # =========================================================
    # UI
    # =========================================================

    def build_ui(self):

        main = tk.Frame(self.root, bg=self.bg)
        main.pack(fill="both", expand=True)

        # -----------------------------------------------------
        # HEADER
        # -----------------------------------------------------

        header = tk.Frame(main, bg=self.bg)
        header.pack(fill="x", padx=55, pady=(28, 12))

        logo = tk.Frame(
            header,
            bg=self.accent,
            width=44,
            height=44
        )
        logo.pack(side="left")
        logo.pack_propagate(False)

        tk.Label(
            logo,
            text="T",
            font=("Segoe UI", 20, "bold"),
            fg="white",
            bg=self.accent,
        ).place(
            relx=0.5,
            rely=0.5,
            anchor="center"
        )

        title_box = tk.Frame(header, bg=self.bg)
        title_box.pack(side="left", padx=14)

        tk.Label(
            title_box,
            text="TranslateX",
            font=("Segoe UI", 23, "bold"),
            fg=self.white,
            bg=self.bg,
        ).pack(anchor="w")

        tk.Label(
            title_box,
            text="AI-powered language translation",
            font=("Segoe UI", 10),
            fg=self.muted,
            bg=self.bg,
        ).pack(anchor="w")

        tk.Label(
            header,
            text="AI TRANSLATION TOOL",
            font=("Segoe UI", 9, "bold"),
            fg="#a78bfa",
            bg=self.bg,
        ).pack(
            side="right",
            pady=10
        )

        # -----------------------------------------------------
        # LANGUAGE BAR
        # -----------------------------------------------------

        language_card = tk.Frame(
            main,
            bg=self.card,
            highlightbackground=self.border,
            highlightthickness=1,
        )
        language_card.pack(
            fill="x",
            padx=55,
            pady=(5, 17)
        )

        language_inner = tk.Frame(
            language_card,
            bg=self.card
        )
        language_inner.pack(
            fill="x",
            padx=20,
            pady=15
        )

        # FROM

        source_box = tk.Frame(
            language_inner,
            bg=self.card
        )
        source_box.pack(
            side="left",
            fill="x",
            expand=True
        )

        tk.Label(
            source_box,
            text="FROM",
            font=("Segoe UI", 8, "bold"),
            fg=self.muted,
            bg=self.card,
        ).pack(
            anchor="w",
            pady=(0, 5)
        )

        self.source_var = tk.StringVar(
            value="English"
        )

        self.source_combo = ttk.Combobox(
            source_box,
            textvariable=self.source_var,
            values=list(LANGUAGES.keys()),
            state="readonly",
            style="Language.TCombobox",
        )
        self.source_combo.pack(fill="x")

        # SWAP

        swap_area = tk.Frame(
            language_inner,
            bg=self.card,
            width=80
        )
        swap_area.pack(
            side="left",
            padx=15
        )
        swap_area.pack_propagate(False)

        tk.Label(
            swap_area,
            text="",
            bg=self.card
        ).pack(pady=1)

        self.swap_button = tk.Button(
            swap_area,
            text="⇄",
            command=self.swap_languages,
            font=("Segoe UI", 17, "bold"),
            fg=self.white,
            bg=self.card2,
            activebackground=self.accent,
            activeforeground=self.white,
            bd=0,
            relief="flat",
            cursor="hand2",
            width=4,
        )
        self.swap_button.pack(pady=7)

        # TO

        target_box = tk.Frame(
            language_inner,
            bg=self.card
        )
        target_box.pack(
            side="left",
            fill="x",
            expand=True
        )

        tk.Label(
            target_box,
            text="TO",
            font=("Segoe UI", 8, "bold"),
            fg=self.muted,
            bg=self.card,
        ).pack(
            anchor="w",
            pady=(0, 5)
        )

        self.target_var = tk.StringVar(
            value="Urdu"
        )

        self.target_combo = ttk.Combobox(
            target_box,
            textvariable=self.target_var,
            values=list(LANGUAGES.keys()),
            state="readonly",
            style="Language.TCombobox",
        )
        self.target_combo.pack(fill="x")

        # -----------------------------------------------------
        # WORKSPACE
        # -----------------------------------------------------

        workspace = tk.Frame(
            main,
            bg=self.bg
        )
        workspace.pack(
            fill="both",
            expand=True,
            padx=55
        )

        workspace.grid_columnconfigure(
            0,
            weight=1
        )

        workspace.grid_columnconfigure(
            1,
            weight=1
        )

        workspace.grid_rowconfigure(
            1,
            weight=1
        )

        # HEADERS

        tk.Label(
            workspace,
            text="YOUR TEXT",
            font=("Segoe UI", 9, "bold"),
            fg=self.muted,
            bg=self.bg,
        ).grid(
            row=0,
            column=0,
            sticky="w",
            pady=(0, 7)
        )

        tk.Label(
            workspace,
            text="TRANSLATION",
            font=("Segoe UI", 9, "bold"),
            fg=self.muted,
            bg=self.bg,
        ).grid(
            row=0,
            column=1,
            sticky="w",
            padx=(18, 0),
            pady=(0, 7)
        )

        # INPUT CARD

        input_card = tk.Frame(
            workspace,
            bg=self.card,
            highlightbackground=self.border,
            highlightthickness=1,
        )
        input_card.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=(0, 9)
        )

        # OUTPUT CARD

        output_card = tk.Frame(
            workspace,
            bg=self.card,
            highlightbackground=self.border,
            highlightthickness=1,
        )
        output_card.grid(
            row=1,
            column=1,
            sticky="nsew",
            padx=(9, 0)
        )

        # INPUT

        self.input_text = tk.Text(
            input_card,
            height=7,
            wrap="word",
            font=("Segoe UI", 12),
            bg=self.card,
            fg=self.white,
            insertbackground=self.white,
            selectbackground=self.accent,
            selectforeground=self.white,
            relief="flat",
            bd=0,
            padx=18,
            pady=15,
            undo=True,
        )
        self.input_text.pack(
            fill="both",
            expand=True
        )

        self.input_text.insert(
            "1.0",
            "Type or paste your text here..."
        )

        self.input_text.configure(
            fg="#64748b"
        )

        self.input_text.bind(
            "<FocusIn>",
            self.remove_placeholder
        )

        self.input_text.bind(
            "<FocusOut>",
            self.restore_placeholder
        )

        # OUTPUT

        self.output_text = tk.Text(
            output_card,
            height=7,
            wrap="word",
            font=("Segoe UI", 12),
            bg=self.card,
            fg=self.white,
            insertbackground=self.white,
            selectbackground=self.accent,
            selectforeground=self.white,
            relief="flat",
            bd=0,
            padx=18,
            pady=15,
            state="disabled",
        )

        self.output_text.pack(
            fill="both",
            expand=True
        )

        # -----------------------------------------------------
        # ACTION BUTTONS
        # EXACTLY BELOW TEXT BOXES
        # -----------------------------------------------------

        actions = tk.Frame(
            workspace,
            bg=self.bg
        )

        actions.grid(
            row=2,
            column=0,
            columnspan=2,
            sticky="ew",
            pady=(11, 0)
        )

        actions.grid_columnconfigure(
            1,
            weight=1
        )

        self.clear_button = tk.Button(
            actions,
            text="Clear",
            command=self.clear_all,
            font=("Segoe UI", 10, "bold"),
            fg=self.white,
            bg=self.card2,
            activebackground=self.border,
            activeforeground=self.white,
            bd=0,
            relief="flat",
            cursor="hand2",
            padx=22,
            pady=10,
        )

        self.clear_button.grid(
            row=0,
            column=0,
            sticky="w"
        )

        # MAIN TRANSLATE BUTTON

        self.translate_button = tk.Button(
            actions,
            text="TRANSLATE",
            command=self.start_translation,
            font=("Segoe UI", 11, "bold"),
            fg="white",
            bg=self.accent,
            activebackground=self.accent_hover,
            activeforeground="white",
            bd=0,
            relief="flat",
            cursor="hand2",
            padx=55,
            pady=11,
        )

        self.translate_button.grid(
            row=0,
            column=1
        )

        self.copy_button = tk.Button(
            actions,
            text="Copy Result",
            command=self.copy_result,
            font=("Segoe UI", 10, "bold"),
            fg=self.white,
            bg=self.card2,
            activebackground=self.border,
            activeforeground=self.white,
            bd=0,
            relief="flat",
            cursor="hand2",
            padx=22,
            pady=10,
        )

        self.copy_button.grid(
            row=0,
            column=2,
            sticky="e"
        )

        # -----------------------------------------------------
        # STATUS
        # -----------------------------------------------------

        status_area = tk.Frame(
            main,
            bg=self.bg
        )

        status_area.pack(
            fill="x",
            padx=55,
            pady=(10, 8)
        )

        self.status_label = tk.Label(
            status_area,
            text="Ready to translate",
            font=("Segoe UI", 9),
            fg=self.muted,
            bg=self.bg,
        )

        self.status_label.pack(
            side="left"
        )

        tk.Label(
            status_area,
            text="Powered by Gemini 3.1 Flash-Lite",
            font=("Segoe UI", 9),
            fg="#64748b",
            bg=self.bg,
        ).pack(
            side="right"
        )

        # -----------------------------------------------------
        # FOOTER
        # -----------------------------------------------------

        footer = tk.Frame(
            main,
            bg="#080d19",
            height=38
        )

        footer.pack(
            fill="x",
            side="bottom"
        )

        footer.pack_propagate(False)

        tk.Label(
            footer,
            text="TranslateX",
            font=("Segoe UI", 9, "bold"),
            fg="#a78bfa",
            bg="#080d19",
        ).pack(
            side="left",
            padx=55,
            pady=10
        )

        tk.Label(
            footer,
            text="AI-powered translation",
            font=("Segoe UI", 8),
            fg="#64748b",
            bg="#080d19",
        ).pack(
            side="right",
            padx=55,
            pady=10
        )

    # =========================================================
    # PLACEHOLDER
    # =========================================================

    def remove_placeholder(self, event=None):

        current = self.input_text.get(
            "1.0",
            "end-1c"
        )

        if current == "Type or paste your text here...":

            self.input_text.delete(
                "1.0",
                "end"
            )

            self.input_text.configure(
                fg=self.white
            )

    def restore_placeholder(self, event=None):

        current = self.input_text.get(
            "1.0",
            "end-1c"
        ).strip()

        if not current:

            self.input_text.delete(
                "1.0",
                "end"
            )

            self.input_text.insert(
                "1.0",
                "Type or paste your text here..."
            )

            self.input_text.configure(
                fg="#64748b"
            )

    # =========================================================
    # SWAP
    # =========================================================

    def swap_languages(self):

        source = self.source_var.get()
        target = self.target_var.get()

        self.source_var.set(target)
        self.target_var.set(source)

        input_value = self.input_text.get(
            "1.0",
            "end-1c"
        )

        if input_value == "Type or paste your text here...":
            input_value = ""

        output_value = self.get_output_text()

        self.input_text.delete(
            "1.0",
            "end"
        )

        if output_value:
            self.input_text.insert(
                "1.0",
                output_value
            )
            self.input_text.configure(
                fg=self.white
            )
        else:
            self.input_text.insert(
                "1.0",
                "Type or paste your text here..."
            )
            self.input_text.configure(
                fg="#64748b"
            )

        self.set_output_text(
            input_value
        )

    # =========================================================
    # OUTPUT HELPERS
    # =========================================================

    def get_output_text(self):

        self.output_text.configure(
            state="normal"
        )

        text = self.output_text.get(
            "1.0",
            "end-1c"
        )

        self.output_text.configure(
            state="disabled"
        )

        return text

    def set_output_text(self, text):

        self.output_text.configure(
            state="normal"
        )

        self.output_text.delete(
            "1.0",
            "end"
        )

        self.output_text.insert(
            "1.0",
            text
        )

        self.output_text.configure(
            state="disabled"
        )

    # =========================================================
    # CLEAR
    # =========================================================

    def clear_all(self):

        self.input_text.delete(
            "1.0",
            "end"
        )

        self.input_text.insert(
            "1.0",
            "Type or paste your text here..."
        )

        self.input_text.configure(
            fg="#64748b"
        )

        self.set_output_text("")

        self.status_label.configure(
            text="Ready to translate",
            fg=self.muted
        )

    # =========================================================
    # COPY
    # =========================================================

    def copy_result(self):

        result = self.get_output_text().strip()

        if not result:

            messagebox.showinfo(
                "Nothing to Copy",
                "There is no translated text to copy."
            )

            return

        self.root.clipboard_clear()
        self.root.clipboard_append(result)
        self.root.update()

        self.status_label.configure(
            text="Translation copied to clipboard",
            fg=self.success
        )

    # =========================================================
    # TRANSLATE
    # =========================================================

    def start_translation(self):

        text = self.input_text.get(
            "1.0",
            "end-1c"
        ).strip()

        if text == "Type or paste your text here...":
            text = ""

        if not text:

            messagebox.showwarning(
                "Text Required",
                "Please enter some text to translate."
            )

            return

        source = self.source_var.get()
        target = self.target_var.get()

        if source == target:

            self.set_output_text(text)

            self.status_label.configure(
                text="Source and target languages are the same",
                fg=self.muted
            )

            return

        api_key = os.getenv(
            "GEMINI_API_KEY"
        )

        if not api_key:

            messagebox.showerror(
                "API Key Missing",
                "GEMINI_API_KEY was not found.\n\n"
                "Please set your Gemini API key and restart the application."
            )

            return

        self.translate_button.configure(
            text="TRANSLATING...",
            state="disabled"
        )

        self.status_label.configure(
            text="Gemini is translating...",
            fg="#a78bfa"
        )

        self.set_output_text("")

        thread = threading.Thread(
            target=self.translate_worker,
            args=(
                text,
                LANGUAGES[source],
                LANGUAGES[target],
                api_key,
            ),
            daemon=True
        )

        thread.start()

    # =========================================================
    # GEMINI API
    # =========================================================

    def translate_worker(
        self,
        text,
        source_language,
        target_language,
        api_key
    ):

        try:

            prompt = f"""
You are a professional translation engine.

Translate the following text from {source_language} to {target_language}.

Important rules:
1. Return ONLY the translated text.
2. Do not explain anything.
3. Do not add quotation marks.
4. Preserve the original meaning and tone.
5. Preserve paragraph breaks where possible.
6. Do not censor normal language.
7. Do not add notes, labels, or comments.

Text to translate:
{text}
"""

            headers = {
                "x-goog-api-key": api_key,
                "Content-Type": "application/json",
            }

            data = {
                "contents": [
                    {
                        "parts": [
                            {
                                "text": prompt
                            }
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.1,
                    "maxOutputTokens": 4096,
                }
            }

            response = requests.post(
                GEMINI_API_URL,
                headers=headers,
                json=data,
                timeout=45
            )

            response.raise_for_status()

            result = response.json()

            candidates = result.get(
                "candidates",
                []
            )

            if not candidates:

                raise Exception(
                    "Gemini returned no translation."
                )

            parts = (
                candidates[0]
                .get("content", {})
                .get("parts", [])
            )

            translated_text = ""

            for part in parts:

                if "text" in part:

                    translated_text += part["text"]

            translated_text = translated_text.strip()

            if not translated_text:

                raise Exception(
                    "Gemini returned an empty translation."
                )

            self.root.after(
                0,
                lambda: self.translation_success(
                    translated_text
                )
            )

        except requests.exceptions.Timeout:

            self.root.after(
                0,
                lambda: self.translation_error(
                    "The Gemini request timed out. Please try again."
                )
            )

        except requests.exceptions.ConnectionError:

            self.root.after(
                0,
                lambda: self.translation_error(
                    "Unable to connect to Gemini. "
                    "Please check your internet connection."
                )
            )

        except requests.exceptions.HTTPError as error:

            error_message = "Gemini API request failed."

            try:

                error_data = response.json()

                error_message = (
                    error_data
                    .get("error", {})
                    .get("message", error_message)
                )

            except Exception:
                pass

            self.root.after(
                0,
                lambda: self.translation_error(
                    error_message
                )
            )

        except Exception as error:

            self.root.after(
                0,
                lambda: self.translation_error(
                    str(error)
                )
            )

    # =========================================================
    # RESULT
    # =========================================================

    def translation_success(self, result):

        self.set_output_text(
            result
        )

        self.status_label.configure(
            text="Translation completed successfully",
            fg=self.success
        )

        self.translate_button.configure(
            text="TRANSLATE",
            state="normal"
        )

    def translation_error(self, message):

        self.status_label.configure(
            text="Translation failed",
            fg=self.danger
        )

        self.translate_button.configure(
            text="TRANSLATE",
            state="normal"
        )

        messagebox.showerror(
            "Translation Error",
            message
        )


# =============================================================
# APPLICATION START
# =============================================================

if __name__ == "__main__":

    root = tk.Tk()

    app = TranslationTool(root)

    root.mainloop()