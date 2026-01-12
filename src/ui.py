def mostrar_popup(linhas: list[str]) -> None:
    import tkinter as tk
    from tkinter import messagebox

    root = tk.Tk()
    root.withdraw()
    messagebox.showwarning("🚨 Alertas da Frota", "\n".join(linhas))
    root.destroy()
