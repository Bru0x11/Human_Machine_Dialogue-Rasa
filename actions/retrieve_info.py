# """
# Use the API provided to obtain all the necessary information from the dataset.
# Use this API to query the KB.
# """
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

import requests
import tmdbsimple as tmdb

import pandas as pd
import numpy as np
import random
import gensim
from gensim.parsing.preprocessing import preprocess_documents
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
import pickle
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from bs4 import BeautifulSoup
import re
import urllib.request
import faiss
import gc

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

import requests
import tmdbsimple as tmdb

import pandas as pd
import numpy as np
import random
import gensim
from gensim.parsing.preprocessing import preprocess_documents
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
import pickle
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from bs4 import BeautifulSoup
import re
import urllib.request

from pprint import pprint
import time

# tmdb.API_KEY = "a3d485e7dbba8ea69c0d9041ab46207a"
# search = tmdb.Search()
# movie_title = "Scream"
# query = search.movie(query=movie_title)
# movie_id = query.get("results")[0].get("id")
# request_url = "https://api.themoviedb.org/3/discover/movie?api_key={}&language=en-US&sort_by=vote_average.desc&include_adult=false&include_video=false&page=1&with_watch_monetization_types=flatrate&vote_count.gte=100".format("a3d485e7dbba8ea69c0d9041ab46207a")

# genre_dictionary = {
#     "action": "28", "adventure": "12", "animation": "16", "comedy": "35", "crime": "80", "documentary": "99", "drama": "18", "family": "10751", "fantasy": "14", "history": "36", "horror": "27",
#     "music": "10402", "mistery": "9648", "romance": "10749", "science fiction": "878", "tv movie": "10770", "thriller": "53", "war": "10752", "western": "37"
# }

# retrieve_vote_lte = None

# retrieve_year_gte = None
# retrieve_year_lte = None
# retrieve_exact_year = None
# retrieve_vote_gte = None
# retrieve_genre = None #genre_dictionary.get("fantasy")

# retrieve_runtime_gte = None
# retrieve_runtime_lte = None
# retrieve_cast = "Johnny Depp"
# retrieve_director = "Tim Burton"

# if retrieve_year_gte != None:
#     add_year_gte = "&primary_release_date.gte={}".format(retrieve_year_gte)
#     request_url += add_year_gte

# if retrieve_year_lte != None:
#     add_year_lte = "&primary_release_date.lte={}".format(retrieve_year_lte)
#     request_url += add_year_lte

# if retrieve_exact_year != None:
#     add_exact_year = "&primary_release_year={}".format(retrieve_exact_year)
#     request_url += add_exact_year

# if retrieve_vote_gte != None:
#     add_vote_average_gte = "&vote_average.gte={}".format(retrieve_vote_gte)
#     request_url += add_vote_average_gte

# if retrieve_vote_lte != None:
#     add_vote_average_lte = "&vote_average.lte={}".format(retrieve_vote_lte)
#     request_url += add_vote_average_lte

# if retrieve_cast != None:

#     actor = retrieve_cast.replace(" ", "+")

#     website = urllib.request.urlopen('https://www.imdb.com/search/name/?name={}'.format(actor))
#     soup = BeautifulSoup(website, 'html.parser')
#     actor_id = soup.find_all(href=re.compile("^/name/"))[0]['href'][6:]
#     original_id_request_url = "https://api.themoviedb.org/3/find/{}?api_key={}&language=en-US&external_source=imdb_id".format(actor_id, "a3d485e7dbba8ea69c0d9041ab46207a")
#     original_id = requests.get(original_id_request_url).json().get("person_results")[0].get('id')

#     add_cast = "&with_cast={}".format(original_id)
#     request_url += add_cast

# if retrieve_genre != None:
#     add_genre = "&with_genres={}".format(retrieve_genre)
#     request_url += add_genre

# if retrieve_director != None:
#     director = retrieve_director.replace(" ", "+")

#     website = urllib.request.urlopen('https://www.imdb.com/search/name/?name={}'.format(director))
#     soup = BeautifulSoup(website, 'html.parser')
#     director_id = soup.find_all(href=re.compile("^/name/"))[0]['href'][6:]
#     original_id_request_url = "https://api.themoviedb.org/3/find/{}?api_key={}&language=en-US&external_source=imdb_id".format(director_id, "a3d485e7dbba8ea69c0d9041ab46207a")
#     original_id = requests.get(original_id_request_url).json().get("person_results")[0].get('id')

#     add_crew = "&with_crew={}".format(original_id)
#     request_url += add_crew

# print(request_url)
# raw = requests.get("https://api.themoviedb.org/3/discover/movie?api_key=a3d485e7dbba8ea69c0d9041ab46207a&language=en-US&sort_by=vote_average.desc&include_adult=false&include_video=false&page=1&with_watch_monetization_types=flatrate&vote_count.gte=100&with_people=510,85,").json()
# print(raw)





