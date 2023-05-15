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

api_key = "a3d485e7dbba8ea69c0d9041ab46207a"
tmdb.API_KEY = api_key
search = tmdb.Search()


class ActionKeepAsking(Action):
    
    def name(self):
        return 'action_keep_asking'
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):
        movie_title = tracker.get_slot("movie_name")

        # If no error has occured previously I can say to keep asking things related to the movies
        if movie_title != None:
            choose_question = random.randint(0, 3)
            if choose_question == 0:
                dispatcher.utter_message(text = 'Do you want to know something else about {} or other films?'.format(movie_title))
            elif choose_question == 1:
                dispatcher.utter_message(text = 'Are there any other questions you have about {} or other movies?'.format(movie_title))
            elif choose_question == 2:
                dispatcher.utter_message(text = 'Is there anything else you\'d like to know about {} or other films?'.format(movie_title))
            elif choose_question == 3:
                dispatcher.utter_message(text = 'Would you like me to provide additional information about {} or other movies?'.format(movie_title))

class ActionResetIsInsideRules(Action):
    
    def name(self):
        return 'action_reset_is_inside_rules'
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):
        return[SlotSet('is_inside_rules', None), SlotSet('keep_asking', None)]

class ActionRetrieveGenre(Action):

    def name(self):
        return 'action_retrieve_genre'
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):
        movie_title = tracker.get_slot("movie_name")
        
        # If you don't specify the name in the request, it raises an error and you have to make the request again.
        if movie_title == None:
            dispatcher.utter_message(text = 'I\'m sorry, but there\'s been an error. Could you please specify also the name of the movie in your request?')
            return []
        
        query = search.movie(query=movie_title)

        # Check if the movie exists or there is a type in the title
        total_results = query.get("total_results")
        if total_results == 0:
            dispatcher.utter_message(text = 'I apologize, but it seems that the film you\'re looking for either doesn\'t exist or there might have been a typo. Could you please provide the title again?')
            # Reset slot movie_name to None
            return [SlotSet("movie_name", None)]

        movie_id = query.get("results")[0].get("id")
        response = tmdb.Movies(movie_id).info()
        all_movie_genres = response.get("genres")
        result = []
        for i in range(len(all_movie_genres)):
           result.append(str(all_movie_genres[i].get("name")))

        return [SlotSet("genre", result), SlotSet("is_inside_rules", True)]
    
class ShowGenre(Action):
    def name(self):
        return "action_show_genre"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):

        genre_list = tracker.get_slot('genre')
        movie_name = tracker.get_slot('movie_name')

        if genre_list != [] and movie_name != None:
            dispatcher.utter_message(text = 'The genres of {} are:'.format(movie_name))
            for genre in genre_list:
                dispatcher.utter_message(text = '* {}'.format(genre))

            # Reset the genre slot to []. This is helpful whenever we ask a question related to another movie and we have some errors with it.
            # If we don't do so, the bot will print the genres of the previous movie.
            return [SlotSet("genre", [])]

class ActionRetrieveReleaseDate(Action):

    def name(self):
        return 'action_retrieve_release_date'
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):
        movie_title = tracker.get_slot("movie_name")
        
        # If you don't specify the name in the request, it raises an error and you have to make the request again.
        if movie_title == None:
            dispatcher.utter_message(text = 'I\'m sorry, but there\'s been an error. Could you please specify also the name of the movie in your request?')
            return []
               
        query = search.movie(query=movie_title)

        # Check if the movie exists or there is a type in the title
        total_results = query.get("total_results")
        if total_results == 0:
            dispatcher.utter_message(text = 'I apologize, but it seems that the film you\'re looking for either doesn\'t exist or there might have been a typo. Could you please provide the title again?')
            # Reset slot movie_name to None
            return [SlotSet("movie_name", None)]
        
        movie_id = query.get("results")[0].get("id")

        response = tmdb.Movies(movie_id).info()
        movie_release_date = response.get("release_date")

        return [SlotSet("release_date", movie_release_date), SlotSet("is_inside_rules", True)]
    
