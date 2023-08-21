import spotify_api as sapi
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
    inpath = input("In-path: ")
    op_args = input("Optional arguments (--a or --r): ")
    shazam = input("Input anything for Shazam mode: ")
    album_art, reset = False, False
    
    try:
        songs = [file for file in os.listdir(inpath) if file.endswith(".mp3")]
    except FileNotFoundError:
        sys.exit("Invalid path name!")

    if "--a" in op_args:
        album_art = True
        
    if "--r" in op_args:
        reset = True

    for song in songs:
        if shazam:
            audio = handle_shazam_song(song, inpath, album_art=album_art, reset=reset)
        else:
            audio = handle_spotify_song(song, inpath, album_art=album_art, reset=reset)
        
        audio.save()

        song_path = f"{inpath}\\{song}"
        try:
            artist = str(audio.tags['TPE1'])
        except KeyError:
            artist = None

        try:
            album = str(audio.tags['TALB'])
        except KeyError:
            album = None

        if any(c in album for c in illegal_chars) or any(c in artist for c in illegal_chars):
            for c in illegal_chars:
                artist = artist.replace(c, " ")
                album = album.replace(c, " ")


        if artist:
            if artist in artist_dict.keys():
                if album:
                    if album in artist_dict[artist]:
                        os.rename(song_path, f"{inpath}\\{artist}\\{album}\\{song}")
                    else:
                        artist_dict[artist].append(album)
                        os.mkdir(f"{inpath}\\{artist}\\{album}")
                        os.rename(song_path, f"{inpath}\\{artist}\\{album}\\{song}")
                else:
                    os.rename(song_path, f"{inpath}\\{artist}\\{song}")
            else:
                artist_dict[artist] = []
                os.mkdir(f"{inpath}\\{artist}")
                if album:
                    if album in artist_dict[artist]:
                        os.rename(song_path, f"{inpath}\\{artist}\\{album}\\{song}")
                    else:
                        artist_dict[artist].append(album)
                        os.mkdir(f"{inpath}\\{artist}\\{album}")
                        os.rename(song_path, f"{inpath}\\{artist}\\{album}\\{song}")
                else:
                    os.rename(song_path, f"{inpath}\\{artist}\\{song}")
        else:
            try:
                os.mkdir(f"{inpath}\\Unknown")
            except FileExistsError:
                pass

            os.rename(song_path, f"{inpath}\\Unknown")



def handle_spotify_song(filename, inpath, album_art = False, reset = False):
    if matches := re.search(r"([^\\]+.mp3)", filename):
        song_name = matches.groups(1)[0]
    else:
        return None

    token = sapi.get_token()
    audio = MP3(f"{inpath}\\{song_name}", ID3=ID3)

    try:
        audio.add_tags()
    except error:
        pass
    
    if "TPE1" in audio.tags:
        result = sapi.search_for_track(token, song_name.split(".")[0], artist=audio.tags['TPE1'])
    elif "TPE2" in audio.tags:
        result = sapi.search_for_track(token, song_name.split(".")[0], artist=audio.tags['TPE2'])
    else:
        result = sapi.search_for_track(token, song_name.split(".")[0])


    if reset:
        audio.delete()

    md.add_title(result, audio)
    md.add_year(result, audio)
    md.add_artist(result, audio)
    md.add_album(result, audio)
    md.add_track_number(result, audio)
    md.add_genres(result, audio)

    if album_art:
        md.add_album_art(result, audio)

    return audio


def handle_shazam_song(filename, inpath, album_art = False, reset = False):
    data = extract_song_data(f"{inpath}\\{filename}")
    audio = MP3(f"{inpath}\\{filename}", ID3=ID3)

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


if __name__ == "__main__":
    main()