import streamlit as st
import pickle
import pandas as pd
import requests

# ---------------- Poster Fetch ----------------
def fetch_poster(movie_id):
    try:
        response = requests.get(
            f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=2ccdd2a7349984d34cc4888cacdf5656&language=en-US",
            timeout=10
        )

        data = response.json()

        if data.get("poster_path"):
            return "https://image.tmdb.org/t/p/w500" + data["poster_path"]

        return "https://via.placeholder.com/500x750?text=No+Poster"

    except:
        return "https://via.placeholder.com/500x750?text=Error"


# ---------------- Load Data ----------------

try:
    movies_dict = pickle.load(
        open("movies_dict.pkl", "rb")
    )

    movies = pd.DataFrame(movies_dict)

    similarity = pickle.load(
        open("similarity.pkl", "rb")
    )

except Exception as e:
    st.error(f"Loading Error: {e}")
    st.stop()


# ---------------- Recommendation ----------------

def recommend(movie):

    movie_index = movies[
        movies['title'] == movie
    ].index[0]

    recommended_movies = []
    recommended_posters = []

    try:

        # optimized neighbors list
        neighbors = similarity[movie_index]

        for idx in neighbors:

            if idx == movie_index:
                continue

            movie_id = movies.iloc[idx].movie_id

            recommended_movies.append(
                movies.iloc[idx].title
            )

            recommended_posters.append(
                fetch_poster(movie_id)
            )

            if len(recommended_movies) == 5:
                break

        return recommended_movies, recommended_posters

    except Exception as e:

        st.error(
            f"Recommendation Error: {e}"
        )

        return [], []


# ---------------- UI ----------------

st.title("🎬 Movie Recommender System")

selected_movie = st.selectbox(
    "Select Movie",
    movies['title'].values
)

if st.button("Recommend"):

    names, posters = recommend(
        selected_movie
    )

    if len(names) > 0:

        cols = st.columns(5)

        for i in range(len(names)):

            with cols[i]:
                st.text(names[i])
                st.image(posters[i])

    else:
        st.warning("No recommendations found")