class ShowReleaseDate(Action):
    def name(self):
        return "action_show_release_date"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):

        release_date = tracker.get_slot('release_date')
        movie_name = tracker.get_slot('movie_name')

        if release_date != None and movie_name != None:
            choose_message = random.randint(0, 3)
            if choose_message == 0:
                dispatcher.utter_message(text = 'The release date of the movie {} is {}.'.format(movie_name, release_date))
            elif choose_message == 1:
                dispatcher.utter_message(text = '{} premiered on {}.'.format(movie_name, release_date))
            elif choose_message == 2:
                dispatcher.utter_message(text = '{} made its debut on {}.'.format(movie_name, release_date))
            elif choose_message == 3:
                dispatcher.utter_message(text = '{} was first shown to audiences on {}.'.format(movie_name, release_date))

            return [SlotSet("release_date", None)]

class ActionRetrieveBudget(Action):

    def name(self):
        return 'action_retrieve_budget'
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):
        movie_title = tracker.get_slot("movie_name")
        
        # If you don't specify the name in the request, it raises an error and you have to make the request again.
        if movie_title == None:
            dispatcher.utter_message(text = 'I\'m sorry, but there\'s been an error. Could you please specify also the name of the movie in your request?')
            return []
               
        query = search.movie(query=movie_title)

        # Check if the movie exists or there is a type in the title
        total_results = query.get("total_results")
        if total_results == 0:
            dispatcher.utter_message(text = 'I apologize, but it seems that the film you\'re looking for either doesn\'t exist or there might have been a typo. Could you please provide the title again?')
            # Reset slot movie_name to None
            return [SlotSet("movie_name", None)]
        
        movie_id = query.get("results")[0].get("id")

        response = tmdb.Movies(movie_id).info()
        movie_budget = response.get("budget")

        return [SlotSet("budget", movie_budget), SlotSet("is_inside_rules", True)]
    
class ShowBudget(Action):
    def name(self):
        return "action_show_budget"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):

        budget = tracker.get_slot('budget')
        movie_name = tracker.get_slot('movie_name')

        if budget != None and movie_name != None:
            choose_message = random.randint(0, 3)
            if choose_message == 0:
                dispatcher.utter_message(text = 'The total budget for {} is {}.'.format(movie_name, budget))
            elif choose_message == 1:
                dispatcher.utter_message(text = 'The overall budget for {} amounts to {}.'.format(movie_name, budget))
            elif choose_message == 2:
                dispatcher.utter_message(text = '{} has a budget of {} in total.'.format(movie_name, budget))
            elif choose_message == 3:
                dispatcher.utter_message(text = '{} is the complete budget allocated for producing {}.'.format(budget, movie_name))

            return [SlotSet("budget", None)]

class ActionRetrieveRuntime(Action):

    def name(self):
        return 'action_retrieve_runtime'
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):
        movie_title = tracker.get_slot("movie_name")
        
        # If you don't specify the name in the request, it raises an error and you have to make the request again.
        if movie_title == None:
            dispatcher.utter_message(text = 'I\'m sorry, but there\'s been an error. Could you please specify also the name of the movie in your request?')
            return []
               
        query = search.movie(query=movie_title)

        # Check if the movie exists or there is a type in the title
        total_results = query.get("total_results")
        if total_results == 0:
            dispatcher.utter_message(text = 'I apologize, but it seems that the film you\'re looking for either doesn\'t exist or there might have been a typo. Could you please provide the title again?')
            # Reset slot movie_name to None
            return [SlotSet("movie_name", None)]
        
        movie_id = query.get("results")[0].get("id")

        response = tmdb.Movies(movie_id).info()
        movie_runtime = response.get("runtime")

        return [SlotSet("runtime", movie_runtime), SlotSet("is_inside_rules", True)]
    
class ShowRuntime(Action):
    def name(self):
        return "action_show_runtime"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):

        runtime = tracker.get_slot('runtime')
        movie_name = tracker.get_slot('movie_name')

        if runtime != None and movie_name != None:
            choose_message = random.randint(0, 3)
            if choose_message == 0:
                dispatcher.utter_message(text = 'The {} lasts {} minutes'.format(movie_name, runtime))
            elif choose_message == 1:
                dispatcher.utter_message(text = 'The duration of {} is {} minutes.'.format(movie_name, runtime))
            elif choose_message == 2:
                dispatcher.utter_message(text = '{} has a runtime of {} minutes.'.format(movie_name, runtime))
            elif choose_message == 3:
                dispatcher.utter_message(text = '{} minutes is the length of {}.'.format(runtime, movie_name))

            return [SlotSet("runtime", None)]


