import streamlit as st
import pickle
import requests
import os
from sklearn.metrics.pairwise import cosine_similarity

# ---------------- LOAD MOVIES ----------------
movies = pickle.load(open('movies.pkl', 'rb'))

# ---------------- LOAD OR CREATE SIMILARITY ----------------
if os.path.exists('similarity.pkl'):
    similarity = pickle.load(open('similarity.pkl', 'rb'))
else:
    # IMPORTANT:
    # This assumes you already have vectors stored in movies.pkl
    # Example: movies['tags'] already vectorized
    similarity = cosine_similarity(movies['tags'])
    pickle.dump(similarity, open('similarity.pkl', 'wb'))

# ---------------- FETCH POSTER ----------------
def fetch_poster(movie_id):
    response = requests.get(
        f'https://api.themoviedb.org/3/movie/{movie_id}?api_key=24e35f7efe10ebbd0830d3165015c62c&language=en-US'
    )
    data = response.json()

    if data.get('poster_path'):
        return "https://image.tmdb.org/t/p/w500" + data['poster_path']
    else:
        return "https://via.placeholder.com/500x750?text=No+Image"

# ---------------- RECOMMEND FUNCTION ----------------
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]

    movies_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:6]

    recommended_movies = []
    recommended_movies_posters = []

    for i in movies_list:
        idx = i[0]
        movie_id = movies.iloc[idx].movie_id
        recommended_movies.append(movies.iloc[idx].title)
        recommended_movies_posters.append(fetch_poster(movie_id))

    return recommended_movies, recommended_movies_posters

# ---------------- STREAMLIT UI ----------------
st.title('Movie Recommender System')

selected_movie_name = st.selectbox(
    "Enter your movie title",
    movies['title'].values
)

if st.button('Recommend'):
    names, posters = recommend(selected_movie_name)
    cols = st.columns(5)

    for idx, col in enumerate(cols):
        with col:
            st.text(names[idx])
            st.image(posters[idx])
