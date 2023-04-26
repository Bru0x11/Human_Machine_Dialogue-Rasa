from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

import requests
import tmdbsimple as tmdb

import pandas as pd
import numpy as np
import gensim
from gensim.parsing.preprocessing import preprocess_documents
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
import pickle
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from bs4 import BeautifulSoup
import re
import urllib.request

api_key = "a3d485e7dbba8ea69c0d9041ab46207a"
tmdb.API_KEY = api_key
search = tmdb.Search()

class ActionRetrieveGenre(Action):

    def name(self):
        return 'action_retrieve_genre'
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):
        movie_title = tracker.get_slot("movie_name")
        print(movie_title)
        if movie_title == None:
            dispatcher.utter_message(text = 'We\'re sorry, but there\'s been an error. Could you please specify also the name of the movie in your request?')
            return []

        query = search.movie(query=movie_title)
        print(query)


        movie_id = query.get("results")[0].get("id")
        response = tmdb.Movies(movie_id).info()
        all_movie_genres = response.get("genres")
        result = []
        for i in range(len(all_movie_genres)):
           result.append(str(all_movie_genres[i].get("name")))

        return [SlotSet("genre", result) if result != "" else SlotSet("genre", "No genre listed")]
    
class ShowList(Action):
    def name(self):
        return "action_showlist"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):

        genre_list = tracker.get_slot('genre')
        movie_name = tracker.get_slot('movie_name')

        dispatcher.utter_message(text = 'Sure thing! The genres of {} are:'.format(movie_name))
        for genre in genre_list:
            dispatcher.utter_message(text = '* {}'.format(genre))

class ActionRetrieveReleaseDate(Action):

    def name(self):
        return 'action_retrieve_release_date'
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):
        movie_title = tracker.get_slot("movie_name")
        query = search.movie(query=movie_title)
        movie_id = query.get("results")[0].get("id")
        response = tmdb.Movies(movie_id).info()
        movie_release_date = response.get("release_date")

        return [SlotSet("release_date", movie_release_date) if movie_release_date != None else SlotSet("release_date", "No release_date listed")]

class ActionRetrieveBudget(Action):

    def name(self):
        return 'action_retrieve_budget'
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):
        movie_title = tracker.get_slot("movie_name")
        query = search.movie(query=movie_title)
        movie_id = query.get("results")[0].get("id")
        response = tmdb.Movies(movie_id).info()
        movie_budget = response.get("budget")

        return [SlotSet("budget", movie_budget) if movie_budget != None else SlotSet("budget", "No release_date listed")]

class ActionRetrieveRuntime(Action):

    def name(self):
        return 'action_retrieve_runtime'
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):
        movie_title = tracker.get_slot("movie_name")
        query = search.movie(query=movie_title)
        movie_id = query.get("results")[0].get("id")
        response = tmdb.Movies(movie_id).info()
        movie_runtime = response.get("runtime")

        return [SlotSet("runtime", movie_runtime) if movie_runtime != None else SlotSet("runtime", "No runtime listed")]

class ActionRetrieveRevenue(Action):

    def name(self):
        return 'action_retrieve_revenue'
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):
        movie_title = tracker.get_slot("movie_name")
        query = search.movie(query=movie_title)
        movie_id = query.get("results")[0].get("id")
        response = tmdb.Movies(movie_id).info()
        movie_revenue = response.get("revenue")

        return [SlotSet("revenue", movie_revenue) if movie_revenue != None else SlotSet("revenue", "No revenue listed")]

class ActionRetrievePlot(Action):

    def name(self):
        return 'action_retrieve_plot'
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):
        movie_title = tracker.get_slot("movie_name")
        query = search.movie(query=movie_title)
        movie_id = query.get("results")[0].get("id")
        response = tmdb.Movies(movie_id).info()
        movie_plot = response.get("overview")

        return [SlotSet("plot", movie_plot) if movie_plot != None else SlotSet("plot", "No plot listed")]

class ActionRetrieveRating(Action):

    def name(self):
        return 'action_retrieve_rating'
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):
        movie_title = tracker.get_slot("movie_name")
        query = search.movie(query=movie_title)
        movie_id = query.get("results")[0].get("id")
        response = tmdb.Movies(movie_id).info()
        movie_rating = response.get("vote_average")

        return [SlotSet("rating", movie_rating) if movie_rating != None else SlotSet("rating", "No rating listed")]

