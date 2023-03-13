from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

import requests
import tmdbsimple as tmdb

tmdb.API_KEY = "a3d485e7dbba8ea69c0d9041ab46207a"
search = tmdb.Search()

class ActionRetrieveGenre(Action):

    def name(self):
        return 'action_retrieve_genre'
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):
        movie_title = tracker.get_slot("movie_name")
        query = search.movie(query=movie_title)
        movie_id = query.get("results")[0].get("id")
        response = tmdb.Movies(movie_id).info()
        all_movie_genres = response.get("genres")
        result = ""
        for i in range(len(all_movie_genres)):
           result += str(all_movie_genres[i].get("name")) + " "

        return [SlotSet("genre", result) if result != "" else SlotSet("genre", "No genre listed")]

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

        request_url = "https://api.themoviedb.org/3/movie/{}/credits?api_key={}".format(str(movie_id), "a3d485e7dbba8ea69c0d9041ab46207a")
        raw = requests.get(request_url).json()
        composer = []
        for crew_element in raw["crew"]:
            if "Original Music Composer" == crew_element["job"]:
                composer.append(crew_element["name"])   
        
        return []

class ActionRetrieveDirector(Action):

    def name(self):
        return 'action_retrieve_director'
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):
        movie_title = tracker.get_slot("movie_name")
        query = search.movie(query=movie_title)
        movie_id = query.get("results")[0].get("id")

        request_url = "https://api.themoviedb.org/3/movie/{}/credits?api_key={}".format(str(movie_id), "a3d485e7dbba8ea69c0d9041ab46207a")
        raw = requests.get(request_url).json()
        director = []
        for crew_element in raw["crew"]:
            if "Director" == crew_element["job"]:
                director.append(crew_element["name"])   
        
        return []
    

class ActionRetrieveProducer(Action):

    def name(self):
        return 'action_retrieve_producer'
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):
        movie_title = tracker.get_slot("movie_name")
        query = search.movie(query=movie_title)
        movie_id = query.get("results")[0].get("id")

        request_url = "https://api.themoviedb.org/3/movie/{}/credits?api_key={}".format(str(movie_id), "a3d485e7dbba8ea69c0d9041ab46207a")
        raw = requests.get(request_url).json()
        producer = []
        for crew_element in raw["crew"]:
            if "Producer" == crew_element["job"]:
                producer.append(crew_element["name"])   
        
        return []