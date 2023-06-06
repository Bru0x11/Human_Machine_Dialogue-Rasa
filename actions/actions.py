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
import faiss
import gc
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

# DEFINING THE API-KEY NEEDED TO QUERY THE TMDB DATABASE
api_key = "a3d485e7dbba8ea69c0d9041ab46207a"
tmdb.API_KEY = api_key
search = tmdb.Search()

# LOADING AND MODIFYING THE MOVIE DATASET FOR TASK #3
movie_database = pd.read_csv('databases/wiki_movie_plots_deduped.csv', memory_map=True)
dataframe = movie_database[['Title','Plot']]
del movie_database
gc.collect()
dataframe.dropna(inplace=True)
dataframe.drop_duplicates(subset=['Plot'],inplace=True)

# CUSTOM ACTIONS

# TASK 1
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

        # Check if the movie exists or there is a typo in the title
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
            choose_question = random.randint(0, 3)
            questions = [
                'Do you want to know something else about {} or other films?',
                'Are there any other questions you have about {} or other movies?',
                'Is there anything else you\'d like to know about {} or other films?',
                'Would you like me to provide additional information about {} or other movies?'
            ]
            question = questions[choose_question].format(movie_name)
            genres = '\n'.join('* {}'.format(genre) for genre in genre_list)
            message = 'Sure! The genres of {} are:\n{}.\n{}'.format(movie_name, genres, question)
            dispatcher.utter_message(text=message)

            # Reset the genre slot to None. This is helpful whenever we ask a question related to another movie and we have some errors with it.
            # If we don't do so, the bot will print the genres of the previous movie.
            return [SlotSet("genre", None)]

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

        # Check if the movie exists or there is a typo in the title
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
            messages = [
                'The release date of the movie {} is {}.',
                '{} premiered on {}.',
                '{} made its debut on {}.',
                '{} was first shown to audiences on {}.'
            ]
            release_date_message = messages[choose_message].format(movie_name, release_date)
            questions = [
                'Do you want to know something else about {} or other films?',
                'Are there any other questions you have about {} or other movies?',
                'Is there anything else you\'d like to know about {} or other films?',
                'Would you like me to provide additional information about {} or other movies?'
            ]
            question = questions[choose_message].format(movie_name)
            message = 'Sure! {} {}'.format(release_date_message, question)
            dispatcher.utter_message(text=message)

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

        # Check if the movie exists or there is a typo in the title
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
            messages = [
                'The total budget for {} is {}.',
                'The overall budget for {} amounts to {}.',
                '{} has a budget of {} in total.',
                'The complete budget allocated for producing {} amounts for {}.'
            ]
            budget_message = messages[choose_message].format(movie_name, budget)
            questions = [
                'Do you want to know something else about {} or other films?',
                'Are there any other questions you have about {} or other movies?',
                'Is there anything else you\'d like to know about {} or other films?',
                'Would you like me to provide additional information about {} or other movies?'
            ]
            question = questions[choose_message].format(movie_name)
            message = 'Sure! {} {}'.format(budget_message, question)
            dispatcher.utter_message(text=message)

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

        # Check if the movie exists or there is a typo in the title
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
            messages = [
                'The {} lasts {} minutes',
                'The duration of {} is {} minutes.',
                '{} has a runtime of {} minutes.',
                'The length of {} is {} minutes.'
            ]
            runtime_message = messages[choose_message].format(movie_name, runtime)
            questions = [
                'Do you want to know something else about {} or other films?',
                'Are there any other questions you have about {} or other movies?',
                'Is there anything else you\'d like to know about {} or other films?',
                'Would you like me to provide additional information about {} or other movies?'
            ]
            question = questions[choose_message].format(movie_name)
            message = 'Sure! {} {}'.format(runtime_message, question)
            dispatcher.utter_message(text=message)

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

        # Check if the movie exists or there is a typo in the title
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
            messages = [
                'The revenue of {} amounts to {}.',
                '{} earned {} in revenue.',
                'The total revenue generated by {} is {}.',
                '{} earned a total of {} in revenue.'
            ]
            revenue_message = messages[choose_message].format(movie_name, revenue)
            questions = [
                'Do you want to know something else about {} or other films?',
                'Are there any other questions you have about {} or other movies?',
                'Is there anything else you\'d like to know about {} or other films?',
                'Would you like me to provide additional information about {} or other movies?'
            ]
            question = questions[choose_message].format(movie_name)
            message = 'Sure! {} {}'.format(revenue_message, question)
            dispatcher.utter_message(text=message)

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

        # Check if the movie exists or there is a typo in the title
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
            messages = [
                'The plot of {} is as follows: {}',
                '{} can be summarized with the following plot: {}',
                'The storyline of {} is described as: {}'
            ]
            plot_message = messages[choose_message].format(movie_name, plot)
            questions = [
                'Do you want to know something else about {} or other films?',
                'Are there any other questions you have about {} or other movies?',
                'Is there anything else you\'d like to know about {} or other films?',
            ]
            question = questions[choose_message].format(movie_name)
            message = 'Sure! {} {}'.format(plot_message, question)
            dispatcher.utter_message(text=message)

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

        # Check if the movie exists or there is a typo in the title
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
            messages = [
                'The rating of {} is {}.',
                '{} has a rating of {}.',
                'The assigned rating for {} is {}.',
                'The rating given to {} is {}.'
            ]
            rating_message = messages[choose_message].format(movie_name, rating)
            questions = [
                'Do you want to know something else about {} or other films?',
                'Are there any other questions you have about {} or other movies?',
                'Is there anything else you\'d like to know about {} or other films?',
            ]
            question = questions[choose_message].format(movie_name)
            message = 'Sure! {} {}'.format(rating_message, question)
            dispatcher.utter_message(text=message)

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

        # Check if the movie exists or there is a typo in the title
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
            choose_question = random.randint(0, 3)
            questions = [
                'Do you want to know something else about {} or other films?',
                'Are there any other questions you have about {} or other movies?',
                'Is there anything else you\'d like to know about {} or other films?',
                'Would you like me to provide additional information about {} or other movies?'
            ]
            question = questions[choose_question].format(movie_name)
            composers = 'The composers of {} are:\n{}\n'.format(movie_name, '\n'.join('* {}'.format(composer) for composer in composer_list))
            message = 'Sure! {}.{}'.format(composers, question)
            dispatcher.utter_message(text=message)
            
            return [SlotSet("composer_name", None)]

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

        # Check if the movie exists or there is a typo in the title
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
            choose_question = random.randint(0, 3)
            questions = [
                'Do you want to know something else about {} or other films?',
                'Are there any other questions you have about {} or other movies?',
                'Is there anything else you\'d like to know about {} or other films?',
                'Would you like me to provide additional information about {} or other movies?'
            ]
            question = questions[choose_question].format(movie_name)
            directors = 'The directors of {} are:\n{}\n'.format(movie_name, '\n'.join('* {}'.format(director) for director in directors_list))
            message = 'Sure! {}.{}'.format(directors, question)
            dispatcher.utter_message(text=message)

            return [SlotSet("director_name", None)]
    
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

        # Check if the movie exists or there is a typo in the title
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
            choose_question = random.randint(0, 3)
            questions = [
                'Do you want to know something else about {} or other films?',
                'Are there any other questions you have about {} or other movies?',
                'Is there anything else you\'d like to know about {} or other films?',
                'Would you like me to provide additional information about {} or other movies?'
            ]
            question = questions[choose_question].format(movie_name)
            producers = 'The producers of {} are:\n{}\n'.format(movie_name, '\n'.join('* {}'.format(producer) for producer in producers_list))
            message = 'Sure! {}.{}'.format(producers, question)
            dispatcher.utter_message(text=message)

            return [SlotSet("producer_name", None)]
    
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

        # Check if the movie exists or there is a typo in the title
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
            choose_question = random.randint(0, 3)
            questions = [
                'Do you want to know something else about {} or other films?',
                'Are there any other questions you have about {} or other movies?',
                'Is there anything else you\'d like to know about {} or other films?',
                'Would you like me to provide additional information about {} or other movies?'
            ]
            question = questions[choose_question].format(movie_name)
            if number_of_actors is not None:
                if number_of_actors < len(cast_list):
                    actors_to_display = cast_list[:number_of_actors]
                    actors_message = 'Here is the list for the movie {} of {} actors:\n{}'.format(movie_name, number_of_actors, '\n'.join('* {}'.format(cast) for cast in actors_to_display))
                else:
                    actors_message = 'Here is the list for the movie {} of {} actors:\n{}'.format(movie_name, len(cast_list), '\n'.join('* {}'.format(cast) for cast in cast_list))
            else:
                actors_message = 'Here is the list of actors for the movie {}:'.format(movie_name)
            message = 'Sure! {}.{}'.format(actors_message, question)
            dispatcher.utter_message(text=message)
            
            return [SlotSet("cast", None), SlotSet("number_of_actors", None)]

