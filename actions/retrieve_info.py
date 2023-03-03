"""
Use the API provided to obtain all the necessary information from the dataset.
Use this API to query the KB.
"""

import requests
import tmdbsimple as tmdb

tmdb.API_KEY = "a3d485e7dbba8ea69c0d9041ab46207a"
movie = tmdb.Movies(603)
search = tmdb.Search()
response = movie.info()
query = search.movie(query='Tomb Raider')
print(query)
