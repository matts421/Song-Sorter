from mutagen import id3
from mutagen.mp3 import MP3
from spotify_api import get_token, search_for_track
from PIL import Image
import requests
import io


def add_title(result, audio):
    if "TIT2" in audio.tags:
        return None
    try:
        title = result['name']
    except KeyError:
        return None
    else:
        audio.tags.add(id3.TIT2(text=title))


def add_album(result, audio):
    if "TALB" in audio.tags:
        return None
    try:
        album = result['album']['name']
    except KeyError:
        return None
    else:
        audio.tags.add(id3.TALB(text=album))


def add_year(result, audio):
    if "TYER" in audio.tags:
        return None
    try:
        date = result['album']['release_date']
        year = date.split("-")[0]
    except KeyError:
        print("Nope!")
        return None
    else:
        audio.tags.add(id3.TYER(text=year))


def add_artist(result, audio):
    if "TPE2" in audio.tags:
        return None
    if "TPE1" in audio.tags:
        return None
    try:
        artist = result['artists'][0]['name']
    except KeyError:
        print("Nope!")
        return None
    else:
        audio.tags.add(id3.TPE1(text=artist))
        audio.tags.add(id3.TPE2(text=artist))


def add_track_number(result, audio):
    if "TRCK" in audio.tags:
        return None
    try:
        track_number = str(result['track_number'])
    except KeyError:
        print("Nope!")
        return None
    else:
        audio.tags.add(id3.TRCK(text=track_number))


def add_genres(result, audio):
    if "TCON" in audio.tags:
        return None
    try:
        album_genres = result['album']['genres']
    except KeyError:
        return None
    else:
        genres = id3.TextFrame()
        for genre in album_genres:
            genres.append(genre)
        audio.tags.add(id3.TCON(text=genres))


def add_album_art(result, audio):
    if "APIC" in audio.tags:
        return None
    try:
        url = result['album']['images'][0]['url']
    except KeyError:
        return None
    else:
        im = Image.open(requests.get(url, stream=True).raw)
        audio.tags.add(
            id3.APIC(
            mime='image/jpeg',
            type=3,
            desc=u'Cover (front)',
            data=im_to_bytes(im)
            )
        )


def im_to_bytes(im):
    byte_array = io.BytesIO()
    im.save(byte_array, format=im.format)
    return byte_array.getvalue()



def add_title2(title, audio):
    if "TIT2" in audio.tags:
        return None
    else:
        audio.tags.add(id3.TIT2(text=title))


def add_album2(album, audio):
    if "TALB" in audio.tags:
        return None
    else:
        audio.tags.add(id3.TALB(text=album))


def add_year2(year, audio):
    if "TYER" in audio.tags:
        return None
    else:
        audio.tags.add(id3.TYER(text=year))


def add_artist2(artist, audio):
    if "TPE2" in audio.tags:
        return None
    if "TPE1" in audio.tags:
        return None
    else:
        audio.tags.add(id3.TPE1(text=artist))
        audio.tags.add(id3.TPE2(text=artist))


def add_genre2(genre, audio):
    if genre:
        if "TCON" in audio.tags:
            return None
        else:
            audio.tags.add(id3.TCON(text=genre))
    else:
        pass


def add_album_art2(url, audio):
    if url:
        if "APIC" in audio.tags:
            return None
        else:
            im = Image.open(requests.get(url, stream=True).raw)
            audio.tags.add(
                id3.APIC(
                mime='image/jpeg',
                type=3,
                desc=u'Cover (front)',
                data=im_to_bytes(im)
                )
            )
    else:
        pass


def add_label2(label, audio):
    if "TPUB" in audio.tags:
        return None
    else:
        audio.tags.add(id3.TPUB(text=label))


if __name__ == "__main__":
    song_name = "Dependin' On You.mp3"
    audio = MP3(song_name, ID3=id3.ID3)
    print(audio.tags.pprint())
    if "APIC" in audio.tags:
        print("Correct")
    else:
        print("Incorrect!")
    #print(audio.tags['TPE1'])