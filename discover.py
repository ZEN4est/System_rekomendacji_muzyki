import tkinter as tk
from spotify_api import search_tracks_with_filters, get_tracks_genre
from sqlalchemy.orm import Session
from model.models import User
from model.crud import get_playlists_by_user, add_song_if_not_exists, add_song_to_playlist
from music_recommender import recommend_query_attributes_graph, fetch_playlist_details
from model.crud import get_songs_in_playlist, get_genres_for_song, get_artists_for_song



def show_discover_screen(content_frame, session: Session, user: User, sp):
    # kolory / fonty
    bg, fg = "#003d2f", "#3fbf7f"
    form_bg = "#b3ffdc"
    input_bg = "#005740"
    input_fg = "white"
    selected_bg = "#3fbf7f"
    font_title = ("Segoe UI", 24, "bold")
    font_icon = ("Segoe UI", 48)
    font_label = ("Segoe UI", 12)
    pad = 20

    # wyczyść poprzednie widżety
    for w in content_frame.winfo_children():
        w.destroy()

    # znajdź playlistę „favorites”
    user_playlists = get_playlists_by_user(session, User.user_id)
    fav = {p.name: p for p in user_playlists}["favorites"]

    # Header
    header = tk.Frame(content_frame, bg=bg)
    header.pack(fill="x", pady=(20,10))
    tk.Frame(header, bg=bg).pack(side="left", expand=True)
    tk.Label(header, text="👁️", font=font_icon, bg=bg, fg=fg).pack(side="left")
    tk.Label(header, text="Discover", font=font_title, bg=bg, fg=fg).pack(side="left")
    tk.Frame(header, bg=bg).pack(side="left", expand=True)

    # Layout: spotify results | filter panel
    main = tk.Frame(content_frame, bg=bg)
    main.pack(fill="both", expand=True)
    main.grid_columnconfigure(0, weight=2)   # results
    main.grid_columnconfigure(1, weight=0)   # filter
    main.grid_columnconfigure(2, weight=1)

    # Spotify search results (left of filter)
    spotify_results = tk.Frame(main, bg=bg)
    spotify_results.grid(row=0, column=0, sticky="nsew", padx=(pad, pad//2), pady=pad)

    # Filter panel (to the right of results)
    filter_panel = tk.Frame(main, bg=form_bg)
    filter_panel.grid(row=0, column=1, sticky="n", pady=pad, padx=pad)

    # Vars for toggles
    artist_var = tk.BooleanVar(value=False)
    decade_var = tk.BooleanVar(value=False)
    genre_var = tk.BooleanVar(value=False)
    language_var = tk.BooleanVar(value=False)
    use_fav_var = tk.BooleanVar(value=False)

    # Toggle buttons in filter_panel
    btns = [
        ("Choose artist", artist_var),
        ("Choose decade", decade_var),
        ("Choose genre", genre_var),
        ("Choose language", language_var),
    ]
    for text, var in btns:
        b = tk.Button(filter_panel, text=text, font=font_label,
                      bg=input_bg, fg=input_fg, relief="raised", width=20)
        def make_cmd(v, button, bt=text):
            def cmd():
                new = not v.get()
                v.set(new)
                button.config(bg=selected_bg if new else input_bg)
            return cmd
        b.config(command=make_cmd(var, b))
        b.pack(pady=5, ipady=6)

    # Use favourites checkbox
    tk.Checkbutton(filter_panel, text="Use favourites", variable=use_fav_var,
                   font=font_label, bg=form_bg, fg=bg,
                   selectcolor=form_bg, activebackground=form_bg).pack(pady=(10,20))

    # Hardcoded playlist details example
    playlist_details_example = [
        {"song_id": "1", "title": "Imagine", "decade": 1970, "language": "English", "genres": ["Rock"], "artists": ["John Lennon"]},
        {"song_id": "3", "title": "Hello",   "decade": 2010, "language": "English", "genres": ["Pop"],  "artists": ["Adele"]}
    ]

    def clear_spotify_results():
        for w in spotify_results.winfo_children():
            w.destroy()

    def get_spotify_track_frame(parent: tk.Frame, idx: int, track: dict) -> tk.Frame:
        # styling from favorites.py
        bg = '#003d2f'
        song_color = '#3CE7A7'
        artist_color = '#2AB481'
        icon_color = '#156748'
        icon_hover = '#44FFB9'

        outer_width = parent.winfo_width()
        entry_font = ('Segoe UI', max(12, outer_width // 50))
        icon_font = ('Segoe UI', max(16, outer_width // 30), 'bold')
        row_height = entry_font[1] * 2 + 10

        frame = tk.Frame(parent, bg=bg, height=row_height)
        frame.grid_columnconfigure(1, weight=1)

        lbl_idx = tk.Label(frame, text=f'{idx+1}.', bg=bg, fg=song_color, font=entry_font)
        lbl_idx.grid(row=0, column=0, sticky='nw', padx=(10,5))

        info = tk.Frame(frame, bg=bg)
        info.grid(row=0, column=1, sticky='nsew')
        tk.Label(info, text=track['name'], bg=bg, fg=song_color, font=entry_font).pack(anchor='w')
        artist_text = ', '.join(a['name'] for a in track['artists'])
        tk.Label(info, text=artist_text, bg=bg, fg=artist_color, font=entry_font).pack(anchor='w')

        lbl_icon = tk.Label(frame, text='♥', bg=bg, fg=icon_color, font=icon_font)
        lbl_icon.grid(row=0, column=2, sticky='ne', padx=(5,10))
        lbl_icon.bind('<Enter>', lambda e: lbl_icon.config(fg=icon_hover))
        lbl_icon.bind('<Leave>', lambda e: lbl_icon.config(fg=icon_color))

        return frame

    def on_filter():
        # Determine playlist details source
        if use_fav_var.get():
            # fetch from database
            playlist_details = fetch_playlist_details(session, fav.playlist_id)
        else:
            # use hardcoded example
            playlist_details = playlist_details_example

        # get recommended attributes
        attrs = recommend_query_attributes_graph(playlist_details)
        artist = attrs.get('artist') if artist_var.get() else None
        genre = attrs.get('genre')   if genre_var.get()  else None
        decade = attrs.get('decade') if decade_var.get()  else None
        language = attrs.get('language') if language_var.get() else None
        use_fav = use_fav_var.get()
        tracks = search_tracks_with_filters(
            sp,
            artist=artist,
            genre=genre,
            decade=decade,
            language=language,
            use_favourites=use_fav
        )
        # display up to 5
        clear_spotify_results()
        for idx, track in enumerate(tracks[:5]):
            frame = get_spotify_track_frame(spotify_results, idx, track)
            frame.pack(fill='x', pady=5)
        clear_spotify_results()
        for idx, track in enumerate(tracks[:5]):
            frame = get_spotify_track_frame(spotify_results, idx, track)
            frame.pack(fill='x', pady=5)

    # Filter button
    filter_button = tk.Button(filter_panel, text="Filter", font=font_label,
                              bg=input_bg, fg=input_fg, relief="flat",
                              width=20, command=on_filter)
    filter_button.pack(pady=(0,20), ipady=6)

    # initial empty state
    clear_spotify_results()
