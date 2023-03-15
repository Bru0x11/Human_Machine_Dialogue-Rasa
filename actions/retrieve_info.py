"""
Use the API provided to obtain all the necessary information from the dataset.
Use this API to query the KB.
"""

import requests
import tmdbsimple as tmdb

tmdb.API_KEY = "a3d485e7dbba8ea69c0d9041ab46207a"
search = tmdb.Search()
movie_title = "Scream"
query = search.movie(query=movie_title)
movie_id = query.get("results")[0].get("id")

request_url = "https://api.themoviedb.org/3/movie/{}/similar?api_key={}&language=en-US&page=1".format(str(movie_id), "a3d485e7dbba8ea69c0d9041ab46207a")
raw = requests.get(request_url).json()
response = raw.get("results")[0]
title = response.get("original_title")
plot = response.get("overview")
release_date = response.get("release_date")
print(title, plot, release_date)
