from http import server
import tkinter as tk
from spotify_api import search_tracks

def show_search_screen(content_frame, sp):
    bg, fg = "#003d2f", "#3fbf7f"
    for widget in content_frame.winfo_children():
        widget.destroy()

    label_frame = tk.Frame(content_frame, bg=bg)
    label_frame.pack(pady=(0, 10))

    search_icon = tk.Label(label_frame, text="🔍", font=("Segoe UI", 100), bg=bg, fg=fg)
    search_icon.pack(pady=(60, 10), side=tk.LEFT)

    search_text = tk.Label(label_frame, text="Search", font=("Segoe UI", 20, "bold"), fg=fg, bg=bg)
    search_text.pack(side=tk.LEFT, pady=(60, 10))

    main_frame = tk.Frame(content_frame, bg=bg)
    main_frame.pack(pady=(10, 0))

    search_box_frame = tk.Frame(main_frame, bg=bg)
    search_box_frame.pack(pady=(0, 10))

    search_entry = tk.Entry(search_box_frame, font=("Segoe UI", 12))
    search_entry.pack(side=tk.LEFT)

    search_results_frame = tk.Frame(main_frame, bg=bg)
    search_results_frame.pack()

    favorites = set()

    def toggle_from_favorites(track, label):
        if track['id'] in favorites:
            label.config(fg=fg)
            favorites.remove(track['id'])
        else:
            favorites.add(track['id'])
            label.config(fg="white")

    def search():
        query = search_entry.get().strip()
        if query:
            tracks = search_tracks(sp, query)
            for widget in search_results_frame.winfo_children():
                widget.destroy()

            for track in tracks:
                track_frame = tk.Frame(search_results_frame, bg=bg)
                track_frame.pack(pady=(10, 0))
                txt = track['name'] + ' - ' + ', '.join(a['name'] for a in track['artists'])
                tk.Label(track_frame, fg=fg, bg=bg, text=txt, font=("Segoe UI", 12)).pack(padx=(0, 5), side=tk.LEFT)
                favorite_lbl = tk.Label(track_frame, fg=fg, bg=bg, text='♥', font=("Segoe UI", 12, 'bold'))
                if track['id'] in favorites:
                    favorite_lbl.config(fg='white')
                favorite_lbl.pack(padx=(0, 5), side=tk.LEFT)
                favorite_lbl.bind("<Button-1>", lambda e, t=track, l=favorite_lbl: toggle_from_favorites(t, l))


    search_button = tk.Button(search_box_frame, text="Search", font=("Segoe UI", 12, "bold"),
                              relief="flat", padx=20, pady=10, command=search)
    search_button.pack(side=tk.LEFT, padx=(30, 0))

