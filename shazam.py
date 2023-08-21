import asyncio
from shazamio import Shazam


async def shazam_song(filename):
  shazam = Shazam()
  result = await shazam.recognize_song(filename)
  return result


def extract_song_data(filename):
  loop = asyncio.get_event_loop()
  data = loop.run_until_complete(shazam_song(filename))['track']
  
  output = {'title' : data['title'],
            'artist' : data['subtitle'],
            }

  for tag in data['sections'][0]['metadata']:
    output[f"{tag['title'].lower()}"] = tag['text']

  try:
    art_url = data['images']['coverart']
  except KeyError:
    art_url = None

  try:
    genre = data['genres']['primary']
  except KeyError:
    genre = None

  output['primary_genre'] = genre
  output['art_url'] = art_url

  
  return output


if __name__ == "__main__":
  file = "Karen  - Track 18.mp3"
  data = extract_song_data(file)
  print(data)