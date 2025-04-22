import tkinter as tk
from neo4j import GraphDatabase
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
import os
from spotify_api import search_tracks, popular_genres, search_by_genre

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

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

# GUI
root = tk.Tk()
root.title("Rekomendacje Muzyczne")

label = tk.Label(root, text="Wpisz nazwę utworu lub artysty:")
label.pack()

entry = tk.Entry(root, width=50)
entry.pack()

button = tk.Button(root, text="Szukaj", command=get_recommendations)
button.pack()

label_recommend = tk.Label(root, text="Sprawdź rekomendacje dla utworu:")
label_recommend.pack()

entry_recommend = tk.Entry(root, width=50)
entry_recommend.pack()

button_recommend = tk.Button(root, text="Pokaż rekomendacje", command=get_song_recommendations)
button_recommend.pack()

label_similarity = tk.Label(root, text="Dodaj relację podobieństwa między utworami:")
label_similarity.pack()

entry_song1 = tk.Entry(root, width=50)
entry_song1.pack()
entry_song2 = tk.Entry(root, width=50)
entry_song2.pack()

button_similarity = tk.Button(root, text="Dodaj relację", command=add_similarity)
button_similarity.pack()

text_output = tk.Text(root, height=15, width=50)
text_output.pack()

root.mainloop()

driver.close()
