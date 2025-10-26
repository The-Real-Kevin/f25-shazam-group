from DBcontrol import connect
import sqlite3
import pandas as pd
from cm_helper import preprocess_audio
from hasher import create_hashes
from const_map import create_constellation_map
import librosa

def check_if_song_exists(youtube_url: str) -> bool:
    with connect() as con:
        cur = con.cursor()
        query = "SELECT COUNT(*) FROM songs WHERE youtube_url = ?"
        cur.execute(query, (youtube_url,))
        count = cur.fetchone()[0]
        return count > 0

def add_song(track_info: dict, resample_rate: None|int = 11025) -> int:
    with connect() as con:
        cur = con.cursor()

        # get the duration of the audio file
        audio_path = track_info["audio_path"]
        duration_s = librosa.get_duration(path=audio_path)

        # Insert the song metadata into the songs table
        query = """
            INSERT INTO songs (youtube_url, title, artist, artwork_url, audio_path, duration_s)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        data = (
            track_info["youtube_url"],
            track_info["title"],
            track_info["artist"],
            track_info["artwork_url"],
            track_info["audio_path"],
            duration_s
        )
        cur.execute(query, data)
        con.commit()

        # select the last inserted song id
        cur.execute("SELECT last_insert_rowid()")
        song_id = cur.fetchone()[0]

        # get the hashes for this song
        audio, sr = preprocess_audio(track_info["audio_path"], sr=resample_rate)
        constellation_map = create_constellation_map(audio, sr)
        hashes = create_hashes(constellation_map, song_id, sr)

        # Insert the hashes into the hashes table
        for hash_val, (time_stamp, _song_id) in hashes.items():
            query = """
                INSERT INTO hashes (hash_val, time_stamp, song_id)
                VALUES (?, ?, ?)
            """
            data = (hash_val, time_stamp, song_id)
            cur.execute(query, data)
        con.commit()

        return song_id
