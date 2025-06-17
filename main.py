from login import create_login_window
import music_recommender

playlist_details_example = [
    {
        "song_id": "1",
        "title": "Imagine",
        "decade": 1970,
        "language": "English",
        "genres": ["Rock"],
        "artists": ["John Lennon"]
    },
    {
        "song_id": "3",
        "title": "Hello",
        "decade": 2010,
        "language": "English",
        "genres": ["Pop"],
        "artists": ["Adele"]
    }
]

if __name__ == "__main__":
    print("----------------------------------\n")
    print(music_recommender.recommend_query_attributes_graph(playlist_details_example))
#     music_recommender.add_song(
#     song_id="3",
#     artist_name="Adele",
#     song_title="Hello",
#     genre_name="Pop",
#     language_name="English",
#     decade_int=2010
# )
    print("\n-----------------------------------------")
    create_login_window()
