import pickle
import streamlit as st
import requests
import os


# ---------------- FETCH POSTER ----------------
@st.cache_data
def fetch_poster(movie_id):
    # Use Streamlit secrets (deployed) or local env variable
    api_key = st.secrets.get("TMDB_API_KEY", os.getenv("TMDB_API_KEY", ""))
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US"

    try:
        response = requests.get(url, timeout=10, proxies={"http": "", "https": ""})
        response.raise_for_status()
        data = response.json()
        poster_path = data.get('poster_path')
        if poster_path:
            return "https://image.tmdb.org/t/p/w500" + poster_path
    except Exception:
        pass

    return "https://placehold.co/500x750?text=No+Poster"


# ---------------- RECOMMEND FUNCTION ----------------
def recommend(movie):
    try:
        index = movies[movies['title'] == movie].index[0]
    except IndexError:
        st.error("Movie not found in the dataset. Please select another one.")
        return [], []

    distances = sorted(
        list(enumerate(similarity[index])),
        reverse=True,
        key=lambda x: x[1]
    )

    recommended_movie_names = []
    recommended_movie_posters = []

    for i in distances[1:6]:
        movie_data = movies.iloc[i[0]]
        movie_id = movie_data['id']
        recommended_movie_posters.append(fetch_poster(movie_id))
        recommended_movie_names.append(movie_data['title'])

    return recommended_movie_names, recommended_movie_posters


# ---------------- STREAMLIT UI ----------------
st.set_page_config(layout="wide")
st.header('🎬 Movie Recommender System Using Machine Learning')

# ---------------- LOAD FILES ----------------
try:
    movies = pickle.load(open('movie_list.pkl', 'rb'))
    similarity = pickle.load(open('similarity.pkl', 'rb'))
except FileNotFoundError:
    st.error("Model files not found. Please ensure pkl files are available.")
    st.stop()

movie_list = movies['title'].values

# ---------------- MOVIE SELECTOR ----------------
selected_movie = st.selectbox(
    "Type or select a movie from the dropdown",
    movie_list
)

# ---------------- RECOMMEND BUTTON ----------------
if st.button('Show Recommendation'):
    with st.spinner('Finding recommendations...'):
        names, posters = recommend(selected_movie)

    if names:
        cols = st.columns(5)
        for i in range(5):
            with cols[i]:
                st.image(posters[i])
                st.markdown(f"**{names[i]}**")
