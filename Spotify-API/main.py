# ----------------------------------------------IMPORTS-------------------------------------------
from secrets import CLIENT_SECRET_KEY, CLIENT_ID, REDIRECT_URL, CACHE_PATH
import requests
from bs4 import BeautifulSoup
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pprint

# -----------------------------------------SCRAPING BILLBOARD-------------------------------------
# date = '2000-08-12'  # YYYY-MM-DD

date = input("Which year do you want to travel to? Type the date in this format YYYY-MM-DD: ")
response = requests.get(url=f"https://www.billboard.com/charts/hot-100/{date}/")
website = response.text

# -----------------------------------------  MAKING SOUP ------------------------------------------
soup = BeautifulSoup(website, "html.parser")
songs = list()
for song in soup.select("li.o-chart-results-list__item h3#title-of-a-story"):
    songs.append(song.getText().strip('\n'))

# ------------------------------SPOTIFY AUTHORIZATION-AUTHORIZATION CODE FLOW-----------------------
sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        scope="playlist-modify-private",
        redirect_uri=REDIRECT_URL,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET_KEY,
        show_dialog=True,
        cache_path=CACHE_PATH
    )
)
user_id = sp.current_user()["id"]

# ---------------------------------------GETTING SONG URIs------------------------------------------

song_uris = list()
year = date.split("-")[0]
for song in songs:
    result = sp.search(q=f"track:{song} year:{year}", type="track")
    # print(result)
    try:
        uri = result["tracks"]["items"][0]["uri"]
        song_uris.append(uri)
    except IndexError:
        print(f"{song} doesn't exist in Spotify. Skipped.")

# print(song_uris)

# --------------------------------------CREATING A NEW PRIVATE PLAYLIST ----------------------------------

playlist_name = f"{date} Billboard 100"
playlist = sp.user_playlist_create(user=user_id,
                                   name=playlist_name,
                                   public=False)

sp.playlist_add_items(playlist_id=playlist["id"],
                      items=song_uris)
