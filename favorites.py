from cProfile import label
import tkinter as tk
from tkinter import ttk
from model.crud import get_favorites_by_user_id, get_songs_in_playlist, remove_song_from_playlist
from model.models import Playlist, Song, User
from sqlalchemy.orm import Session

def get_song_in_favorites_frame(outer_frame: tk.Frame, session: Session, idx: int, h: int,
                                song: Song, favorites_id: int) -> tk.Frame:
    bg = '#003d2f'
    song_color = '#3CE7A7'
    artist_color = '#2AB481'
    icon_bright = '#44FFB9'
    icon_dark = '#156748'

    artists = song.artists
    title = song.title

    outer_width = outer_frame.winfo_width()
    pad_small=outer_width // 100
    entry_font = ('Segoe UI', outer_width // 50)
    song_icon_font = ('Segoe UI', outer_width // 15, 'bold')

    frame = tk.Frame(outer_frame, bg=bg, height=h, width=outer_width)

    frame.grid_columnconfigure(1, weight=1)
    frame.grid_rowconfigure(0, weight=1)

    # ---- Index    ----
    index_label = tk.Label(frame, bg=bg, fg=song_color, text=f'{idx+1}.', font=entry_font)
    index_label.grid(row=0, column=0, sticky='nw', padx=(0, pad_small))

    # ---- Song Info ----
    song_info_frame = tk.Frame(frame, bg=bg)
    song_info_frame.grid(row=0, column=1, sticky='nsew') # Fills North, South, East, West

    title_label = tk.Label(song_info_frame, bg=bg, fg=song_color, text=title, font=entry_font)
    title_label.pack(side='top', anchor='w')

    artist_text = ', '.join([x.artist for x in artists])
    artist_label = tk.Label(song_info_frame, bg=bg, fg=artist_color, text=artist_text, font=entry_font)
    artist_label.pack(side='top', anchor='w')

    # --- Button ----
    remove_label = tk.Label(frame, bg=bg, fg=icon_dark, text = '❌', font=song_icon_font)
    remove_label.grid(row=0, column=2, sticky='nse')

    def remove(_event):
        remove_song_from_playlist(session, favorites_id, song.song_id)
        frame.destroy()

    def on_enter(e):
        e.widget['foreground'] = icon_bright
    
    def on_leave(e):
        e.widget['foreground'] = icon_dark

    remove_label.bind('<Button-1>', remove)
    remove_label.bind('<Enter>', on_enter)
    remove_label.bind('<Leave>', on_leave)

    return frame

def show_favorites_screen(content_frame: tk.Frame, session: Session, user: User):
    for widget in content_frame.winfo_children():
        widget.destroy()


    favorites = get_favorites_by_user_id(session, user.user_id)
    if favorites is None:
        raise Exception("User has no 'favorites' playlist")

    bg = '#003d2f'
    song_color = '#3CE7A7'
    icon_bright = '#44FFB9'
    icon_dark = '#156748'

    pad_small = 10
    pad_big = 60
    icon_big_font = ("Segoe UI", 100)
    label_big_font = ("Segoe UI", 20, 'bold')
    empty_font = ("Segoe UI", 20)

    width = 2 * content_frame.winfo_width() // 5
    height = int(840 * (1440 / content_frame.winfo_height()))
    list_height = height // 14
    label_frame = tk.Frame(content_frame, bg=bg)
    label_frame.pack(pady=(0, 10))

    heart_icon = tk.Label(label_frame, text='♥', font=icon_big_font, bg=bg, fg=icon_dark)
    heart_icon.pack(pady=(pad_big, pad_small), side=tk.LEFT)

    heart_text = tk.Label(label_frame, text='Favorites', font=label_big_font, fg=icon_bright, bg=bg)
    heart_text.pack(side=tk.LEFT, pady=(pad_big, pad_small))

    favorites_list_frame = tk.Frame(content_frame, bg=bg, width=width, height=height)
    favorites_list_frame.pack()
    favorites_list_frame.pack_propagate(False)

    songs = get_songs_in_playlist(session, favorites.playlist_id)
    if len(songs) == 0:
        empty_label = tk.Label(favorites_list_frame, text='Empty...', font=empty_font, fg=song_color, bg=bg)
        empty_label.pack(pady=(pad_big, 0), side=tk.TOP)
    for idx, song in enumerate(songs):
        track_frame = get_song_in_favorites_frame(
            outer_frame=favorites_list_frame, session=session, idx=idx, h=list_height,
            song=song, favorites_id=favorites.playlist_id
        )
        track_frame.pack_propagate(False)
        track_frame.pack(side=tk.TOP, pady=(0, pad_small // 2), fill='x')


