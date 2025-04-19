"""
RAG Chatbot Interface using Tkinter
-----------------------------------
This GUI provides an interface for a Retrieval-Augmented Generation (RAG) chatbot.
Users can select a file (.pdf, .docx, .txt) or a folder containing documents to ingest.
They can then interact with the chatbot, which uses the ingested documents to answer questions.

Features:
- File/Folder loading with progress indication
- Chat display with sender-specific alignment and color
- Query handling with multithreading for responsiveness
"""

import os 
import requests
import threading
import tkinter as tk
from tkinter import filedialog, ttk, scrolledtext

API_URL = "http://127.0.0.1:5000"

class RAGInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("RAG Chatbot Interface")
        self.root.geometry("800x600")
        self.root.configure(bg="white")

        # === Top Frame: Controls ===
        control_frame = tk.Frame(self.root, bg="white")
        control_frame.pack(pady=10)

        self.source_type = tk.StringVar(value="File")
        self.option_menu = ttk.Combobox(
            control_frame, textvariable=self.source_type,
            values=["File", "Folder"], state="readonly", width=10
        )
        self.option_menu.pack(side=tk.LEFT, padx=10)

        self.load_button = tk.Button(control_frame, text="📂 Load", command=self.load_path)
        self.load_button.pack(side=tk.LEFT, padx=10)

        self.progress = ttk.Progressbar(control_frame, orient="horizontal", mode="determinate", length=200)
        self.progress.pack(side=tk.LEFT, padx=10)

        # === Middle Frame: Chat Display ===
        self.chat_frame = tk.Frame(self.root, bg="white")
        self.chat_frame.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        self.chat_display = scrolledtext.ScrolledText(
            self.chat_frame, wrap=tk.WORD, state='disabled',
            bg="white", font=("Helvetica", 14)
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True)

        # Configure tags for alignment and color
        self.chat_display.tag_config("left", justify="left", foreground="blue", spacing1=2, spacing3=4)
        self.chat_display.tag_config("right", justify="right", foreground="green", spacing1=2, spacing3=4)

        # === Bottom Frame: Prompt Input ===
        input_frame = tk.Frame(self.root, bg="white")
        input_frame.pack(pady=10, fill=tk.X)

        self.entry = tk.Entry(input_frame, font=("Helvetica", 14))
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        self.entry.bind("<Return>", self.send_query)

        self.send_button = tk.Button(input_frame, text="Send", command=self.send_query)
        self.send_button.pack(side=tk.RIGHT, padx=10)

    def load_path(self):
        choice = self.source_type.get()
        if choice == "File":
            path = filedialog.askopenfilename(
                title="Select a file",
                filetypes=[
                    ("Supported files", "*.pdf *.docx *.txt"),
                    ("PDF files", "*.pdf"),
                    ("Word files", "*.docx"),
                    ("Text files", "*.txt"),
                    ("All files", "*.*")
                ]
            )
        else:
            path = filedialog.askdirectory(title="Select a folder")

        if not path:
            return

        self.progress.start(10)
        self.add_message("📄 Loading text data ...", sender="IA")

        def thread_ingest():
            try:
                res = requests.post(f"{API_URL}/ingest", json={"path": path})
                data = res.json()
                self.add_message(
                    f"✅ Text data successfully loaded:\n📁 {os.path.basename(path)}\n📄 Documents: {data['num_docs']}",
                    sender="IA"
                )
            except Exception as e:
                self.add_message(f"❌ Error during loading: {str(e)}", sender="IA")
            finally:
                self.progress.stop()

        threading.Thread(target=thread_ingest).start()

    def send_query(self, event=None):
        query = self.entry.get().strip()
        if not query:
            return
        self.entry.delete(0, tk.END)
        self.add_message(query, sender="Me")

        def thread_query():
            try:
                res = requests.post(f"{API_URL}/ask", json={"query": query})
                data = res.json()
                self.add_message(data["answer"], sender="IA")
            except Exception as e:
                self.add_message(f"❌ Error: {str(e)}", sender="IA")

        threading.Thread(target=thread_query).start()

    def add_message(self, message, sender="IA"):
        self.chat_display.config(state='normal')
        tag = "left" if sender == "IA" else "right"
        message = message.strip()
        self.chat_display.insert(tk.END, f"{sender}: {message}\n", tag)
        self.chat_display.config(state='disabled')
        self.chat_display.yview(tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = RAGInterface(root)
    root.mainloop()