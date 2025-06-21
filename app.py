import streamlit as st
import pickle
import requests
import pandas as pd
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# --- Load Data ---
movies = pickle.load(open('movies.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

# --- Setup Retry Session for TMDb API ---
session = requests.Session()
retry_strategy = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET"]
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("http://", adapter)
session.mount("https://", adapter)

headers = {
    'User-Agent': 'Mozilla/5.0',
    'Accept': 'application/json'
}

API_KEY = "8265bd1679663a7ea12ac168da84d2e8"  # Your preferred API key

# --- Fetch Poster ---
def fetch_poster(movie_id):
    try:
        url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}'
        response = session.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        poster_path = data.get('poster_path')
        if poster_path:
            return "https://image.tmdb.org/t/p/w500/" + poster_path
        else:
            return "https://via.placeholder.com/300x450?text=No+Image"
    except Exception as e:
        st.error(f"Error fetching poster: {e}")
        return "https://via.placeholder.com/300x450?text=Error"

# --- Recommend Function ---
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_titles = []
    recommended_posters = []

    for i in movie_list:
        movie_id = movies.iloc[i[0]]['movie_id']
        recommended_titles.append(movies.iloc[i[0]]['title'])
        time.sleep(1)  # avoid rapid-fire requests
        recommended_posters.append(fetch_poster(movie_id))

    return recommended_titles, recommended_posters

# --- Streamlit UI ---
st.set_page_config(page_title="Movie Recommender", layout="wide")
st.title("🎬 Movie Recommender System")

selected_movie_name = st.selectbox("Choose a movie you like:", movies['title'].values)

if st.button("Recommend"):
    names, posters = recommend(selected_movie_name)

    cols = st.columns(5)
    for idx, col in enumerate(cols):
        with col:
            st.text(names[idx])
            st.image(posters[idx])