class ActionRetrieveRevenue(Action):

    def name(self):
        return 'action_retrieve_revenue'
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):
        movie_title = tracker.get_slot("movie_name")
        
        # If you don't specify the name in the request, it raises an error and you have to make the request again.
        if movie_title == None:
            dispatcher.utter_message(text = 'I\'m sorry, but there\'s been an error. Could you please specify also the name of the movie in your request?')
            return []
               
        query = search.movie(query=movie_title)

        # Check if the movie exists or there is a type in the title
        total_results = query.get("total_results")
        if total_results == 0:
            dispatcher.utter_message(text = 'I apologize, but it seems that the film you\'re looking for either doesn\'t exist or there might have been a typo. Could you please provide the title again?')
            # Reset slot movie_name to None
            return [SlotSet("movie_name", None)]
        
        movie_id = query.get("results")[0].get("id")

        response = tmdb.Movies(movie_id).info()
        movie_revenue = response.get("revenue")

        return [SlotSet("revenue", movie_revenue), SlotSet("is_inside_rules", True)]
    
class ShowRevenue(Action):
    def name(self):
        return "action_show_revenue"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):

        revenue = tracker.get_slot('revenue')
        movie_name = tracker.get_slot('movie_name')

        if revenue != None and movie_name != None:
            choose_message = random.randint(0, 3)
            if choose_message == 0:
                dispatcher.utter_message(text = 'The revenue of {} amounts to {}.'.format(movie_name, revenue))
            elif choose_message == 1:
                dispatcher.utter_message(text = '{} earned {} in revenue.'.format(movie_name, revenue))
            elif choose_message == 2:
                dispatcher.utter_message(text = 'The total revenue generated by {} is {}.'.format(movie_name, revenue))
            elif choose_message == 3:
                dispatcher.utter_message(text = '{} is the amount of money {} made in revenue.'.format(revenue, movie_name))

            return [SlotSet("revenue", None)]

class ActionRetrievePlot(Action):

    def name(self):
        return 'action_retrieve_plot'
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):
        movie_title = tracker.get_slot("movie_name")
        
        # If you don't specify the name in the request, it raises an error and you have to make the request again.
        if movie_title == None:
            dispatcher.utter_message(text = 'I\'m sorry, but there\'s been an error. Could you please specify also the name of the movie in your request?')
            return []
               
        query = search.movie(query=movie_title)

        # Check if the movie exists or there is a type in the title
        total_results = query.get("total_results")
        if total_results == 0:
            dispatcher.utter_message(text = 'I apologize, but it seems that the film you\'re looking for either doesn\'t exist or there might have been a typo. Could you please provide the title again?')
            # Reset slot movie_name to None
            return [SlotSet("movie_name", None)]
        
        movie_id = query.get("results")[0].get("id")

        response = tmdb.Movies(movie_id).info()
        movie_plot = response.get("overview")

        return [SlotSet("plot", movie_plot), SlotSet("is_inside_rules", True)]
    
class ShowPlot(Action):
    def name(self):
        return "action_show_plot"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):

        plot = tracker.get_slot('plot')
        movie_name = tracker.get_slot('movie_name')

        if plot != None and movie_name != None:
            choose_message = random.randint(0, 2)
            if choose_message == 0:
                dispatcher.utter_message(text = 'The plot of {} is the following: {}.'.format(movie_name, plot))
            elif choose_message == 1:
                dispatcher.utter_message(text = '{} can be summarized with the following plot: {}.'.format(movie_name, plot))
            elif choose_message == 2:
                dispatcher.utter_message(text = 'The storyline of {} is described as: {}.'.format(movie_name, plot))

            return [SlotSet("plot", None)]

