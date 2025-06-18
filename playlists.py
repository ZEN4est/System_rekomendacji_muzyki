from cProfile import label
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from model.models import Playlist, Song, SongArtist, PlaylistSong, User
from sqlalchemy.orm import Session
from model.crud import delete_playlist, get_genres_for_song, get_playlists_by_user, get_songs_in_playlist, \
                       get_artists_for_song, create_song, add_song_to_playlist, add_song_if_not_exists, \
                       get_songs_in_playlist, remove_song_from_playlist, create_playlist

def get_favorites_set(session: Session, favorites: Playlist) -> set[str]:
    songs: list[Song] = get_songs_in_playlist(session, favorites.playlist_id)
    a = set()
    for s in songs:
        a.add(s.song_id)
    return a


def get_song_in_playlist_frame(outer_frame: tk.Frame, session: Session, idx, h, song: Song, 
                               favorites_set: set[str], favorites_id: int,
                               playlist_id: int) -> tk.Frame:
    bg = '#003d2f'
    song_color = '#3CE7A7'
    artist_color = '#2AB481'
    icon_bright = '#44FFB9'
    icon_dark = '#156748'
    entry_font = ('Segoe UI', 12)
    song_icon_font = ('Segoe UI', 25)

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
        remove_song_from_playlist(session, playlist_id, song.song_id)
        frame.destroy()

    remove_label.bind('<Button-1>', toggle_remove)
    def on_enter_p(e):
        e.widget['foreground'] = 'white'
    
    def on_leave_p(e):
        e.widget['foreground'] = icon_bright
    remove_label.bind('<Enter>', on_enter_p)
    remove_label.bind('<Leave>', on_leave_p)

    return frame

