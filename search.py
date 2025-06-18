import tkinter as tk
from spotify_api import search_tracks, get_tracks_genre
from sqlalchemy.orm import Session
from model.models import User, Playlist, Song
from model.crud import add_song_to_playlist, get_playlists_by_user, add_song_if_not_exists, remove_song_from_playlist
from playlists import get_favorites_dict


def get_song_in_search_frame(outer_frame: tk.Frame, session: Session,idx, h, 
                             track_id: str, favorites_id: int, favorites_set: set[str],
                             title='Title', artists=['Artist1', 'Artist2'],
                             language='english', genres=['Prog rock'], decade=2020, 
                             ) -> tk.Frame:
    bg = '#003B2B'
    song_color = '#3CE7A7'
    artist_color = '#2AB481'
    icon_bright = '#44FFB9'
    icon_dark = '#156748'
    playlist_active = icon_bright
    playlist_inactive = 'grey'
    entry_font = ('Segoe UI', 12)
    song_icon_font = ('Segoe UI', 20)

    pad_small = 5
    # The main container for one song entry. It has a fixed height.
    frame = tk.Frame(outer_frame, bg=bg, height=h)

    # --- Main Grid Layout (3 columns) ---
    # Column 1 (Song Info) will expand to fill empty space.
    frame.grid_columnconfigure(1, weight=1)
    # The main row should use all the vertical space given to it.
    frame.grid_rowconfigure(0, weight=1)

    # --- Column 0: Index Label ---
    # Sticks to the top-left corner.
    index_label = tk.Label(frame, bg=bg, fg=song_color, text=f'{idx + 1}.', font=entry_font)
    index_label.grid(row=0, column=0, sticky='nw', padx=(0, pad_small))

    # --- Column 1: Song Info ---
    # This frame fills the entire cell. We use .pack() inside it for simple alignment.
    song_info_frame = tk.Frame(frame, bg=bg)
    song_info_frame.grid(row=0, column=1, sticky='nsew') # Fills North, South, East, West

    # Pinning the title to the TOP of the frame ensures it aligns with the index.
    title_label = tk.Label(song_info_frame, bg=bg, fg=song_color, text=title, font=entry_font)
    title_label.pack(side='top', anchor='w')

    # Pinning the artist to the BOTTOM of the frame.
    artist_label = tk.Label(song_info_frame, bg=bg, fg=artist_color, text=', '.join(artists), font=entry_font)
    artist_label.pack(side='top', anchor='w')

    # --- Column 2: Buttons ---
    # This frame also fills its cell vertically.
    button_frame = tk.Frame(frame, bg=bg)
    button_frame.grid(row=0, column=2, sticky='ns') # Fills North, South

    # ❤️ ❌
    add_label = tk.Label(button_frame, bg=bg, fg=icon_bright if track_id in favorites_set else icon_dark, text='♥', font=song_icon_font)
    add_label.pack(side='right')

    # --- Binding ---
    def toggle_from_favorites(_event):
        song=add_song_if_not_exists(session, track_id, title, language, decade, artists, genres)
        if track_id not in favorites_set:
            add_song_to_playlist(session, favorites_id, song.song_id)
            add_label.config(fg=icon_bright)
        else:
            remove_song_from_playlist(session, favorites_id, song.song_id)
            add_label.config(fg=icon_dark)
    add_label.bind('<Button-1>', toggle_from_favorites)

    return frame


def show_search_screen(content_frame, session: Session, user: User, sp):
    pad_small = 5
    bg, fg = "#003d2f", "#3fbf7f"
    for widget in content_frame.winfo_children():
        widget.destroy()

    user_playlists = get_playlists_by_user(session, User.user_id)
    playlist_dict = {str(p.name): p for p in user_playlists}
    favorites = playlist_dict['favorites']

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

    favorites_dict = get_favorites_dict(session, favorites)
    def search():
        query = search_entry.get().strip()
        if query:
            tracks = search_tracks(sp, query)
            for widget in search_results_frame.winfo_children():
                widget.destroy()

            for idx, track in enumerate(tracks):
                track_frame = get_song_in_search_frame(
                        search_results_frame, session, idx=idx, h=40, 
                        track_id=track['id'],
                        title=track['name'],
                        artists=list(map(lambda a: a['name'], track['artists'])),
                        genres=list(get_tracks_genre(sp, track)),
                        decade= int(track['album']['release_date'].split('-')[0]) // 10 * 10,
                        favorites_id=favorites.playlist_id,
                        favorites_set = get_favorites_dict(session, favorites)
                )
                track_frame.pack_propagate(False)
                track_frame.pack(side=tk.TOP, pady=(0, pad_small), fill='x')


    search_button = tk.Button(search_box_frame, text="Search", font=("Segoe UI", 12, "bold"),
                              relief="flat", padx=20, pady=10, command=search)
    search_button.pack(side=tk.LEFT, padx=(30, 0))