class ActionRetrieveComposer(Action):

    def name(self):
        return 'action_retrieve_composer'
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):
        movie_title = tracker.get_slot("movie_name")
        query = search.movie(query=movie_title)
        movie_id = query.get("results")[0].get("id")

        request_url = "https://api.themoviedb.org/3/movie/{}/credits?api_key={}".format(str(movie_id), api_key)
        raw = requests.get(request_url).json()
        composer = []
        for crew_element in raw["crew"]:
            if "Original Music Composer" == crew_element["job"]:
                composer.append(crew_element["name"])  
        
        return [SlotSet("composer_name", composer) if composer != "" else SlotSet("composer_name", "No rating listed")]

class ActionRetrieveDirector(Action):

    def name(self):
        return 'action_retrieve_director'
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):
        movie_title = tracker.get_slot("movie_name")
        query = search.movie(query=movie_title)
        movie_id = query.get("results")[0].get("id")

        request_url = "https://api.themoviedb.org/3/movie/{}/credits?api_key={}".format(str(movie_id), api_key)
        raw = requests.get(request_url).json()
        director = []
        for crew_element in raw["crew"]:
            if "Director" == crew_element["job"]:
                director.append(crew_element["name"])   
        
        return [SlotSet("director_name", director) if director != "" else SlotSet("director_name", "No rating listed")]
    

class ActionRetrieveProducer(Action):

    def name(self):
        return 'action_retrieve_producer'
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):
        movie_title = tracker.get_slot("movie_name")
        query = search.movie(query=movie_title)
        movie_id = query.get("results")[0].get("id")

        request_url = "https://api.themoviedb.org/3/movie/{}/credits?api_key={}".format(str(movie_id), api_key)
        raw = requests.get(request_url).json()
        producer = []
        for crew_element in raw["crew"]:
            if "Producer" == crew_element["job"]:
                producer.append(crew_element["name"])  
        
        return [SlotSet("producer_name", producer) if producer != "" else SlotSet("producer_name", "No rating listed")]
    

class ActionRetrieveCast(Action):

    def name(self):
        return 'action_retrieve_cast'
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):
        movie_title = tracker.get_slot("movie_name")
        actors_amount = tracker.get_slot("number_of_actors")

        try:
            number_of_actors = int(actors_amount)
        except:
            number_of_actors = actors_amount
                
        query = search.movie(query=movie_title)
        movie_id = query.get("results")[0].get("id")

        request_url = "https://api.themoviedb.org/3/movie/{}/credits?api_key={}".format(str(movie_id), api_key)
        raw = requests.get(request_url).json()
        list_of_actors = []
        for cast_element in raw["cast"]:
            list_of_actors.append(cast_element["name"])    
      
        if type(number_of_actors) == int:
            if number_of_actors == 0:
                list_of_actors = list_of_actors[:10]
            elif number_of_actors < len(list_of_actors):
                list_of_actors = list_of_actors[:number_of_actors]
        
        return [SlotSet("cast", list_of_actors) if list_of_actors != "" else SlotSet("cast", "No rating listed")]
    
class ActionRecommendationWithMovie(Action):

    def name(self):
        return 'action_recommendation_with_movie'
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):
        movie_title = tracker.get_slot("movie_name")
        copy_movie_title = tracker.get_slot("copy_of_movie_name")
        index_already_watched = tracker.get_slot("index_already_watched")

        if copy_movie_title != movie_title:
            index_already_watched = 0

        query = search.movie(query=movie_title)
        movie_id = query.get("results")[0].get("id")

        request_url = "https://api.themoviedb.org/3/movie/{}/similar?api_key={}&language=en-US&page=1".format(str(movie_id), api_key)
        raw = requests.get(request_url).json()
        response = raw.get("results")[index_already_watched]

        title = response.get("original_title")
        plot = response.get("overview")
        release_date = response.get("release_date")

        return[SlotSet("movie_name", title), SlotSet("plot", plot), SlotSet("release_date", release_date), SlotSet("index_already_watched", index_already_watched+1), SlotSet("copy_of_movie_name", movie_title)]


