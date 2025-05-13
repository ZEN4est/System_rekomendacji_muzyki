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

# tamta funcke mozna wywyalic i moze ogaranac tylko ta
def search_tracks_with_filters(sp, artist=None, decade=None, genre=None, language=None, use_favourites=False):
    query_parts = []

    if artist:
        query_parts.append(f"artist:{artist}")
    if genre:
        query_parts.append(f"genre:{genre}")
    if decade:
        # przykład: "1990-1999"
        start_year = int(decade[:4])
        end_year = int(decade[-4:])
        query_parts.append(f"year:{start_year}-{end_year}")
    if language:
        query_parts.append(f"tag:{language}") #język nie jest bezpośrednio obsługiwany, to obejście

    query = " ".join(query_parts)

    results = sp.search(q=query, type="track", limit=20)

    tracks = results['tracks']['items']

    if use_favourites:
        # Filtrowanie tylko do polubionych, trzebabedzie przekazac tutaj zapisane tracki
        saved_tracks = sp.current_user_saved_tracks(limit=50)
        saved_ids = {item['track']['id'] for item in saved_tracks['items']}
        tracks = [track for track in tracks if track['id'] in saved_ids]

    return tracks