class ActionRetrieveRating(Action):

    def name(self):
        return 'action_retrieve_rating'
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):
        movie_title = tracker.get_slot("movie_name")
        
        # If you don't specify the name in the request, it raises an error and you have to make the request again.
        if movie_title == None:
            dispatcher.utter_message(text = 'I\'m sorry, but there\'s been an error. Could you please specify also the name of the movie in your request?')
            return []
               
        query = search.movie(query=movie_title)

        # Check if the movie exists or there is a type in the title
        total_results = query.get("total_results")
        if total_results == 0:
            dispatcher.utter_message(text = 'I apologize, but it seems that the film you\'re looking for either doesn\'t exist or there might have been a typo. Could you please provide the title again?')
            # Reset slot movie_name to None
            return [SlotSet("movie_name", None)]
        
        movie_id = query.get("results")[0].get("id")

        response = tmdb.Movies(movie_id).info()
        movie_rating = response.get("vote_average")

        return [SlotSet("rating", movie_rating), SlotSet("is_inside_rules", True)]
    
class ShowRating(Action):
    def name(self):
        return "action_show_rating"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):

        rating = tracker.get_slot('rating')
        movie_name = tracker.get_slot('movie_name')

        if rating != None and movie_name != None:
            choose_message = random.randint(0, 3)
            if choose_message == 0:
                dispatcher.utter_message(text = 'The rating of {} is {}.'.format(movie_name, rating))
            elif choose_message == 1:
                dispatcher.utter_message(text = '{} has a rating of {}.'.format(movie_name, rating))
            elif choose_message == 2:
                dispatcher.utter_message(text = 'The assigned rating for {} is {}.'.format(movie_name, rating))
            elif choose_message == 3:
                dispatcher.utter_message(text = '{} is the rating given to {}.'.format(rating, movie_name))

            return [SlotSet("rating", None)]

class ActionRetrieveComposer(Action):

    def name(self):
        return 'action_retrieve_composer'
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):
        movie_title = tracker.get_slot("movie_name")
        
        # If you don't specify the name in the request, it raises an error and you have to make the request again.
        if movie_title == None:
            dispatcher.utter_message(text = 'I\'m sorry, but there\'s been an error. Could you please specify also the name of the movie in your request?')
            return []
        
        query = search.movie(query=movie_title)

        # Check if the movie exists or there is a type in the title
        total_results = query.get("total_results")
        if total_results == 0:
            dispatcher.utter_message(text = 'I apologize, but it seems that the film you\'re looking for either doesn\'t exist or there might have been a typo. Could you please provide the title again?')
            # Reset slot movie_name to None
            return [SlotSet("movie_name", None)]
        
        movie_id = query.get("results")[0].get("id")

        request_url = "https://api.themoviedb.org/3/movie/{}/credits?api_key={}".format(str(movie_id), api_key)
        raw = requests.get(request_url).json()
        composer = []
        for crew_element in raw["crew"]:
            if "Original Music Composer" == crew_element["job"]:
                composer.append(crew_element["name"])  
        
        return [SlotSet("composer_name", composer), SlotSet("is_inside_rules", True)]
    
class ShowComposer(Action):
    def name(self):
        return "action_show_composer"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):

        composer_list = tracker.get_slot('composer_name')
        number_of_composers = len(composer_list)
        movie_name = tracker.get_slot('movie_name')

        if composer_list != [] and movie_name != None:
            if number_of_composers > 1:
                dispatcher.utter_message(text = 'The composers of {} are:'.format(movie_name))
                for composer in composer_list:
                    dispatcher.utter_message(text = '* {}'.format(composer))
            else:
                dispatcher.utter_message(text = 'The composer of {} is {}.'.format(movie_name, composer_list[0]))
            
            return [SlotSet("composer_name", [])]

