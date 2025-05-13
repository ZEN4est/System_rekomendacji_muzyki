import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os

def open_settings_window(content_frame, user, session):
    # Wyczyść content_frame
    for widget in content_frame.winfo_children():
        widget.destroy()

    # Nagłówek zębatki
    tk.Label(content_frame, text="⚙", font=("Segoe UI", 50), fg="#3fbf7f", bg="#003d2f").pack(pady=(10, 0))
    tk.Label(content_frame, text="Settings", font=("Segoe UI", 20), fg="#3fbf7f", bg="#003d2f").pack()

    # Pola edycji
    frame = tk.Frame(content_frame, bg="#003d2f")
    frame.pack(pady=30)

    # Imię
    tk.Label(frame, text="Name", bg="#003d2f", fg="#3fbf7f", font=("Segoe UI", 12)).grid(row=0, column=0, padx=10)
    name_entry = tk.Entry(frame)
    name_entry.insert(0, user.first_name)
    name_entry.grid(row=1, column=0, padx=10)

    # Nazwisko
    tk.Label(frame, text="Lastname", bg="#003d2f", fg="#3fbf7f", font=("Segoe UI", 12)).grid(row=0, column=1, padx=10)
    last_entry = tk.Entry(frame)
    last_entry.insert(0, user.last_name)
    last_entry.grid(row=1, column=1, padx=10)

    # Hasło
    tk.Label(frame, text="New password", bg="#003d2f", fg="white").grid(row=2, column=0, pady=(20, 5))
    new_pass = tk.Entry(frame, show="*")
    new_pass.grid(row=3, column=0)

    tk.Label(frame, text="Repeat password", bg="#003d2f", fg="white").grid(row=2, column=1, pady=(20, 5))
    repeat_pass = tk.Entry(frame, show="*")
    repeat_pass.grid(row=3, column=1)

    # Avatar — w przyszłości możesz go dodać tutaj
    def choose_avatar():
        pass  # zostawione na później

    tk.Button(content_frame, text="Edit avatar", command=choose_avatar, bg="white", padx=20).pack(pady=(10, 20))
    tk.Button(content_frame, text="Save", bg="white", padx=20).pack()

    def delete_account():
        confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete your account?")
        if confirm:
            # if (user, "delete"):
            print("Deleting user...")
            user.delete(session)  # <-- Musisz mieć tę metodę!
            content_frame.winfo_toplevel().destroy()

    tk.Button(content_frame, text="Delete account", bg="red", fg="white", command=delete_account).pack(pady=20)