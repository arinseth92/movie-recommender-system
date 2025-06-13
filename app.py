import streamlit as st
import pickle
import pandas as pd
import requests

@st.cache_resource
def load_data():
    # Hugging Face URLs
    movies_url = "https://huggingface.co/datasets/arinseth92/movie-recommender-pkl/resolve/main/movies.pkl"
    similarity_url = "https://huggingface.co/datasets/arinseth92/movie-recommender-pkl/resolve/main/similarity.pkl"

    # Download the files from Hugging Face
    with open("movies.pkl", "wb") as f:
        f.write(requests.get(movies_url).content)

    with open("similarity.pkl", "wb") as f:
        f.write(requests.get(similarity_url).content)

    with open("movies.pkl", "rb") as f:
        movies = pickle.load(f)

    with open("similarity.pkl", "rb") as f:
        similarity = pickle.load(f)

    return movies, similarity

# Load Data
movies, similarity = load_data()

# Streamlit UI
st.title("🎬 Movie Recommender System")
selected_movie = st.selectbox("Choose a movie:", movies["title"].values)

def recommend(movie):
    index = movies[movies["title"] == movie].index[0]
    distances = similarity[index]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
    return [movies.iloc[i[0]].title for i in movie_list]

if st.button("Recommend 🎥"):
    recommendations = recommend(selected_movie)
    st.subheader("Recommended Movies:")
    for i, title in enumerate(recommendations, 1):
        st.write(f"{i}. {title}")