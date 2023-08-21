import metadata as md
from shazam import extract_song_data
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, error
import re
import os
import sys

artist_dict = {}
illegal_chars = r'\/:*?<>|'

def main():
    BASE_DIR = input("In-path: ")

    if not os.path.exists(BASE_DIR):
        sys.exit("Invalid path!")

    try:
        os.mkdir(f"{BASE_DIR}\\Sorted")
    except FileExistsError:
        pass

    SORTED_DIR = f"{BASE_DIR}\\Sorted"

    op_args = input("Optional arguments (--a or --r): ")
    album_art, reset = False, False
    
    mp3_files = []

    exclude = set(['Sorted'])
    for root, dirs, files in os.walk(BASE_DIR):
        dirs[:] = [d for d in dirs if d not in exclude]
        if files != []:
            for file in files:
                if file.endswith('.mp3'):
                    mp3_files.append(f"{root}\\{file}")

    if "--a" in op_args:
        album_art = True
        
    if "--r" in op_args:
        reset = True

    for song_path in mp3_files:
        print(f"Started proccessing {song_path}")
        audio = handle_shazam_song(song_path, album_art=album_art, reset=reset)
        audio.save()

        try:
            artist = str(audio.tags['TPE1'])
        except KeyError:
            artist = None

        try:
            song = str(audio.tags['TIT2'])
        except KeyError:
            song = os.path.basename(song_path)

        try:
            album = str(audio.tags['TALB'])
        except KeyError:
            album = None
        
        try:
            if any(c in album for c in illegal_chars) or any(c in artist for c in illegal_chars):
                for c in illegal_chars:
                    artist = artist.replace(c, " ")
                    album = album.replace(c, " ")
        except TypeError:
            pass


        if artist:
            if artist in artist_dict.keys():
                if album:
                    if album in artist_dict[artist]:
                        move_song(song_path, SORTED_DIR, artist, album, song)
                    else:
                        artist_dict[artist].append(album)
                        try:
                            os.mkdir(f"{SORTED_DIR}\\{artist}\\{album}")
                        except FileExistsError:
                            pass
                        move_song(song_path, SORTED_DIR, artist, album, song)
                else:
                    move_song(song_path, SORTED_DIR, artist, album, song)
            else:
                artist_dict[artist] = []

                try:
                    os.mkdir(f"{SORTED_DIR}\\{artist}")
                except FileExistsError:
                    pass

                if album:
                        if album in artist_dict[artist]:
                            move_song(song_path, SORTED_DIR, artist, album, song)
                        else:
                            artist_dict[artist].append(album)
                            try:
                                os.mkdir(f"{SORTED_DIR}\\{artist}\\{album}")
                            except FileExistsError:
                                pass
                            move_song(song_path, SORTED_DIR, artist, album, song)
                else:
                    move_song(song_path, SORTED_DIR, artist, album, song)
        else:
            try:
                os.mkdir(f"{SORTED_DIR}\\Unknown")
            except FileExistsError:
                pass

            move_song(song_path, SORTED_DIR, artist, album, song)


def handle_shazam_song(inpath, album_art = False, reset = False):
    data = extract_song_data(inpath)
    audio = MP3(f"{inpath}", ID3=ID3)

    try:
        audio.add_tags()
    except error:
        pass

    if reset:
        audio.delete()

    md.add_title2(data['title'], audio)

    try:
        md.add_year2(data['released'], audio)
    except KeyError:
        pass

    md.add_artist2(data['artist'], audio)

    try:
        md.add_album2(data['album'], audio)
    except KeyError:
        pass

    try:
        md.add_label2(data['label'], audio)
    except KeyError:
        pass

    md.add_genre2(data['primary_genre'], audio)
    

    if album_art:
        md.add_album_art2(data['art_url'], audio)

    return audio


def move_song(song_path, sorted_dir, artist, album, song):
    if artist == None:
        try:
            os.rename(song_path, f"{sorted_dir}\\Unknown\\{song}.mp3")
        except FileExistsError:
            print(f"Skipping duplicate: {song_path}")
    elif album == None:
        try:
            os.rename(song_path, f"{sorted_dir}\\{artist}\\{song}.mp3")
        except FileExistsError:
            print(f"Skipping duplicate: {song_path}")
    else:
        try:
            os.rename(song_path, f"{sorted_dir}\\{artist}\\{album}\\{song}.mp3")
        except FileExistsError:
            print(f"Skipping duplicate: {song_path}")


if __name__ == "__main__":
    main()