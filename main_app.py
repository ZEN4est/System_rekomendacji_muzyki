import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
from settings_window import open_settings_window
from search import show_search_screen

def open_main_window(user, session, sp):
    root = tk.Tk()
    root.title("Główna aplikacja")
    root.geometry("900x500")
    root.configure(bg="#003d2f")

    def handle_logout():
        from login import create_login_window
        root.destroy()
        create_login_window()

    # ---------------- Sidebar ----------------
    sidebar = tk.Frame(root, bg="#004635", width=200)
    sidebar.pack(side="left", fill="y")

    # Profil + nazwa użytkownika
    profile_icon = tk.Canvas(sidebar, width=60, height=60, bg="#004635", highlightthickness=0)
    profile_icon.create_oval(5, 5, 55, 55, fill="white")
    profile_icon.create_text(30, 30, text="👤", font=("Segoe UI", 20), fill="#004635")
    profile_icon.pack(pady=(20, 5))

    username_label = tk.Label(sidebar, text=user.username, fg="white", bg="#004635", font=("Segoe UI", 12, "bold"))
    username_label.pack(pady=(0, 30))

    # Menu boczne
    menu_items = ["Home", "Search", "Playlists", "Favourites", "Discover"]
    implemented_items = ['Home', 'Search']
    for item in menu_items:
        lbl = tk.Label(sidebar, text=item, fg="#9ae0b2" if item in implemented_items else "white",
                       bg="#004635", font=("Segoe UI", 12), anchor="w", padx=20)
        lbl.pack(fill="x", pady=5)

        if item == "Home":
            lbl.bind("<Button-1>", lambda e: show_home_screen())
        elif item == "Search":
            lbl.bind("<Button-1>", lambda e: show_search_screen(content_frame, sp))

    # Przycisk wylogowania
    logout_button = tk.Button(sidebar, text="🔓 Wyloguj się", command=handle_logout,
                            bg="#004635", fg="white", relief="flat", font=("Segoe UI", 12))
    logout_button.pack(side="bottom", pady=(10, 5))
    # Ikonka ustawień (lewy dolny róg)
    gear_icon = tk.Label(sidebar, text="⚙️", bg="#004635", fg="white", font=("Segoe UI", 16))
    gear_icon.pack(side="bottom", pady=20)


    def show_home_screen():
        for widget in content_frame.winfo_children():
            widget.destroy()

        home_icon = tk.Label(content_frame, text="🏠", font=("Segoe UI", 100), bg="#003d2f", fg="#3fbf7f")
        home_icon.pack(pady=(60, 10))

        welcome_text = tk.Label(content_frame, text="Welcome", font=("Segoe UI", 20), fg="#3fbf7f", bg="#003d2f")
        welcome_text.pack()

    # ---------------- Main content ----------------
    content_frame = tk.Frame(root, bg="#003d2f")
    content_frame.pack(expand=True, fill="both")
    gear_icon.bind("<Button-1>", lambda e: open_settings_window(content_frame, user, session))

    show_home_screen()

    root.mainloop()
