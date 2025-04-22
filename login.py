import tkinter as tk
from tkinter import ttk
import tkinter.font as tkFont



def create_login_window():
    closed_manually = False

    def handle_login():
        # Placeholder for login functionality
        pass

    def handle_register():
        # Placeholder for register functionality
        pass

    def on_window_close(root):
        nonlocal closed_manually
        closed_manually = True
        root.destroy()

    # Create the main application window
    root = tk.Tk()
    root.title("Login/Register")
    root.geometry("400x350")
    root.resizable(False, False)
    label_font = tkFont.Font(family="Segoe UI", size=12, weight="bold")
    other_font = tkFont.Font(family="Segoe UI", size=12)


    root.protocol("WM_DELETE_WINDOW", lambda: on_window_close(root))

    # Create the tab control
    notebook = ttk.Notebook(root)

    # Create frames for Login and Register tabs
    login_frame = ttk.Frame(notebook)
    register_frame = ttk.Frame(notebook)

    notebook.add(login_frame, text="Logowanie")
    notebook.add(register_frame, text="Rejestracja")
    notebook.pack(expand=True, fill="both")

    # ------------------ Login Tab ------------------
    ttk.Label(login_frame, text="Nazwa użytkownika:", font=label_font).pack(pady=(20, 5))
    login_username_entry = ttk.Entry(login_frame)
    login_username_entry.pack()

    ttk.Label(login_frame, text="Hasło:", font=label_font).pack(pady=(10, 5))
    login_password_entry = ttk.Entry(login_frame, show="*")
    login_password_entry.pack()

    ttk.Button(login_frame, text="Zaloguj się", command=root.destroy).pack(pady=20)

    # ------------------ Register Tab ------------------
    ttk.Label(register_frame, text="Nazwa użytkownika:", font=label_font).pack(pady=(20, 5))
    register_username_entry = ttk.Entry(register_frame)
    register_username_entry.pack()

    ttk.Label(register_frame, text="E-mail:", font=label_font).pack(pady=(10, 5))
    register_email_entry = ttk.Entry(register_frame)
    register_email_entry.pack()

    ttk.Label(register_frame, text="Hasło:", font=label_font).pack(pady=(10, 5))
    register_password_entry = ttk.Entry(register_frame, show="*")
    register_password_entry.pack()

    ttk.Button(register_frame, text="Zarejestruj się", command=root.destroy).pack(pady=20)

    # Run the app
    root.mainloop()
    return closed_manually