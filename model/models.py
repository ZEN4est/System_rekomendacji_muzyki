from enum import auto
from turtle import back
from sqlalchemy import (
    create_engine, Column, Integer, String, ForeignKey, CheckConstraint, Table
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

# Association table: PlaylistSongs:
class PlaylistSong(Base):
    __tablename__ = 'playlistsongs'

    playlist_id = Column(Integer, ForeignKey('playlists.playlist_id'), primary_key=True)
    song_id = Column(Integer, ForeignKey('songs.song_id'), primary_key=True)

    # Relationshps (for easier joins)
    playlist = relationship('Playlist', back_populates='songs')
    song = relationship('Song', back_populates='playlists')

# Users table
class User(Base):
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)

    # Relationships
    playlists = relationship('Playlist', back_populates='user')

# Playlists table
class Playlist(Base):
    __tablename__ = 'playlists'

    playlist_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)

    # Relationships
    user = relationship('User', back_populates='playlists')
    songs = relationship('PlaylistSong', back_populates='playlist', cascade='all, delete-orphan')

# Songs table
class Song(Base):
    __tablename__ = 'songs'

    song_id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(100), nullable=False)
    language = Column(String(50), nullable=False)
    decade = Column(Integer, nullable=False)

    # Decade constraint
    __table_args__ = (
        CheckConstraint('decade >= 1900 and decade <= 2050 and decade % 10 = 0', name='check_decade_valid'),
    )

    # Relationships
    playlists = relationship('PlaylistSong', back_populates='song', cascade='all, delete-orphan')
    genres = relationship('SongGenre', back_populates="song", cascade='all, delete-orphan')
    artists = relationship('SongArtist', back_populates='song', cascade='all, delete-orphan')

# SongGenres table
class SongGenre(Base):
    __tablename__ = 'songgenres'

    song_id = Column(Integer, ForeignKey('songs.song_id'), primary_key=True)
    genre = Column(String(50), primary_key=True)

    # Relationships
    song = relationship('Song', back_populates='genres')

# SongArtists table
class SongArtist(Base):
    __tablename__ = 'songartists'

    song_id = Column(Integer, ForeignKey('songs.song_id'), primary_key=True)
    artist = Column(String(100), primary_key=True)

    # Relationships
    song = relationship('Song', back_populates='artists')