class ActionRetrieveDirector(Action):

    def name(self):
        return 'action_retrieve_director'
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):
        movie_title = tracker.get_slot("movie_name")
        
        # If you don't specify the name in the request, it raises an error and you have to make the request again.
        if movie_title == None:
            dispatcher.utter_message(text = 'I\'m sorry, but there\'s been an error. Could you please specify also the name of the movie in your request?')
            return []
        
        query = search.movie(query=movie_title)

        # Check if the movie exists or there is a type in the title
        total_results = query.get("total_results")
        if total_results == 0:
            dispatcher.utter_message(text = 'I apologize, but it seems that the film you\'re looking for either doesn\'t exist or there might have been a typo. Could you please provide the title again?')
            # Reset slot movie_name to None
            return [SlotSet("movie_name", None)]
        
        movie_id = query.get("results")[0].get("id")

        request_url = "https://api.themoviedb.org/3/movie/{}/credits?api_key={}".format(str(movie_id), api_key)
        raw = requests.get(request_url).json()
        director = []
        for crew_element in raw["crew"]:
            if "Director" == crew_element["job"]:
                director.append(crew_element["name"])   
        
        return [SlotSet("director_name", director), SlotSet("is_inside_rules", True)]
    
class ShowDirector(Action):
    def name(self):
        return "action_show_director"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):

        directors_list = tracker.get_slot('director_name')
        number_of_directors = len(directors_list)
        movie_name = tracker.get_slot('movie_name')

        if directors_list != [] and movie_name != None:
            if number_of_directors > 1:
                dispatcher.utter_message(text = 'The directors of {} are:'.format(movie_name))
                for director in directors_list:
                    dispatcher.utter_message(text = '* {}'.format(director))
            else:
                dispatcher.utter_message(text = 'The director of {} is {}.'.format(movie_name, directors_list[0]))

            return [SlotSet("director_name", [])]
    
class ActionRetrieveProducer(Action):

    def name(self):
        return 'action_retrieve_producer'
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):
        movie_title = tracker.get_slot("movie_name")
        
        # If you don't specify the name in the request, it raises an error and you have to make the request again.
        if movie_title == None:
            dispatcher.utter_message(text = 'I\'m sorry, but there\'s been an error. Could you please specify also the name of the movie in your request?')
            return []
        
        query = search.movie(query=movie_title)

        # Check if the movie exists or there is a type in the title
        total_results = query.get("total_results")
        if total_results == 0:
            dispatcher.utter_message(text = 'I apologize, but it seems that the film you\'re looking for either doesn\'t exist or there might have been a typo. Could you please provide the title again?')
            # Reset slot movie_name to None
            return [SlotSet("movie_name", None)]
        
        movie_id = query.get("results")[0].get("id")

        request_url = "https://api.themoviedb.org/3/movie/{}/credits?api_key={}".format(str(movie_id), api_key)
        raw = requests.get(request_url).json()
        producer = []
        for crew_element in raw["crew"]:
            if "Producer" == crew_element["job"]:
                producer.append(crew_element["name"])  
        
        return [SlotSet("producer_name", producer), SlotSet("is_inside_rules", True)]
    
class ShowProducer(Action):
    def name(self):
        return "action_show_producer"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):

        producers_list = tracker.get_slot('producer_name')
        number_of_producers = len(producers_list)
        movie_name = tracker.get_slot('movie_name')

        if producers_list != [] and movie_name != None:
            if number_of_producers > 1:
                dispatcher.utter_message(text = 'The producers of {} are:'.format(movie_name))
                for producer in producers_list:
                    dispatcher.utter_message(text = '* {}'.format(producer))
            else:
                dispatcher.utter_message(text = 'The producer of {} is {}.'.format(movie_name, producers_list[0]))

            return [SlotSet("producer_name", [])]
    
class ActionRetrieveCast(Action):

    def name(self):
        return 'action_retrieve_cast'
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):
        movie_title = tracker.get_slot("movie_name")
        
        # If you don't specify the name in the request, it raises an error and you have to make the request again.
        if movie_title == None:
            dispatcher.utter_message(text = 'I\'m sorry, but there\'s been an error. Could you please specify also the name of the movie in your request?')
            return []
        
        query = search.movie(query=movie_title)

        # Check if the movie exists or there is a type in the title
        total_results = query.get("total_results")
        if total_results == 0:
            dispatcher.utter_message(text = 'I apologize, but it seems that the film you\'re looking for either doesn\'t exist or there might have been a typo. Could you please provide the title again?')
            # Reset slot movie_name to None
            return [SlotSet("movie_name", None)]
        
        actors_amount = tracker.get_slot("number_of_actors")
        try:
            number_of_actors = int(actors_amount)
        except:
            number_of_actors = actors_amount
                
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
        
        return [SlotSet("cast", list_of_actors), SlotSet("is_inside_rules", True)]
    
