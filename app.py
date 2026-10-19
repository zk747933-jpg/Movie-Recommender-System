import os
import pickle
import numpy as np
import pandas as pd
import requests
import streamlit as st

st.set_page_config(page_title="Movie Recommender", page_icon="🎬", layout="wide")
st.title("🎬 Movie Recommender System")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


@st.cache_data
def load_movies():
    with open(os.path.join(BASE_DIR, "movies_dict.pkl"), "rb") as f:
        return pd.DataFrame(pickle.load(f)).reset_index(drop=True)


@st.cache_resource
def load_neighbors():
    return np.load(os.path.join(BASE_DIR, "top_neighbors.npy"))


@st.cache_data(show_spinner=False)
def fetch_poster(movie_id):
    placeholder = "https://via.placeholder.com/500x750?text=No+Poster"
    try:
        r = requests.get(
            f"https://api.themoviedb.org/3/movie/{movie_id}",
            params={"api_key": st.secrets["TMDB_API_KEY"], "language": "en-US"},
            timeout=10,
        )
        path = r.json().get("poster_path")
        return "https://image.tmdb.org/t/p/w500" + path if path else placeholder
    except Exception:
        return placeholder


movies = load_movies()
neighbors = load_neighbors()


def recommend(movie):
    pos = int(np.where(movies["title"].values == movie)[0][0])
    names, posters = [], []
    for i in neighbors[pos][:5]:
        row = movies.iloc[int(i)]
        names.append(row["title"])
        posters.append(fetch_poster(int(row["movie_id"])))
    return names, posters


selected_movie = st.selectbox("Select Movie", movies["title"].values)

if st.button("Recommend"):
    names, posters = recommend(selected_movie)
    cols = st.columns(5)
    for col, name, poster in zip(cols, names, posters):
        with col:
            st.text(name)
            st.image(poster)
