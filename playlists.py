from cProfile import label
import tkinter as tk
from tkinter import ttk
from model.models import Playlist, Song, SongArtist, PlaylistSong, User
from sqlalchemy.orm import Session
from model.crud import get_genres_for_song, get_playlists_by_user, get_songs_in_playlist, \
                       get_artists_for_song, create_song, add_song_to_playlist, add_song_if_not_exists, \
                       get_songs_in_playlist, remove_song_from_playlist

def get_favorites_set(session: Session, favorites: Playlist) -> set[str]:
    songs: list[Song] = get_songs_in_playlist(session, favorites.playlist_id)
    a = set()
    for s in songs:
        a.add(s.song_id)
    return a


def get_song_in_playlist_frame(outer_frame: tk.Frame, session: Session, idx, h, song: Song, favorites_set: set[str], favorites_id: int) -> tk.Frame:
    bg = '#003d2f'
    song_color = '#3CE7A7'
    artist_color = '#2AB481'
    icon_bright = '#44FFB9'
    icon_dark = '#156748'
    playlist_active = icon_bright
    playlist_inactive = 'grey'
    closure_toggle_remove = True
    entry_font = ('Segoe UI', 12)
    song_icon_font = ('Segoe UI', 20)

    title = song.title
    artists = get_artists_for_song(session, song.song_id)

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
    artist_text = ', '.join([x.artist for x in artists])
    artist_label = tk.Label(song_info_frame, bg=bg, fg=artist_color, text=artist_text, font=entry_font)
    artist_label.pack(side='top', anchor='w')

    # --- Column 2: Buttons ---
    # This frame also fills its cell vertically.
    button_frame = tk.Frame(frame, bg=bg)
    button_frame.grid(row=0, column=2, sticky='ns') # Fills North, South

    # ❤️ ❌
    add_label = tk.Label(button_frame, bg=bg, fg=icon_bright if song.song_id in favorites_set else icon_dark, text='♥', font=song_icon_font)
    remove_label = tk.Label(button_frame, bg=bg, fg=icon_bright, text='x', font=song_icon_font)

    # To vertically center the buttons, we pack an expanding empty frame (a spacer)
    # above and below them. This pushes them to the middle.
    remove_label.pack(side='right')
    add_label.pack(side='right')

    # --- Bindings ---
    def toggle_add(_event):
        if song.song_id not in favorites_set:
            add_song_to_playlist(session, favorites_id, song.song_id)
            add_label.config(fg=icon_bright)
            favorites_set.add(song.song_id)
        else:
            remove_song_from_playlist(session, favorites_id, song.song_id)
            add_label.config(fg=icon_dark)
            favorites_set.remove(song.song_id)

    add_label.bind('<Button-1>', toggle_add)

    def toggle_remove(_event):
        nonlocal closure_toggle_remove
        closure_toggle_remove = not closure_toggle_remove
        remove_label.config(fg=icon_bright if closure_toggle_remove else icon_dark)

    remove_label.bind('<Button-1>', toggle_remove)

    return frame

def show_playlists_screen(main_frame: tk.Frame, user: User, session: Session):
    # background color, main color, dimmed main color
    bg = '#003d2f'
    song_color = '#3CE7A7'
    icon_bright = '#44FFB9'
    icon_dark = '#156748'

    pad_small = 10
    pad_big = 60
    icon_big_font = ("Segoe UI", 100)
    label_big_font = ("Segoe UI", 20, 'bold')
    empty_font = ("Segoe UI", 20)

    user_playlists = get_playlists_by_user(session, User.user_id)
    playlist_dict = {str(p.name): p for p in user_playlists}
    favorites = playlist_dict['favorites']
    favorites_set = get_favorites_set(session, favorites)

    for widget in main_frame.winfo_children():
        widget.destroy()

    sidebar = tk.Frame(main_frame, bg=bg, width=200)
    sidebar.pack(side="left", fill="y")

    content_frame = tk.Frame(main_frame, bg=bg)
    content_frame.pack(expand=True, fill='both')

    width = 2 * main_frame.winfo_width()
    height = int(840 * (1440 / content_frame.winfo_height()))
    list_height = height // 14

    label_frame = tk.Frame(content_frame, bg=bg)
    label_frame.pack(pady=(0, pad_small))

    playlist_icon = tk.Label(label_frame, text='🔖', font=icon_big_font, bg=bg, fg=icon_dark)
    playlist_icon.pack(pady=(pad_big, pad_small), side=tk.LEFT)

    p_text = tk.Label(label_frame, text='Playlists', font=label_big_font, fg='#3fbf7f', bg=bg)
    p_text.pack(side=tk.LEFT, pady=(pad_big, pad_small))

    user_playlists = get_playlists_by_user(session, User.user_id)
    playlist_dict = {str(p.name): p for p in user_playlists}
    favorites = playlist_dict['favorites']
    favorites_set = get_favorites_set(session, favorites)

    # --- Main layout setup ---
    playlist_list_frame = tk.Frame(content_frame, bg=bg, width=width, height=height)
    playlist_list_frame.pack()
    playlist_list_frame.pack_propagate(False)

    songs = get_songs_in_playlist(session, favorites.playlist_id)
    for i, song in enumerate(get_songs_in_playlist(session, favorites.playlist_id)):
        entry_frame = get_song_in_playlist_frame(
            playlist_list_frame,
            session,
            idx=i,
            h=40, # Set a fixed height for each song entry
            song=song,
            favorites_set=favorites_set,
            favorites_id=favorites.playlist_id
        )
        entry_frame.pack_propagate(False)
        entry_frame.pack(side=tk.TOP, pady=(0, pad_small), fill='x')

