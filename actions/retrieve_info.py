"""
Use the API provided by IMBD to obtain all the necessary information from the dataset.
Use this API to query the KB.
"""

import imdb

moviesDB = imdb.IMDB()

print(dir(moviesDB))