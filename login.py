import tkinter as tk
from tkinter import ttk, messagebox
import tkinter.font as tkFont
from user import User
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
from sqlalchemy import create_engine
from main_app import open_main_window

load_dotenv()

DATABASE_URL = os.getenv("POSTGRESQL_URL")
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

def create_login_window():
    def switch_frame(target):
        login_frame.pack_forget()
        register_frame.pack_forget()
        if target == "login":
            login_frame.pack(expand=True)
        else:
            register_frame.pack(expand=True)

    def handle_login():
        username = login_username_entry.get().strip()
        password = login_password_entry.get().strip()
        user = session.query(User).filter_by(username=username, password=password).first()
        if user:
            root.destroy()
            open_main_window(user,session)
        else:
            messagebox.showerror("Błąd", "Nieprawidłowy login lub hasło.")

    def handle_register():
        first_name = register_first_name_entry.get().strip()
        last_name = register_last_name_entry.get().strip()
        username = register_username_entry.get().strip()
        email = register_email_entry.get().strip()
        password = register_password_entry.get().strip()

        if not all([first_name, last_name, username, email, password]):
            messagebox.showerror("Błąd", "Wszystkie pola są wymagane.")
            return

        new_user = User(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email,
            password=password
        )
        try:
            session.add(new_user)
            session.commit()
            messagebox.showinfo("Sukces", "Zarejestrowano pomyślnie! Teraz możesz się zalogować.")
            switch_frame("login")
        except Exception as e:
            session.rollback()
            messagebox.showerror("Błąd przy rejestracji", str(e))

    root = tk.Tk()
    root.title("Logowanie / Rejestracja")
    root.geometry("500x500")
    root.configure(bg="#003d2f")

    # Styl przycisków przełączających
    tab_frame = tk.Frame(root, bg="#003d2f")
    tab_frame.pack(pady=(10, 0))

    login_tab_btn = tk.Button(tab_frame, text="Logowanie", font=("Segoe UI", 12, "bold"), bg="#004635", fg="white",
                              relief="flat", padx=20, pady=5, command=lambda: switch_frame("login"))
    login_tab_btn.grid(row=0, column=0, padx=5)

    register_tab_btn = tk.Button(tab_frame, text="Rejestracja", font=("Segoe UI", 12, "bold"), bg="#004635", fg="white",
                                 relief="flat", padx=20, pady=5, command=lambda: switch_frame("register"))
    register_tab_btn.grid(row=0, column=1, padx=5)

    # ------------------ Login Frame ------------------
    login_frame = tk.Frame(root, bg="#003d2f")
    login_frame.pack(expand=True)

    tk.Label(login_frame, text="Nazwa użytkownika", bg="#003d2f", fg="#3fbf7f", font=("Segoe UI", 12)).pack(pady=(40, 5))
    login_username_entry = tk.Entry(login_frame, font=("Segoe UI", 12))
    login_username_entry.pack()

    tk.Label(login_frame, text="Hasło", bg="#003d2f", fg="#3fbf7f", font=("Segoe UI", 12)).pack(pady=(20, 5))
    login_password_entry = tk.Entry(login_frame, show="*", font=("Segoe UI", 12))
    login_password_entry.pack()

    tk.Button(login_frame, text="Zaloguj się", command=handle_login,
              bg="white", fg="#003d2f", font=("Segoe UI", 12), padx=20, pady=5).pack(pady=40)

    # ------------------ Register Frame ------------------
    register_frame = tk.Frame(root, bg="#003d2f")

    tk.Label(register_frame, text="Imię", bg="#003d2f", fg="#3fbf7f", font=("Segoe UI", 12)).pack(pady=(20, 5))
    register_first_name_entry = tk.Entry(register_frame, font=("Segoe UI", 12))
    register_first_name_entry.pack()

    tk.Label(register_frame, text="Nazwisko", bg="#003d2f", fg="#3fbf7f", font=("Segoe UI", 12)).pack(pady=(10, 5))
    register_last_name_entry = tk.Entry(register_frame, font=("Segoe UI", 12))
    register_last_name_entry.pack()

    tk.Label(register_frame, text="Nazwa użytkownika", bg="#003d2f", fg="#3fbf7f", font=("Segoe UI", 12)).pack(pady=(10, 5))
    register_username_entry = tk.Entry(register_frame, font=("Segoe UI", 12))
    register_username_entry.pack()

    tk.Label(register_frame, text="E-mail", bg="#003d2f", fg="#3fbf7f", font=("Segoe UI", 12)).pack(pady=(10, 5))
    register_email_entry = tk.Entry(register_frame, font=("Segoe UI", 12))
    register_email_entry.pack()

    tk.Label(register_frame, text="Hasło", bg="#003d2f", fg="#3fbf7f", font=("Segoe UI", 12)).pack(pady=(10, 5))
    register_password_entry = tk.Entry(register_frame, show="*", font=("Segoe UI", 12))
    register_password_entry.pack()

    tk.Button(register_frame, text="Zarejestruj się", command=handle_register,
              bg="white", fg="#003d2f", font=("Segoe UI", 12), padx=20, pady=5).pack(pady=30)

    root.mainloop()
