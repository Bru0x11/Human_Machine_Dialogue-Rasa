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
request_url = "https://api.themoviedb.org/3/discover/movie?api_key={}&language=en-US&sort_by=popularity.desc&include_adult=false&include_video=false&page=1&with_watch_monetization_types=flatrate".format("a3d485e7dbba8ea69c0d9041ab46207a")

# prova = "https://api.themoviedb.org/3/genre/movie/list?api_key={}&language=en-US".format("a3d485e7dbba8ea69c0d9041ab46207a")
# raw = requests.get(prova).json()
# print(raw)

retrieve_year_gte = None
retrieve_year_lte = "2012"
retrieve_exact_year = None
retrieve_vote_gte = None
retrieve_vote_lte = None
retrieve_cast = None
retrieve_genre = "27"
retrieve_runtime_gte = "100"
retrieve_runtime_lte = None

if retrieve_year_gte != None:
    add_year_gte = "&primary_release_date.gte={}".format(retrieve_year_gte)
    request_url += add_year_gte

if retrieve_year_lte != None:
    add_year_lte = "&primary_release_date.lte={}".format(retrieve_year_lte)
    request_url += add_year_lte

if retrieve_exact_year != None:
    add_exact_year = "&primary_release_yeaer={}".format(retrieve_exact_year)
    request_url += add_exact_year

if retrieve_vote_gte != None:
    add_vote_average_gte = "&vote_average.gte={}".format(retrieve_vote_gte)
    request_url += add_vote_average_gte

if retrieve_vote_lte != None:
    add_vote_average_lte = "&vote_average.lte={}".format(retrieve_vote_lte)
    request_url += add_vote_average_lte

if retrieve_cast != None:
    add_cast = "&with_cast={}".format(retrieve_cast)
    request_url += add_cast

if retrieve_genre != None:
    add_genre = "&with_genres={}".format(retrieve_genre)
    request_url += add_genre

if retrieve_runtime_gte != None:
    add_runtime_gte = "&with_runtime.gte={}".format(retrieve_runtime_gte)
    request_url += add_runtime_gte

if retrieve_runtime_lte != None:
    add_runtime_lte = "&with_runtime.lte={}".format(retrieve_runtime_lte)
    request_url += add_runtime_lte



raw = requests.get(request_url).json()
print(raw)
