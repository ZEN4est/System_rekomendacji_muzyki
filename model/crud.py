from sqlalchemy.orm import Session
from .models import User, Playlist, Song, PlaylistSong, SongArtist, SongGenre

# ========== USER CRUD ==========
def create_user(session: Session, username, first_name, last_name, email, password):
    user = User(
        username=username,
        first_name=first_name,
        last_name=last_name,
        email=email,
        password=password
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    
    # TODO: check if there's a better way
    # Adding a 'favorites' playlist for every new user
    favorites = create_playlist(session, name='favorites', user_id=user.user_id)
    session.add(favorites)
    session.commit()
    session.refresh(favorites)

    return user

def get_user_by_id(session: Session, user_id):
    return session.query(User).filter_by(user_id=user_id).first()

def get_all_users(session: Session):
    return session.query(User).all()

def update_user_password(session: Session, user_id, new_password):
    user = get_user_by_id(session, user_id)
    if user:
        user.password = new_password
        session.commit()
        return True
    return False

def delete_user(session: Session, user_id):
    user = get_user_by_id(session, user_id)
    if user:
        session.delete(user)
        session.commit()
        return True
    return False


# ========== PLAYLIST CRUD ==========
def create_playlist(session: Session, name, user_id):
    playlist = Playlist(name=name, user_id=user_id)
    session.add(playlist)
    session.commit()
    session.refresh(playlist)
    return playlist

def get_playlist_by_id(session: Session, playlist_id):
    return session.query(Playlist).filter_by(playlist_id=playlist_id).first()

def get_playlists_by_user(session: Session, user_id):
    return session.query(Playlist).filter_by(user_id=user_id).all()

def delete_playlist(session: Session, playlist_id):
    playlist = get_playlist_by_id(session, playlist_id)
    if playlist:
        session.delete(playlist)
        session.commit()
        return True
    return False


# ========== SONG CRUD ==========
def create_song(session: Session, title, language, decade):
    song = Song(title=title, language=language, decade=decade)
    session.add(song)
    session.commit()
    session.refresh(song)
    return song

def get_song_by_id(session: Session, song_id):
    return session.query(Song).filter_by(song_id=song_id).first()

def get_all_songs(session: Session):
    return session.query(Song).all()

def update_song_title(session: Session, song_id, new_title):
    song = get_song_by_id(session, song_id)
    if song:
        song.title = new_title
        session.commit()
        return True
    return False

def delete_song(session: Session, song_id):
    song = get_song_by_id(session, song_id)
    if song:
        session.delete(song)
        session.commit()
        return True
    return False


# ========== PLAYLIST ↔ SONG RELATIONSHIP ==========
def add_song_to_playlist(session: Session, playlist_id, song_id):
    relation = PlaylistSong(playlist_id=playlist_id, song_id=song_id)
    session.add(relation)
    session.commit()
    return relation

def remove_song_from_playlist(session: Session, playlist_id, song_id):
    relation = session.query(PlaylistSong).filter_by(
        playlist_id=playlist_id, song_id=song_id
    ).first()
    if relation:
        session.delete(relation)
        session.commit()
        return True
    return False

def get_songs_in_playlist(session: Session, playlist_id):
    return session.query(Song).join(PlaylistSong).filter(PlaylistSong.playlist_id == playlist_id).all()


# ========== SONGGENRE CRUD ==========
def add_genre_to_song(session: Session, song_id: int, genre: str):
    genre_entry = SongGenre(song_id=song_id, genre=genre)
    session.add(genre_entry)
    session.commit()
    return genre_entry

def remove_genre_from_song(session: Session, song_id: int, genre: str):
    genre_entry = session.query(SongGenre).filter_by(song_id=song_id, genre=genre).first()
    if genre_entry:
        session.delete(genre_entry)
        session.commit()
        return True
    return False

def get_genres_for_song(session: Session, song_id: int):
    return session.query(SongGenre).filter_by(song_id=song_id).all()

def get_songs_by_genre(session: Session, genre: str):
    return session.query(SongGenre).filter_by(genre=genre).all()


# ========== SONGARTIST CRUD ==========
def add_artist_to_song(session: Session, song_id: int, artist: str):
    artist_entry = SongArtist(song_id=song_id, artist=artist)
    session.add(artist_entry)
    session.commit()
    return artist_entry

def remove_artist_from_song(session: Session, song_id: int, artist: str):
    artist_entry = session.query(SongArtist).filter_by(song_id=song_id, artist=artist).first()
    if artist_entry:
        session.delete(artist_entry)
        session.commit()
        return True
    return False

def get_artists_for_song(session: Session, song_id: int):
    return session.query(SongArtist).filter_by(song_id=song_id).all()

def get_songs_by_artist(session: Session, artist: str):
    return session.query(SongArtist).filter_by(artist=artist).all()
