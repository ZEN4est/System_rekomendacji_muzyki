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

    def save_changes():
        fname = name_entry.get().strip()
        lname = last_entry.get().strip()
        p1 = new_pass.get()
        p2 = repeat_pass.get()

        if p1 != p2:
            messagebox.showerror("Error", "Passwords do not match.")
            return

        if not fname or not lname:
            messagebox.showerror("Error", "Name and Lastname cannot be empty.")
            return

        from model.crud import update_user_data  # Import lokalny dla bezpieczeństwa cykli

        # Jeśli hasło jest podane, zaktualizuj też je
        result = update_user_data(session, user.user_id, first_name=fname, last_name=lname, password=p1 if p1 else None)

        if result:
            messagebox.showinfo("Success", "Account updated.")
            # Aktualizuj obiekt użytkownika lokalnie
            user.first_name = fname
            user.last_name = lname
            if p1:
                user.password = p1
        else:
            messagebox.showerror("Error", "Something went wrong while updating.")

    tk.Button(content_frame, text="Save", command=save_changes, bg="white", padx=20).pack()


    def delete_account():
        confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete your account?")
        if confirm:
            from model.crud import delete_user
            success = delete_user(session, user.user_id)
            if success:
                messagebox.showinfo("Deleted", "Account has been deleted.")
                content_frame.winfo_toplevel().destroy()
            else:
                messagebox.showerror("Error", "Account could not be deleted.")

    tk.Button(content_frame, text="Delete account", bg="red", fg="white", command=delete_account).pack(pady=20)