# TASK 2
    
class ActionRecommendationWithMovie(Action):
    def name(self):
        return 'action_recommendation_with_movie'
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):
        movie_title = tracker.get_slot("movie_name")
        query = search.movie(query=movie_title)

        movie_id = query.get("results")[0].get("id")

        request_url = "https://api.themoviedb.org/3/movie/{}/similar?api_key={}&language=en-US&page=1&sort_by=vote_average.desc&vote_average.gte=7&vote_count.gte=100".format(str(movie_id), api_key)
        raw = requests.get(request_url).json()
    
        response = raw.get("results")[0]


        title = response.get("original_title")
        plot = response.get("overview")
        release_date = response.get("release_date")

        return[SlotSet("movie_name", title), SlotSet("plot", plot), SlotSet("release_date", release_date)]


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
    

class ActionSummaryRequests(Action):
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

        message = "Great! You've provided all the essential elements for me to find a movie. Let's review the choices you've made so far:"

        if genre_list != None:
            message += '\nThe genres that you chose are:\n{}'.format('\n'.join('* {}'.format(genre) for genre in genre_list))

        if retrieve_vote != None:
            message += '\nAfter that, the chosen rating is {}.'.format(retrieve_vote)

        if retrieve_year != None:
            if retrieve_is_before:
                message += '\nMoreover, you want to check all the films prior to the year {}.'.format(retrieve_year)
            elif retrieve_is_after:
                message += '\nMoreover, you want to check all the films after the year {}.'.format(retrieve_year)
            elif retrieve_is_exactly:
                message += '\nMoreover, you have indicated your desire to browse films specifically for the year {}.'.format(retrieve_year)

        if retrieve_cast != None:
            message += '\nAlso, here is the list of actors that you asked for:\n{}'.format('\n'.join('* {}'.format(cast) for cast in retrieve_cast))

        if retrieve_director != None and retrieve_director != retrieve_cast:
            message += '\nFinally, the directors chosen by you are:{}'.format('\n'.join('* {}'.format(director) for director in retrieve_director))

        message += "\nWould you like to confirm?"
        
        dispatcher.utter_message(text=message)
        
        return []