class ActionRecommendationWithoutMovie(Action):

    def name(self):
        return 'action_recommendation_without_movie'
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):
        request_url = "https://api.themoviedb.org/3/discover/movie?api_key={}&language=en-US&sort_by=vote_average.desc&include_adult=false&include_video=false&page=1&with_watch_monetization_types=flatrate&vote_count.gte=100".format(api_key)

        genre_dictionary = {
            "action": "28", "adventure": "12", "animation": "16", "comedy": "35", "crime": "80", "documentary": "99", "drama": "18", "family": "10751", "fantasy": "14", "history": "36", "horror": "27",
            "music": "10402", "mistery": "9648", "romance": "10749", "science fiction": "878", "tv movie": "10770", "thriller": "53", "war": "10752", "western": "37"
        }

        retrieve_year = tracker.get_slot("release_date")
        retrieve_is_before = tracker.get_slot("is_before")
        retrieve_is_after = tracker.get_slot("is_after")
        retrieve_is_exactly = tracker.get_slot("is_exactly")
        retrieve_vote = tracker.get_slot("rating")
        retrieve_cast = tracker.get_slot("cast")
        retrieve_director = tracker.get_slot("director_name")

        genre_list = tracker.get_slot("genre")
        retrieve_genre = ""
        if genre_list != None:
            for genre in genre_list:
                retrieve_genre += "{},".format(genre_dictionary.get(genre))        

        if retrieve_year != "Don't ask" and retrieve_year != None:
            if retrieve_is_before != None:
                add_year_gte = "&primary_release_date.lte={}".format(retrieve_year)
                request_url += add_year_gte
            elif retrieve_is_after != None:
                add_year_lte = "&primary_release_date.gte={}".format(retrieve_year)
                request_url += add_year_lte
            elif retrieve_is_exactly != None:
                add_year_lte = "&primary_release_year={}".format(retrieve_year)
                request_url += add_year_lte  
            
        if retrieve_vote!= "Don't ask" and retrieve_vote != None:
            add_vote_average_gte = "&vote_average.gte={}".format(retrieve_vote)
            request_url += add_vote_average_gte

        list_of_actors_id = ""
        if retrieve_cast != "Don't ask" and retrieve_cast != None:
            for actor in retrieve_cast:
                actor = actor.replace(" ", "+")

                website = urllib.request.urlopen('https://www.imdb.com/search/name/?name={}'.format(actor))
                soup = BeautifulSoup(website, 'html.parser')
                actor_id = soup.find_all(href=re.compile("^/name/"))[0]['href'][6:]
                original_id_request_url = "https://api.themoviedb.org/3/find/{}?api_key={}&language=en-US&external_source=imdb_id".format(actor_id, "a3d485e7dbba8ea69c0d9041ab46207a")
                original_id = requests.get(original_id_request_url).json().get("person_results")[0].get('id')
                list_of_actors_id += "{},".format(original_id)

        list_of_directors_id = ""
        if retrieve_director != "Don't ask" and retrieve_director != None:
            for director in retrieve_director:
                director = director.replace(" ", "+")

                website = urllib.request.urlopen('https://www.imdb.com/search/name/?name={}'.format(director))
                soup = BeautifulSoup(website, 'html.parser')
                director_id = soup.find_all(href=re.compile("^/name/"))[0]['href'][6:]
                original_id_request_url = "https://api.themoviedb.org/3/find/{}?api_key={}&language=en-US&external_source=imdb_id".format(director_id, "a3d485e7dbba8ea69c0d9041ab46207a")
                original_id = requests.get(original_id_request_url).json().get("person_results")[0].get('id')
                list_of_directors_id += "{},".format(original_id)

        cast_and_director_ids = list_of_actors_id + list_of_directors_id
        print(cast_and_director_ids)
        if cast_and_director_ids != "":
            add_cast_and_director = "&with_people={}".format(cast_and_director_ids)
            request_url += add_cast_and_director 

        if retrieve_genre != "Don't ask" and retrieve_genre != None:
            add_genre = "&with_genres={}".format(retrieve_genre)
            request_url += add_genre

        print(request_url)
        raw = requests.get(request_url).json()
        response = raw.get("results")[0]

        title = response.get("original_title")
        plot = response.get("overview")
        release_date = response.get("release_date")

        return[SlotSet("movie_name", title), SlotSet("plot", plot), SlotSet("release_date", release_date)]


class ActionResetSlots(Action):

    def name(self):
        return 'action_reset_slots'
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):
         return[SlotSet("plot", None), SlotSet("release_date", None), SlotSet("release_date", None), SlotSet("is_before", None)]
    
