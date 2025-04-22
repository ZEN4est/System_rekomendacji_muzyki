# Funkcja do wyszukiwania piosenek
def search_tracks(sp,query):
    results = sp.search(q=query, type='track', limit=10)
    return results['tracks']['items']