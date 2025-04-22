popular_genres = [
    "pop", "hip-hop", "rap", "rock", "edm", "reggaeton", "r-n-b", "latin",
    "k-pop", "indie", "trap", "electronic", "dance", "metal", "alternative",
    "house", "classical", "funk", "jazz", "country"
]

# Funkcja do wyszukiwania piosenek
def search_tracks(sp,query):
    results = sp.search(q=query, type='track', limit=10)
    return results['tracks']['items']

def search_by_genre(sp, genre,country, limit=10):
    results = sp.search(q=f'genre:"{genre}"', type='artist', limit=limit)
    tracks = []

    for artist in results['artists']['items']:
        top_tracks = sp.artist_top_tracks(artist['id'], country=country)
        for track in top_tracks['tracks'][:1]:  # np. tylko pierwszy top track każdego artysty
            tracks.append(track)

    return tracks
