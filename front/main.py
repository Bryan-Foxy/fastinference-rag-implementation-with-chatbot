import tkinter as tk
from interface import RAGInterface

if __name__ == "__main__":
    root = tk.Tk()
    app = RAGInterface(root)
    root.mainloop()