def show_playlists_screen(main_frame: tk.Frame, user: User, session: Session):
    bg = '#003d2f'
    song_color = '#3CE7A7'
    icon_bright = '#44FFB9'
    icon_dark = '#156748'
    dodaj = '#052718'

    pad_small = 10
    pad_big = 60
    icon_big_font = ("Segoe UI", 100)
    label_big_font = ("Segoe UI", 20, 'bold')
    empty_font = ("Segoe UI", 20)
    playlist_font = ("Segoe UI", 12)
    nowa_font = ("Segoe UI", 16)

    user_playlists = get_playlists_by_user(session, user.user_id)
    playlist_dict = {str(p.name): p for p in user_playlists}
    favorites = playlist_dict['favorites']
    favorites_set = get_favorites_set(session, favorites)
    user_playlists = [p for n, p in playlist_dict.items() if n != 'favorites']

    active_playlist=None
    for pp_name, playlist in playlist_dict.items():
        if pp_name != 'favorites':
            active_playlist = playlist
            break

    for widget in main_frame.winfo_children():
        widget.destroy()

    sidebar = tk.Frame(main_frame, bg=bg, width=200)
    sidebar.pack(side="left", fill="y")
    side_height = main_frame.winfo_height()
    playlists_name_frame = tk.Frame(sidebar, bg=bg)
    playlists_name_frame.pack(side=tk.TOP, fill='both', pady=(side_height // 3))

    def on_enter(e):
        e.widget['foreground'] = icon_bright
    
    def on_leave(e):
        e.widget['foreground'] = icon_dark

    def on_enter_p(e):
        e.widget['foreground'] = 'white'
    
    def on_leave_p(e, playlist_id):
        nonlocal active_playlist
        e.widget['foreground'] = song_color if active_playlist and active_playlist.playlist_id == playlist_id else 'grey'

    def fill_playlist_labels(rel_frame: tk.Frame):
        nonlocal active_playlist
        for c in rel_frame.winfo_children():
            c.destroy()

        main_turbo = tk.Label(rel_frame, text='Playlists: ', font=empty_font, bg=bg, fg=song_color)
        main_turbo.pack(fill='x', pady=(5, 0), anchor='center')
        main_line = tk.Label(rel_frame, text='_'*20, font=empty_font, bg=bg, fg=song_color)
        main_line.pack(fill='x', anchor='e')
        if len(list(playlist_dict.keys())) == 1:
            empty_lbl = tk.Label(rel_frame, text='No available playlists...', font=playlist_font, bg=bg, fg=song_color)
            empty_lbl.pack(fill='x', pady=5, anchor='center')
            return

        def remove(_event, playlist):
            delete_playlist(session, playlist_id=playlist.playlist_id)
            messagebox.showinfo('Sukes', f'Usunięto playlistę {playlist.name}')
            playlist_dict.pop(pp_name)
            fill_playlist_labels(rel_frame=rel_frame)
        def switch(_event,playlist):
            nonlocal active_playlist
            active_playlist = playlist
            fill_playlist_labels(rel_frame=rel_frame)
            fill_list(playlist)

        for pp_name, playlist in playlist_dict.items():
            nonlocal active_playlist
            if pp_name == 'favorites':
                continue
            row = tk.Frame(rel_frame, bg=bg)
            sc = 'grey' if active_playlist is None else (song_color if playlist.playlist_id == active_playlist.playlist_id else 'grey')
            lbl = tk.Label(row, text=playlist.name, font=playlist_font, bg=bg, fg=sc)
            lbl.pack(side=tk.LEFT)
            cross = tk.Label(row, bg=bg, fg=icon_dark, text = '❌', font=("Segoe UI", 16, 'bold'))
            cross.pack(side=tk.RIGHT)
            cross.bind('<Button-1>', lambda e, p=playlist: remove(e, p))
            cross.bind('<Enter>', on_enter)
            cross.bind('<Leave>', on_leave)
            lbl.bind('<Button-1>', lambda e, p=playlist: switch(e, p))
            lbl.bind('<Enter>', on_enter_p)
            lbl.bind('<Leave>', lambda e: on_leave_p(e, playlist_id=playlist.playlist_id))
            row.pack(fill='x', pady=5, anchor='center')


    fill_playlist_labels(playlists_name_frame)
    side_main = tk.Label(sidebar, text='New playlist: ', font=nowa_font, bg=bg, fg=song_color)
    input_frame = tk.Frame(sidebar, bg=bg)
    new_playlist = tk.Entry(input_frame, font=playlist_font)
    def handle_add():
        p_name = new_playlist.get().strip()
        if len(p_name) == 0:
            messagebox.showerror('Błąd', 'Pusta nazwa playlisty')
            return
        if p_name in playlist_dict.keys() or p_name == 'favorites':
            messagebox.showerror('Błąd', 'Playlista już istnieje')
            return
        n_p = create_playlist(session, name=p_name, user_id=user.user_id)
        messagebox.showinfo('Sukes', f'Dodano playlistę {p_name}')
        playlist_dict[str(p_name)] = n_p
        fill_playlist_labels(playlists_name_frame)

    new_playlist.pack(side=tk.LEFT, padx=(0, 5), anchor='se')
    add_button = tk.Button(input_frame, text='Dodaj', command=handle_add,
                           bg='#88af9f', fg=dodaj, font=("Segoe UI", 10, 'bold'))
    add_button.pack(side=tk.RIGHT, anchor='se')
    input_frame.pack(side=tk.BOTTOM, fill='x')

    side_main.pack(side=tk.BOTTOM, anchor='sw')

    content_frame = tk.Frame(main_frame, bg=bg)
    content_frame.pack(expand=True, fill='both')

    #width = 2 * main_frame.winfo_width()
    width = 500
    height = int(840 * (1440 / content_frame.winfo_height()))
    list_height = height // 14

    label_frame = tk.Frame(content_frame, bg=bg)
    label_frame.pack(pady=(0, pad_small))

    playlist_icon = tk.Label(label_frame, text='🔖', font=icon_big_font, bg=bg, fg=icon_dark)
    playlist_icon.pack(pady=(pad_big, pad_small), side=tk.LEFT)

    p_text = tk.Label(label_frame, text='Playlists', font=label_big_font, fg='#3fbf7f', bg=bg)
    p_text.pack(side=tk.LEFT, pady=(pad_big, pad_small))

    user_playlists = get_playlists_by_user(session, user.user_id)
    playlist_dict = {str(p.name): p for p in user_playlists}
    favorites = playlist_dict['favorites']
    favorites_set = get_favorites_set(session, favorites)

    # --- Main layout setup ---
    playlist_list_frame = tk.Frame(content_frame, bg=bg, width=width, height=height)
    playlist_list_frame.pack()
    playlist_list_frame.pack_propagate(False)

    def fill_list(playlist):
        for c in playlist_list_frame.winfo_children():
            c.destroy()
        for i, song in enumerate(get_songs_in_playlist(session, playlist.playlist_id)):
            entry_frame = get_song_in_playlist_frame(
                playlist_list_frame,
                session,
                idx=i,
                h=40, # Set a fixed height for each song entry
                song=song,
                favorites_set=favorites_set,
                favorites_id=favorites.playlist_id,
                playlist_id=playlist.playlist_id
            )
            entry_frame.pack_propagate(False)
            entry_frame.pack(side=tk.TOP, pady=(0, pad_small), fill='x')

    if active_playlist is not None:
        fill_list(active_playlist)