class ShowCast(Action):
    def name(self):
        return "action_show_cast"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):

        cast_list = tracker.get_slot('cast')
        movie_name = tracker.get_slot('movie_name')
        number_of_actors = tracker.get_slot('number_of_actors')
        try:
            number_of_actors = int(number_of_actors)
        except:
            number_of_actors = number_of_actors

        if cast_list != [] and movie_name != None:
            if number_of_actors != None:
                dispatcher.utter_message(text = 'Here is the list for the movie {} of {} actors:'.format(movie_name, number_of_actors))
                for cast in cast_list:
                    dispatcher.utter_message(text = '* {}'.format(cast))
            else:
                dispatcher.utter_message(text = 'Here is the list of actors for the movie {}:'.format(movie_name))
                for cast in cast_list:
                    dispatcher.utter_message(text = '* {}'.format(cast))
            
            return [SlotSet("cast", []), SlotSet("number_of_actors", None)]

# TASK 2
    
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
        return 'action_summary_request'
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):
        genre_list = tracker.get_slot("genre")
        retrieve_year = tracker.get_slot("release_date")
        retrieve_is_before = tracker.get_slot("is_before")
        retrieve_is_after = tracker.get_slot("is_after")
        retrieve_is_exactly = tracker.get_slot("is_exactly")
        retrieve_vote = tracker.get_slot("rating")
        retrieve_cast = tracker.get_slot("cast")
        retrieve_director = tracker.get_slot("director_name")

        dispatcher.utter_message(text = "Great! You've provided all the essential elements for me to find a movie. Let's review the choices you've made so far: ")
        if genre_list != None:
            dispatcher.utter_message(text = 'The genres that you chose are:')
            for genre in genre_list:
                dispatcher.utter_message(text = '* {}'.format(genre))

        if retrieve_vote != None:
            dispatcher.utter_message(text = 'After that, the rating chosen is {}.'.format(retrieve_vote))

        if retrieve_year != None:
            if retrieve_is_before != None:
                dispatcher.utter_message(text = "Moreover, you want to check all the films prior the year {}".format(retrieve_year))
            elif retrieve_is_after != None:
                dispatcher.utter_message(text = "Moreover, you want to check all the films after the year {}".format(retrieve_year))
            elif retrieve_is_exactly != None:
                dispatcher.utter_message(text = "Moreover, you have indicated your desire to browse films specifically for the year.{}".format(retrieve_year))

        if retrieve_cast != None:
            dispatcher.utter_message(text = 'Also, here is the list of actors that you asked for:')
            for cast in retrieve_cast:
                dispatcher.utter_message(text = '* {}'.format(cast))

        if retrieve_director != None and retrieve_director != retrieve_cast:
            dispatcher.utter_message(text = 'Finally, the directors chosen by you are:')
            for director in retrieve_director:
                dispatcher.utter_message(text = '* {}'.format(director))
        
        return []


class ActionResetSlots(Action):

    def name(self):
        return 'action_reset_slots'
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):
         
         return[SlotSet("is_inside_rules", None), SlotSet("keep_asking", None)]
    
class ActionResetGenre(Action):

    def name(self):
        return 'action_reset_genre'
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):
        return[SlotSet("genre", None)]

class ActionResetRating(Action):

    def name(self):
        return 'action_reset_rating'
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):
        return[SlotSet("rating", None)]

class ActionResetCast(Action):

    def name(self):
        return 'action_reset_cast'
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):
        return[SlotSet("cast", None)]

class ActionResetReleaseDate(Action):

    def name(self):
        return 'action_reset_release_date'
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):
        return[SlotSet("release_date", None), SlotSet("is_before", None), SlotSet("is_after", None), SlotSet("is_exactly", None)]

class ActionResetDirectorName(Action):

    def name(self):
        return 'action_reset_director_name'
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):
        return[SlotSet("director_name", None)]
        
        
    
# TASK 3
    
# class ActionFindMovieWithPlot(Action):

#     def name(self):
#         return 'action_obtain_movie_from_plot'
    