# movie_dataframe = pd.read_csv('databases/movies_metadata.csv', sep=',')
# #Filtering the data
# all_plots = movie_dataframe['overview'].values
# for i in range(0, len(all_plots)):
#     all_plots[i] = str(all_plots[i])

# input_plot = "toys named Buz and Woody belonging to a young boy named Andy."

# use_doc2vec_model = False
# if use_doc2vec_model:
#     # print("INSIDE")
#     # processed_plots = preprocess_documents(all_plots)
#     # tagged_corpus = [TaggedDocument(d, [i]) for i, d in enumerate(processed_plots)]
#     # print("TRAINING")
#     # model = Doc2Vec(tagged_corpus, dm=0, vector_size=200, window=2, min_count=1, epochs=100, hs=1)
#     # print("SAVING MODEL")
#     # pickle.dump(model, open('plot_models/prova_d2v_model.pkl', 'wb'))
#     # print("DONE")

#     model = pickle.load(open('plot_models/prova_d2v_model.pkl', 'rb'))
#     preprocessed_input = gensim.parsing.preprocessing.preprocess_string(input_plot)
#     input_vector = model.infer_vector(preprocessed_input)
#     similarities = model.docvecs.most_similar(positive = [input_vector])
    
#     #dispatcher.utter_message(text = "The movies that are similar to your plot are:")
#     for similarity in similarities:
#         #dispatcher.utter_message(text = "{} with a similarity score of {}".format(movie_dataframe['Title'].iloc[similarity[0]], similarity[1]))
#         print("{} with a similarity score of {}".format(movie_dataframe['original_title'].iloc[similarity[0]], similarity[1]))

#     # return[SlotSet("movie_name", movie_dataframe['Title'].iloc[similarities[0][0]]),
#     #         SlotSet("director_name", movie_dataframe['Director'].iloc[similarities[0][0]]),
#     #         SlotSet("plot", movie_dataframe['Plot'].iloc[similarities[0][0]]),
#     #         SlotSet("wiki_link", movie_dataframe['Wiki Page'].iloc[similarities[0][0]])
#     #         ]

# else: #BERT
#     model = SentenceTransformer('bert-base-nli-mean-tokens')

#     sentence_embeddings = model.encode(all_plots)
#     pickle.dump(sentence_embeddings, open('plot_models/prova_bert_model.pkl', 'wb'))
#     sentence_embeddings = pickle.load(open('plot_models/prova_bert_model.pkl', 'rb'))

#     input_embedding = model.encode(input_plot)

#     result = cosine_similarity(
#         [input_embedding],
#         sentence_embeddings[0:]
#     )

#     movie_index = np.argmax(result)
#     print(movie_index)
#     print(movie_dataframe['original_title'][movie_index])

#     # return[SlotSet("movie_name", movie_dataframe['Title'][movie_index]),
#     #         SlotSet("director_name", movie_dataframe['Director'][movie_index]),
#     #         SlotSet("plot", movie_dataframe['Plot'][movie_index]),
#     #         SlotSet("wiki_link", movie_dataframe['Wiki Page'][movie_index])
#     #         ]



# class prova():

#     def validate_is_plot_received(self):
#             input_plot = "In the arcade night the videogame characters leave their games. The protagonist is a girl from a candy racing game who glitches"
#             data = pd.read_csv('databases/wiki_movie_plots_deduped.csv', memory_map=True)
#             data.info() 
#             df = data[['Title','Plot']]
#             del data
#             gc.collect()
#             df.dropna(inplace=True)
#             df.drop_duplicates(subset=['Plot'],inplace=True)
#             model = SentenceTransformer('task3_tools/fine_tuned_model')
#             index = faiss.read_index('task3_tools/fine_tuned_encoding.index')
#             results = self.search(input_plot, top_k=5, index=index, model=model, movie_dataframe=df)
#             print("\n")
#             for result in results:
#                 print('\t',result)
#             return 
        
#     def fetch_movie_info(self, dataframe_idx, movie_dataframe):
#         info = movie_dataframe.iloc[dataframe_idx]
#         meta_dict = {}
#         meta_dict['Title'] = info['Title']
#         return meta_dict
        
#     def search(self, query, top_k, index, model, movie_dataframe):
#         t=time.time()
#         query_vector = model.encode([query])
#         top_k = index.search(query_vector, top_k)
#         print('>>>> Results in Total Time: {}'.format(time.time()-t))
#         top_k_ids = top_k[1].tolist()[0]
#         top_k_ids = list(np.unique(top_k_ids))
#         results =  [self.fetch_movie_info(idx, movie_dataframe) for idx in top_k_ids]
#         return results

# item = prova()
# item.validate_is_plot_received()


