import pickle
import streamlit as st
import requests

# Function to fetch movie details
def fetch_movie_details(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=6c18716348163256c33d881457089635&language=en-US"
    try:
        data = requests.get(url).json()
        poster_path = data.get('poster_path', "")
        overview = data.get('overview', "No overview available.")
        rating = data.get('vote_average', "N/A")
        release_date = data.get('release_date', "N/A")
        runtime = data.get('runtime', "N/A")
        genres = ", ".join([genre['name'] for genre in data.get('genres', [])])
        tagline = data.get('tagline', "")
        poster_url = f"https://image.tmdb.org/t/p/w500/{poster_path}" if poster_path else "https://via.placeholder.com/500x750.png?text=No+Poster"
        return poster_url, overview, rating, release_date, runtime, genres, tagline
    except:
        return ("https://via.placeholder.com/500x750.png?text=No+Poster",
                "No overview available.", "N/A", "N/A", "N/A", "N/A", "N/A")

# Function to fetch trailer video
def fetch_movie_trailer(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key=6c18716348163256c33d881457089635&language=en-US"
    try:
        data = requests.get(url).json()
        for video in data.get('results', []):
            if video['type'] == 'Trailer' and video['site'] == 'YouTube':
                return f"https://www.youtube.com/watch?v={video['key']}"
    except:
        pass
    return None

# Recommendation logic
def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movies = []
    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].movie_id
        title = movies.iloc[i[0]].title
        poster, overview, rating, release_date, runtime, genres, tagline = fetch_movie_details(movie_id)
        trailer_url = fetch_movie_trailer(movie_id)
        recommended_movies.append({
            "title": title,
            "poster": poster,
            "overview": overview,
            "rating": rating,
            "release_date": release_date,
            "runtime": runtime,
            "genres": genres,
            "tagline": tagline,
            "trailer_url": trailer_url
        })
    return recommended_movies

# Streamlit App
st.set_page_config(page_title="Movie Recommender System", layout="wide")
st.markdown(
    """
    <style>
    .title-style {
        font-size: 3rem;
        font-weight: bold;
        color: #2C3E50;
        text-align: center;
    }
    .movie-title {
        font-size: 1.2rem;
        font-weight: bold;
        color: #3498DB;
    }
    .movie-tagline {
        font-style: italic;
        color: #7F8C8D;
    }
    .movie-genres {
        font-weight: bold;
        color: #1ABC9C;
    }
    .container {
        background-color: #F4F6F7;
        padding: 10px;
        border-radius: 10px;
        margin: 10px;
    }
    </style>
    """, unsafe_allow_html=True
)
st.markdown("<div class='title-style'>🎥 Movie Recommender System</div>", unsafe_allow_html=True)

# Load data
movies = pickle.load(open('movies.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

movie_list = movies['title'].values
selected_movie = st.selectbox("Search or select a movie", movie_list)

if st.button('Show Recommendations'):
    with st.spinner("Fetching recommendations..."):
        try:
            recommendations = recommend(selected_movie)
            if not recommendations:
                st.error("No recommendations found.")
            else:
                st.subheader("Recommended Movies:")
                for movie in recommendations:
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        st.image(movie['poster'], use_container_width=True)
                    with col2:
                        st.markdown(f"<div class='movie-title'>{movie['title']}</div>", unsafe_allow_html=True)
                        if movie['tagline']:
                            st.markdown(f"<div class='movie-tagline'>\"{movie['tagline']}\"</div>", unsafe_allow_html=True)
                        st.markdown(f"⭐ **Rating**: {movie['rating']} | 📅 **Release**: {movie['release_date']}")
                        st.markdown(f"⏱️ **Runtime**: {movie['runtime']} minutes")
                        st.markdown(f"<div class='movie-genres'>🎭 {movie['genres']}</div>", unsafe_allow_html=True)
                        st.markdown(f"📖 **Overview**: {movie['overview']}")
                        if movie['trailer_url']:
                            st.video(movie['trailer_url'])
                        else:
                            st.write("No trailer available.")
                        st.markdown("<hr>", unsafe_allow_html=True)
        except Exception as e:
            st.error(f"An error occurred: {e}")


