import tkinter as tk
from tkinter import ttk
from neo4j import GraphDatabase
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
import os
from spotify_api import search_tracks, popular_genres, search_by_genre
from login import create_login_window
from PIL import Image, ImageTk
import requests
from io import BytesIO
from functools import partial

load_dotenv()

# Konfiguracja Spotify API
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=CLIENT_ID,
                                                           client_secret=CLIENT_SECRET))

# Konfiguracja Neo4j
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

def get_recommendations():
    query = entry.get()
    results = sp.search(q=query, type='track', limit=5)
    text_output.delete(1.0, tk.END)
    
    with driver.session() as session:
        for track in results['tracks']['items']:
            print(track)
            track_name = track['name']
            artist_name = track['artists'][0]['name']
            text_output.insert(tk.END, f"{track_name} - {artist_name}\n")
            
            session.run("MERGE (s:Song {name: $track_name, artist: $artist_name})", 
                        track_name=track_name, artist_name=artist_name)

def get_song_recommendations():
    query = entry.get()
    text_output.delete(1.0, tk.END)
    with driver.session() as session:
        results = session.run("""
            MATCH (s:Song {name: $query})-[:SIMILAR_TO]->(rec:Song)
            RETURN rec.name, rec.artist
        """, query=query)
        
        recommendations = results.values()
        if recommendations:
            text_output.insert(tk.END, "Rekomendowane utwory:\n")
            for rec_name, rec_artist in recommendations:
                text_output.insert(tk.END, f"{rec_name} - {rec_artist}\n")
        else:
            text_output.insert(tk.END, "Brak rekomendacji. Dodaj więcej danych do bazy!\n")

def add_similarity():
    song1 = entry_song1.get()
    song2 = entry_song2.get()
    with driver.session() as session:
        session.run("""
            MATCH (s1:Song {name: $song1}), (s2:Song {name: $song2})
            MERGE (s1)-[:SIMILAR_TO]->(s2)
            MERGE (s2)-[:SIMILAR_TO]->(s1)
        """, song1=song1, song2=song2)
    text_output.insert(tk.END, f"Dodano relację podobieństwa: {song1} <-> {song2}\n")

# GUI resultframe to frame z w ktorym wyswietlimy wyniki do przerobienia jak bedzie miesjce
def display_results(tracks):
    for widget in results_frame.winfo_children():
        widget.destroy()

    for track in tracks:
        name = track['name']
        artists = ', '.join(artist['name'] for artist in track['artists'])
        track_info = f"{name} – {artists}"
        label = tk.Label(results_frame, text=track_info)
        label.pack(anchor='w')

        button = tk.Button(results_frame, text="Dodaj do ulubionych", command=lambda t=track: on_select(t))
        button.pack(anchor='e')

def on_select(track):
    print(f"Wybrano: {track['name']} - {track['artists'][0]['name']}")

def on_search():
    query = entry.get()
    if query:
        tracks = search_tracks(sp,query)
        display_results(tracks)

def on_genre_search():
    genre = genre_var.get()
    if genre:
        tracks = search_by_genre(genre)
        display_results(tracks)
        
# genre_var = tk.StringVar()
# genre_dropdown = tk.Combobox(root, textvariable=genre_var, values=popular_genres)
# genre_dropdown.set("Wybierz gatunek")
# genre_dropdown.pack(pady=10)

