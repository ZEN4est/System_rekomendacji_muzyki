import tkinter as tk
from neo4j import GraphDatabase
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Konfiguracja Spotify API
SPOTIPY_CLIENT_ID = "your_client_id"
SPOTIPY_CLIENT_SECRET = "your_client_secret"
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID,
                                                           client_secret=SPOTIPY_CLIENT_SECRET))

# Konfiguracja Neo4j
NEO4J_URI = "neo4j+s://5bd822a5.databases.neo4j.io"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "ccRa8Rm0x0ISGWe3ZTeE6cbFRA3m6FLntiAcQVmQFUM"

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