class ActionFindMovieWithPlot(Action):

    def name(self):
        return 'action_obtain_movie_from_plot'
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):
        input_plot = tracker.latest_message['text']
        
        movie_dataframe = pd.read_csv('databases/wiki_movie_plots_deduped.csv', sep=',')
        #Filtering the data
        movie_dataframe = movie_dataframe[movie_dataframe['Release Year'] >= 1980]
        movie_dataframe = movie_dataframe[movie_dataframe['Origin/Ethnicity'] == 'American']
        movie_dataframe = movie_dataframe.reset_index()
        all_plots = movie_dataframe['Plot'].values

        use_doc2vec_model = True

        if use_doc2vec_model:

            #processed_plots = preprocess_documents(all_plots)
            #tagged_corpus = [TaggedDocument(d, [i]) for i, d in enumerate(processed_plots)]
            #model = Doc2Vec(tagged_corpus, dm=0, vector_size=200, window=2, min_count=1, epochs=100, hs=1)
            #pickle.dump(model, open('plot_models/doc2vec_model.pkl', 'wb'))

            model = pickle.load(open('plot_models/doc2vec_model.pkl', 'rb'))
            preprocessed_input = gensim.parsing.preprocessing.preprocess_string(input_plot)
            input_vector = model.infer_vector(preprocessed_input)
            similarities = model.docvecs.most_similar(positive = [input_vector])
            
            dispatcher.utter_message(text = "The movies that are similar to your plot are:")
            for similarity in similarities:
                dispatcher.utter_message(text = "{} with a similarity score of {}".format(movie_dataframe['Title'].iloc[similarity[0]], similarity[1]))

            return[SlotSet("movie_name", movie_dataframe['Title'].iloc[similarities[0][0]]),
                   SlotSet("director_name", movie_dataframe['Director'].iloc[similarities[0][0]]),
                   SlotSet("plot", movie_dataframe['Plot'].iloc[similarities[0][0]]),
                   SlotSet("wiki_link", movie_dataframe['Wiki Page'].iloc[similarities[0][0]])
                   ]

        else: #BERT
            model = SentenceTransformer('bert-base-nli-mean-tokens')

            #sentence_embeddings = model.encode(all_plots)
            #pickle.dump(sentence_embeddings, open('plot_models/bert_model.pkl', 'wb'))
            sentence_embeddings = pickle.load(open('plot_models/bert_model.pkl', 'rb'))

            input_embedding = model.encode(input_plot)

            result = cosine_similarity(
                [input_embedding],
                sentence_embeddings[0:]
            )

            movie_index = np.argmax(result)
            print(movie_index)
            print(movie_dataframe['Title'][movie_index])

            return[SlotSet("movie_name", movie_dataframe['Title'][movie_index]),
                   SlotSet("director_name", movie_dataframe['Director'][movie_index]),
                   SlotSet("plot", movie_dataframe['Plot'][movie_index]),
                   SlotSet("wiki_link", movie_dataframe['Wiki Page'][movie_index])
                   ]
        
# class ValidateRetrieveMovieInformationForm(FormValidationAction):
#     def name(self):
#         return "validate_retrieve_movie_information_form"

#     def validate_enable_genre(self, slot_value, dispatcher, tracker, domain):
#             if slot_value == False:
#                 return{"genre": "Don't ask", "enable_release_date": None, "release_date": None, "movie_period": None, "enable_rating": None, "rating": None, "enable_cast": None, "cast": None}
#             else:
#                 return{"enable_genre": slot_value, "enable_release_date": None, "release_date": None, "movie_period": None, "enable_rating": None, "rating": None, "enable_cast": None, "cast": None}
            
#     # def validate_genre(self, slot_value, dispatcher, tracker, domain):
#     #     return{"genre": slot_value, "enable_release_date": None, "release_date": None, "movie_period": None, "enable_rating": None, "rating": None, "enable_cast": None, "cast": None}
            
#     def validate_enable_rating(self, slot_value, dispatcher, tracker, domain):
#             if slot_value == False:
#                 return{"rating": "Don't ask", "enable_cast": None, "cast": None, "enable_release_date": None, "release_date": None}
#             else:
#                 return{"enable_rating": slot_value, "enable_cast": None, "cast": None, "enable_release_date": None, "release_date": None}

#     def validate_enable_cast(self, slot_value, dispatcher, tracker, domain):
#             if slot_value == False:
#                 return{"cast": "Don't ask", "enable_release_date": None, "release_date": None}
#             else:
#                 return{"enable_cast": slot_value, "enable_release_date": None, "release_date": None}
            
#     def validate_enable_release_date(self, slot_value, dispatcher, tracker, domain):
#         if slot_value == False:
#             return{"release_date": "Don't ask", "movie_period": "Don't ask"}
#         else:
#             return{"enable_release_date": slot_value}
        

