from cProfile import label
import tkinter as tk
from tkinter import ttk
from turtle import bgcolor
from model.crud import add_song_to_playlist, get_favorites_by_user_id, get_playlist_song, get_songs_in_playlist, remove_song_from_playlist, \
                        get_playlists_by_user
from model.models import Playlist, Song, User
from sqlalchemy.orm import Session

class ScrollablePopup:
    def __init__(self, session: Session, parent, x, y, content_data, song: Song, style_dict):
        self.session = session
        self.style_dict=style_dict
        self.top = tk.Toplevel(parent)
        self.top.title('Playlists')
        self.top.geometry(f'+{x}+{y}')
        self.top.transient(parent)
        self.top.wait_visibility()
        self.top.grab_set()
        self.top.focus_set()
        self.song = song
        self.content_data = content_data

        self.create_scrollable_frame(content_data)

        self.top.protocol("WM_DELETE_WINDOW", self.on_close_popup)

    def create_scrollable_frame(self, content_labels_data):
        self.canvas = tk.Canvas(self.top, borderwidth=0, background=self.style_dict['bg'])
        self.scrollbar = ttk.Scrollbar(self.top, orient='vertical', command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side='right', fill='y')
        self.canvas.pack(side='left', fill='both', expand=True)

        s = ttk.Style()
        s.configure('TFrame', background=self.style_dict['bg'])
        self.scrollable_frame = ttk.Frame(self.canvas, style='TFrame')
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor='nw')

        self.scrollable_frame.bind(
            '<Configure>',
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox('all')
            )
        )

        if not content_labels_data.keys():
            empty_label = tk.Label(self.scrollable_frame, text='No playlists found',
                                   font=self.style_dict['empty_font'], fg=self.style_dict['song_color'], bg=self.style_dict['bg'])
            empty_label.pack(pady=(20, 0), padx=(20, 0), side=tk.TOP, anchor='center')
            self.scrollable_frame.bind('<Button-1>', lambda e: self.on_close_popup)
        for playlist, has in content_labels_data.items():
            label = ttk.Label(self.scrollable_frame, text=playlist.name, borderwidth=1, relief='solid', padding=(5, 2))
            label.configure(background=self.style_dict['bg'])
            if has:
                label.configure(foreground=self.style_dict['song_color'])
            else:
                label.configure(foreground='grey')
            label.pack(fill='x', padx=5, pady=2)
            label.bind('<Button-1>', lambda e: self.on_clickable_label_click(e, playlist, has))
            label.config(cursor='hand2')

    def on_clickable_label_click(self, event, playlist, has):
        if has:
            remove_song_from_playlist(self.session, playlist_id=playlist.playlist_id, song_id=self.song.song_id)
            print(f'Removed {self.song.title} from {playlist.name}')
        else:
            if get_playlist_song(self.session, playlist_id=playlist.playlist_id, song_id=self.song.song_id) is None:
                add_song_to_playlist(self.session, playlist_id=playlist.playlist_id, song_id=self.song.song_id)
                print(f'Added {self.song.title} to {playlist.name}')
            else:
                print(f'Song {self.song.title} to {playlist.name}')

        self.on_close_popup()

    def on_close_popup(self):
        self.top.grab_release()
        self.top.destroy()

def get_song_in_favorites_frame(outer_frame: tk.Frame, session: Session, idx: int, h: int,
                                song: Song, favorites_id: int, playlist_has_song: dict[Playlist, bool]) -> tk.Frame:
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
    print(entry_font)
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

    # --- Buttons ----
    button_frame= tk.Frame(frame, bg=bg)
    button_frame.grid(row=0, column=2, sticky='nse')

    add_label = tk.Label(button_frame, bg=bg, fg=icon_dark, text='➕', font=song_icon_font)

    def add(_event):
        label_x = add_label.winfo_rootx()
        label_y = add_label.winfo_rooty()
        label_width = add_label.winfo_width()
        popup_x = label_x + label_width + pad_small * 2
        popup_y = label_y
        ScrollablePopup(session, add_label.winfo_toplevel(), popup_x, popup_y, playlist_has_song, song,
                        style_dict={'bg': bg, 'empty_font': song_icon_font, 'song_color': song_color})

    remove_label = tk.Label(button_frame, bg=bg, fg=icon_dark, text = '❌', font=song_icon_font)

    def remove(_event):
        remove_song_from_playlist(session, favorites_id, song.song_id)
        frame.destroy()

    def on_enter(e):
        e.widget['foreground'] = icon_bright
    
    def on_leave(e):
        e.widget['foreground'] = icon_dark

    add_label.bind('<Button-1>', add)
    add_label.bind('<Enter>', on_enter)
    add_label.bind('<Leave>', on_leave)

    remove_label.bind('<Button-1>', remove)
    remove_label.bind('<Enter>', on_enter)
    remove_label.bind('<Leave>', on_leave)

    remove_label.pack(side=tk.RIGHT, padx=(0, pad_small))
    add_label.pack(side=tk.RIGHT)

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

    heart_text = tk.Label(label_frame, text='Favorites', font=label_big_font, fg='#3fbf7f', bg=bg)
    heart_text.pack(side=tk.LEFT, pady=(pad_big, pad_small))

    favorites_list_frame = tk.Frame(content_frame, bg=bg, width=width, height=height)
    favorites_list_frame.pack()
    favorites_list_frame.pack_propagate(False)

    playlists_all = get_playlists_by_user(session, user.user_id)

    songs = get_songs_in_playlist(session, favorites.playlist_id)
    if len(songs) == 0:
        empty_label = tk.Label(favorites_list_frame, text='Empty...', font=empty_font, fg=song_color, bg=bg)
        empty_label.pack(pady=(pad_big, 0), side=tk.TOP)
    for idx, song in enumerate(songs):
        playlist_has_song: dict[Playlist, bool] = {p: bool(get_playlist_song(session, playlist_id=p.playlist_id, song_id=song.song_id)) for p in playlists_all if p.name != 'favorites'}
        track_frame = get_song_in_favorites_frame(
            outer_frame=favorites_list_frame, session=session, idx=idx, h=list_height,
            song=song, favorites_id=favorites.playlist_id, playlist_has_song=playlist_has_song
        )
        track_frame.pack_propagate(False)
        track_frame.pack(side=tk.TOP, pady=(0, pad_small // 2), fill='x')