class ActionResetSlots(Action):
    def name(self):
        return 'action_reset_slots'
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):
         
         return[SlotSet("is_inside_rules", None), SlotSet("keep_asking", None), SlotSet("movie_name", None)]
    
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
    
class ActionResetPlot(Action):
    def name(self):
        return 'action_reset_plot'
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):
        return[SlotSet("plot", None)]

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
class ActionFindMovieWithPlot(Action):
    def name(self):
        return 'action_obtain_movie_from_plot'
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):
        # Get the user input for the plot/theme
        input_plot = tracker.latest_message['text']
        
        # Load the pre-trained SentenceTransformer model
        model = SentenceTransformer('task3_tools/fine_tuned_model')
        
        # Load the index for the pre-trained model
        index = 'task3_tools/fine_tuned_encoding.index'
        
        # Search for movies similar to the input plot/theme
        results = search(input_plot, top_k=5, index=index, model=model)
        
        # Print the search results
        print("\n")
        for result in results:
            print('\t', result)

class ValidateRetrievePlotForm(FormValidationAction):
    def name(self):
        return "validate_retrieve_plot_form"
    
    @staticmethod
    async  def required_slots(domain_slots, dispatcher, tracker, domain):
        return ["is_plot_received", "iterate_plot"]

    def validate_is_plot_received(self, slot_value, dispatcher, tracker, domain):
        reversed_events = list(reversed(tracker.events))
        if reversed_events[0].get('name') != 'iterate_plot':
            input_plot = tracker.latest_message['text']  # Get the latest user message text from the tracker
            model = SentenceTransformer('task3_tools/fine_tuned_model')  # Load the SentenceTransformer model
            index = faiss.read_index('task3_tools/fine_tuned_encoding.index')  # Read the faiss index
            results = self.search(input_plot, top_k=5, index=index, model=model, movie_dataframe=dataframe)  # Perform the search using the input plot
            movies = '\n'.join('* {}.'.format(result.get('Title')) for result in results)  # Generate a string of movie titles from the search results
            message = 'Great! Here is a list of movies that bear some resemblance to the one you inquired about:\n{}\nIf you want to know something more about them, feel free to ask!'.format(movies)
            dispatcher.utter_message(text=message)  

            return {"is_plot_received": True, "iterate_plot": None} 


    def validate_iterate_plot(self, slot_value, dispatcher, tracker, domain):
        if slot_value == True:
            # If the slot value is True, re-call the form by setting "is_plot_received" to None and "iterate_plot" to True
            return {"is_plot_received": None, "iterate_plot": True}
        elif slot_value == False:
            # If the slot value is False, end the form by setting "iterate_plot" to False
            return {"iterate_plot": False}
        
    def fetch_movie_info(self, dataframe_idx, movie_dataframe):
        info = movie_dataframe.iloc[dataframe_idx]
        meta_dict = {}
        meta_dict['Title'] = info['Title']
        return meta_dict
        
    def search(self, query, top_k, index, model, movie_dataframe):
        query_vector = model.encode([query])
        top_k = index.search(query_vector, top_k)
        top_k_ids = top_k[1].tolist()[0]
        top_k_ids = list(np.unique(top_k_ids))
        results =  [self.fetch_movie_info(idx, movie_dataframe) for idx in top_k_ids]
        return results