import streamlit as st
import pickle
import zipfile
import numpy as np
import pandas as pd
import requests

st.set_page_config(page_title="Movie Recommender", page_icon="🎬", layout="wide")
st.title("🎬 Movie Recommender System")


@st.cache_data
def load_movies():
    with open("movies_dict.pkl", "rb") as f:
        return pd.DataFrame(pickle.load(f)).reset_index(drop=True)


@st.cache_resource
def load_similarity():
    # similarity.pkl 184MB hai (GitHub limit 100MB), isliye zip se padhte hain
    with zipfile.ZipFile("similarity.zip") as z:
        with z.open("similarity.pkl") as f:
            return np.asarray(pickle.load(f))


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
similarity = load_similarity()


def recommend(movie):
    pos = int(np.where(movies["title"].values == movie)[0][0])
    distances = similarity[pos]
    top = sorted(enumerate(distances), key=lambda x: x[1], reverse=True)[1:6]

    names, posters = [], []
    for i, _ in top:
        row = movies.iloc[i]
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
