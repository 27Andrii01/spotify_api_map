"""
Script works with
SPotify API and helps
users with finding
information about artists
"""
import os
import base64
import json
import folium
from requests import post, get
from dotenv import load_dotenv
import pycountry

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

def get_token():
    """
    Function get token
    """
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"

    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token

def get_auth_header(token):
    """
    Functiion get authheader
    """
    return {"Authorization": "Bearer " + token}

def search_for_artist(token, artist_name):
    """
    Function search the artist
    """
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"?q={artist_name}&type=artist&limit=1"

    query_url = url + query
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)["artists"]["items"]
    if len(json_result) == 0:
        return None
    return json_result[0]

def get_songs_by_artist(token, artist_id):
    """
    Function find a songs list by artist id
    """
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=US"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)['tracks']
    return json_result

def get_available_markets(token: str, song_id: str):
    """
    Function get countries where the most popular song is available
    """
    url = f"https://api.spotify.com/v1/tracks/{song_id}"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)
    return json_result['available_markets']

token = get_token()
artist = search_for_artist(token, "Eminem")
songs = get_songs_by_artist(token, artist['id'])
gam = get_available_markets(token, songs[0]['id'])
the_most_popular = songs[0]['name']

def get_country_name(gam):
    """
    function get names of countries that are in available markets
    """
    res = []
    for am in gam:
        name = pycountry.countries.get(alpha_2 = am)
        if name:
            res.append(name.name)

    return res

def get_cordinate_map(aval_mark:list ) -> list:
    """
    Function, that convert location into coordinates(latitude, longtitude) and print them on the map
    """
    res = []
    nores = []
    workinf = []
    data = "coord.csv"
    with open(data, "r", encoding="UTF-8") as file_info:
        ready_info = file_info.readlines()
    for i in ready_info:
        workinf.append(i.strip())
    for i in workinf:
        if (i.split("\t"))[3] in aval_mark:
            res.append((float((i.split("\t"))[1]), float((i.split("\t"))[2]), (i.split("\t"))[3]))
        else:
            nores.append((float((i.split("\t"))[1]), float((i.split("\t"))[2]), (i.split("\t"))[3]))
    map = folium.Map(tiles="Stamen Terrain", min_zoom=3)
    f1 = folium.FeatureGroup(name=f'{the_most_popular} Avail')
    for i in res:
        loc = folium.Marker(location=[i[0], i[1]],\
        icon = folium.Icon(color='green'), popup=i[2])
        f1.add_child(loc)
    f1.add_to(map)
    f2 = folium.FeatureGroup(name=f'{the_most_popular} Unavail')
    for i in set(nores):
        loc1 = folium.Marker(location=[i[0], i[1]], icon = folium.Icon(color='red'), popup=i[2])
        f2.add_child(loc1)
    f2.add_to(map)
    folium.LayerControl().add_to(map)
    map.save("map_spotify.html")