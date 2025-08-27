import requests
from bs4 import BeautifulSoup
import requests
import os

# Insert your TMDb API key here
TMDB_API_KEY = "93a9fdedc62d8a573c54b7fb94606206"
POSTERS_DIR = "./frontend/posters_raw"
TMDB_API_URL = f"https://api.themoviedb.org/3/movie/top_rated?api_key={TMDB_API_KEY}&language=en-US&page=1"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w600_and_h900_bestv2"

def download_posters():
    os.makedirs(POSTERS_DIR, exist_ok=True)
    response = requests.get(TMDB_API_URL)
    if response.status_code != 200:
        print("Error fetching data from TMDb. Check your API key.")
        return
    data = response.json()
    movies = data.get("results", [])[:20]
    print(f"Found {len(movies)} movies. Downloading posters...")
    for idx, movie in enumerate(movies, 1):
        title = movie.get("title", f"Movie_{idx}")
        poster_path = movie.get("poster_path")
        if poster_path:
            poster_url = f"{TMDB_IMAGE_BASE}{poster_path}"
            img_data = requests.get(poster_url).content
            filename = f"{idx:02d}_{title.replace(' ', '_').replace('/', '-')}.jpg"
            filepath = os.path.join(POSTERS_DIR, filename)
            with open(filepath, "wb") as f:
                f.write(img_data)
            print(f"Downloaded: {title}")
        else:
            print(f"No poster found for: {title}")
    print("Done.")

if __name__ == "__main__":
    print("""
To run this script:
1. Get a free TMDb API key: https://www.themoviedb.org/settings/api
2. Paste your API key into the TMDB_API_KEY variable in this script.
3. Create a virtual environment:
   python3 -m venv venv
4. Activate the environment:
   source venv/bin/activate
5. Install requirements:
   pip install requests
6. Run the script:
   python download_imdb_posters.py
""")
    download_posters()