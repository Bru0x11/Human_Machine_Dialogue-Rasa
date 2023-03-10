"""
Use the API provided to obtain all the necessary information from the dataset.
Use this API to query the KB.
"""

import requests
import tmdbsimple as tmdb

tmdb.API_KEY = "a3d485e7dbba8ea69c0d9041ab46207a"
movie = tmdb.Movies()
search = tmdb.Search()
genres = tmdb.Genres()

query = search.movie(query="Scream")
movie_id = query.get("results")[0].get("id")
print(movie_id)
response = tmdb.Movies(movie_id).info()
print(response)
all_movie_genres = response.get("producer")
print(all_movie_genres)

