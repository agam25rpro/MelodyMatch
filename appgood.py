import pickle
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from flask import Flask, render_template, request, jsonify
import os
import requests
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Spotify credentials from environment variables
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')

# Initialize the Spotify client
client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Function to download similarity.pkl from Google Drive
def download_similarity_pkl():
    url = "https://drive.google.com/uc?id=1n2cBVm1gTx4utK2F2LrFOMPWpPn-Jj0n"
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open("similarity.pkl", "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
    else:
        raise Exception("Failed to download the file: HTTP Status", response.status_code)

# Download the similarity file
download_similarity_pkl()

# Load data
music = pickle.load(open('df.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

def get_song_album_cover_url(song_name, artist_name):
    search_query = f"track:{song_name} artist:{artist_name}"
    results = sp.search(q=search_query, type="track")

    if results and results["tracks"]["items"]:
        track = results["tracks"]["items"][0]
        album_cover_url = track["album"]["images"][0]["url"]
        return album_cover_url
    else:
        return "https://i.postimg.cc/0QNxYz4V/social.png"

def recommend(song):
    index = music[music['song'] == song].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_music_names = []
    recommended_music_posters = []
    for i in distances[1:6]:
        artist = music.iloc[i[0]].artist
        recommended_music_posters.append(get_song_album_cover_url(music.iloc[i[0]].song, artist))
        recommended_music_names.append(music.iloc[i[0]].song)

    return recommended_music_names, recommended_music_posters

@app.route('/')
def index():
    music_list = music['song'].values
    return render_template('index.html', music_list=music_list)

@app.route('/recommend', methods=['POST'])
def recommend_song():
    song = request.form['song']
    recommended_music_names, recommended_music_posters = recommend(song)
    return jsonify(names=recommended_music_names, posters=recommended_music_posters)

if __name__ == '__main__':
    app.run(debug=True)