# nwm baza nie działa to takie bagno będzie na razie
IMG_SIZE = 100
COLUMNS = 3
def render_tracks(frame, track_list, show_trash=False):
    for widget in frame.winfo_children():
        widget.destroy()

    frame.image_refs.clear()

    def bind_hover_recursive(widget, on_enter, on_leave):
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
        for child in widget.winfo_children():
            bind_hover_recursive(child, on_enter, on_leave)

    for idx, track in enumerate(track_list):
        row = idx // COLUMNS
        col = idx % COLUMNS

        card = tk.Frame(frame, bd=2, relief="groove", padx=5, pady=5)
        card.grid(row=row, column=col, padx=10, pady=10)
        card.grid_propagate(False)
        card.config(width=120, height=170)

        url = track["album"]["images"][0]["url"]
        img_data = BytesIO(requests.get(url).content)
        img = Image.open(img_data).resize((IMG_SIZE, IMG_SIZE))
        tk_img = ImageTk.PhotoImage(img)
        frame.image_refs.append(tk_img)

        img_label = tk.Label(card, image=tk_img, bg='white')
        img_label.pack()

        # Overlay (starts hidden)
        overlay = tk.Label(card, text="🗑️" if show_trash else "♥", font=("Arial", 16), bg="white", cursor="hand2")
        overlay.place(relx=0.9, rely=0.1, anchor="center")
        overlay.place_forget()

        # Functions for hover events
        def show_overlay(e, ol=overlay): ol.place(relx=0.9, rely=0.1, anchor="center")
        def hide_overlay(e, ol=overlay): ol.place_forget()

        bind_hover_recursive(card, show_overlay, hide_overlay)

        # Use partial to properly capture the track
        if show_trash:
            overlay.bind("<Button-1>", lambda e, t=track: remove_from_favorites(t))
        else:
            overlay.bind("<Button-1>", lambda e, t=track: add_to_favorites(t))

        # Info
        tk.Label(card, text=track["name"], font=("Segoe UI", 10, "bold"), wraplength=130, justify="center").pack(pady=(5, 0))
        artists = ", ".join(a["name"] for a in track["artists"])
        tk.Label(card, text=artists, font=("Segoe UI", 9), wraplength=130, justify="center").pack()

def temporary_search():
    query = entry.get()
    if query:
        #image_refs = []
        tracks = search_tracks(sp, query)
        render_tracks(search_frame, tracks, show_trash=False)

def create_scrollable_section(parent):
    canvas = tk.Canvas(parent)
    frame = ttk.Frame(canvas)
    scrollbar = ttk.Scrollbar(parent, orient='vertical', command=canvas.yview)

    canvas.create_window((0, 0), window=frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    frame.image_refs = []
    return frame

closed_manually = create_login_window()

if closed_manually:
    exit(0)

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
# GUI
root = tk.Tk()
root.title("Rekomendacje Muzyczne")
root.geometry("650x800")

favorited_tracks = []

notebook = ttk.Notebook(root)

# Create frames for Login and Register tabs
search_tab = ttk.Frame(notebook)
favorites_tab = ttk.Frame(notebook)

notebook.add(search_tab, text="Wyszukiwanie")
notebook.add(favorites_tab, text="Ulubione")
notebook.pack(expand=True, fill="both")

label = tk.Label(search_tab, text="Wpisz nazwę utworu lub artysty:")
label.pack()

entry = tk.Entry(search_tab, width=50)
entry.pack()

#button = tk.Button(root, text="Szukaj", command=get_recommendations)
button = tk.Button(search_tab, text="Szukaj", command=temporary_search)
button.pack()

search_frame = create_scrollable_section(search_tab)
favorites_frame = create_scrollable_section(favorites_tab)

def add_to_favorites(track):
    if track not in favorited_tracks:
        favorited_tracks.append(track)
        render_tracks(favorites_frame, favorited_tracks, show_trash=True)

def remove_from_favorites(track):
    if track in favorited_tracks:
        favorited_tracks.remove(track)
        render_tracks(favorites_frame, favorited_tracks, show_trash=True)


# --- Initial Render ---
#render_tracks(search_frame, tracks)
#render_tracks(favorites_frame, favorited_tracks, show_trash=True)

root.mainloop()
driver.close()

#label_recommend = tk.Label(root, text="Sprawdź rekomendacje dla utworu:")
#label_recommend.pack()
#
#entry_recommend = tk.Entry(root, width=50)
#entry_recommend.pack()
#
#button_recommend = tk.Button(root, text="Pokaż rekomendacje", command=get_song_recommendations)
#button_recommend.pack()
#
#label_similarity = tk.Label(root, text="Dodaj relację podobieństwa między utworami:")
#label_similarity.pack()
#
#entry_song1 = tk.Entry(root, width=50)
#entry_song1.pack()
#entry_song2 = tk.Entry(root, width=50)
#entry_song2.pack()
#
#button_similarity = tk.Button(root, text="Dodaj relację", command=add_similarity)
#button_similarity.pack()

#text_output = tk.Text(root, height=15, width=50)
#text_output.pack()