#     def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):
#         input_plot = tracker.latest_message['text']
        
#         movie_dataframe = pd.read_csv('databases/wiki_movie_plots_deduped.csv', sep=',')
#         #Filtering the data
#         movie_dataframe = movie_dataframe[movie_dataframe['Release Year'] >= 1980]
#         movie_dataframe = movie_dataframe[movie_dataframe['Origin/Ethnicity'] == 'American']
#         movie_dataframe = movie_dataframe.reset_index()
#         all_plots = movie_dataframe['Plot'].values

#         use_doc2vec_model = True

#         if use_doc2vec_model:

#             #processed_plots = preprocess_documents(all_plots)
#             #tagged_corpus = [TaggedDocument(d, [i]) for i, d in enumerate(processed_plots)]
#             #model = Doc2Vec(tagged_corpus, dm=0, vector_size=200, window=2, min_count=1, epochs=100, hs=1)
#             #pickle.dump(model, open('plot_models/doc2vec_model.pkl', 'wb'))

#             model = pickle.load(open('plot_models/doc2vec_model.pkl', 'rb'))
#             preprocessed_input = gensim.parsing.preprocessing.preprocess_string(input_plot)
#             input_vector = model.infer_vector(preprocessed_input)
#             similarities = model.docvecs.most_similar(positive = [input_vector])
            
#             dispatcher.utter_message(text = "The movies that are similar to your plot are:")
#             for similarity in similarities:
#                 dispatcher.utter_message(text = "{} with a similarity score of {}".format(movie_dataframe['Title'].iloc[similarity[0]], similarity[1]))

#             return[SlotSet("movie_name", movie_dataframe['Title'].iloc[similarities[0][0]]),
#                    SlotSet("director_name", movie_dataframe['Director'].iloc[similarities[0][0]]),
#                    SlotSet("plot", movie_dataframe['Plot'].iloc[similarities[0][0]]),
#                    SlotSet("wiki_link", movie_dataframe['Wiki Page'].iloc[similarities[0][0]])
#                    ]

#         else: #BERT
#             model = SentenceTransformer('bert-base-nli-mean-tokens')

#             #sentence_embeddings = model.encode(all_plots)
#             #pickle.dump(sentence_embeddings, open('plot_models/bert_model.pkl', 'wb'))
#             sentence_embeddings = pickle.load(open('plot_models/bert_model.pkl', 'rb'))

#             input_embedding = model.encode(input_plot)

#             result = cosine_similarity(
#                 [input_embedding],
#                 sentence_embeddings[0:]
#             )

#             movie_index = np.argmax(result)
#             print(movie_index)
#             print(movie_dataframe['Title'][movie_index])

#             return[SlotSet("movie_name", movie_dataframe['Title'][movie_index]),
#                    SlotSet("director_name", movie_dataframe['Director'][movie_index]),
#                    SlotSet("plot", movie_dataframe['Plot'][movie_index]),
#                    SlotSet("wiki_link", movie_dataframe['Wiki Page'][movie_index])
#                    ]

# class ActionLoopPlot(Action):

#     def name(self):
#         return 'action_loop_plot'
    
#     def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):

#          return[SlotSet("is_plot_received", None), SlotSet("plot", None)]


class ValidateRetrievePlotForm(FormValidationAction):
    def name(self):
        return "validate_retrieve_plot_form"
    
    @staticmethod
    async  def required_slots(domain_slots, dispatcher, tracker, domain):
        return ["is_plot_received", "iterate_plot"]

    def validate_is_plot_received(self, slot_value, dispatcher, tracker, domain):
        reversed_events = list(reversed(tracker.events))
        if reversed_events[0].get('name') != 'iterate_plot':
            print("ESEGUO IL CODICE PER TROVATE IL FILM PIù SIMILE...")
            dispatcher.utter_message(text = "The movies that are similar to your plot are: ...")
            return{"is_plot_received": True, "iterate_plot": None}

    def validate_iterate_plot(self, slot_value, dispatcher, tracker, domain):
        if slot_value == True:
            return{"is_plot_received": None, "iterate_plot": True} #re-call the form
        elif slot_value == False:
            return{"iterate_plot": False}