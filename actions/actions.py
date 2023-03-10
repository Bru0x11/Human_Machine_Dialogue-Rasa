from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

import requests
import tmdbsimple as tmdb

tmdb.API_KEY = "a3d485e7dbba8ea69c0d9041ab46207a"

class ActionRetrieveGenre(Action):

    def name(self):
        return 'action_retrieve_genre'
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):
        search = tmdb.Search()

        movie_title = tracker.get_slot("movie_name")
        query = search.movie(query=movie_title)
        movie_id = query.get("results")[0].get("id")
        response = tmdb.Movies(movie_id).info()
        all_movie_genres = response.get("genres")
        result = ""
        for i in range(len(all_movie_genres)):
           print(all_movie_genres[i].get("name"))
           result += str(all_movie_genres[i].get("name")) + " "
        
        dispatcher.utter_message(text=result)

        return []

class ActionRetrieveProducer(Action):

    def name(self):
        return 'action_retrieve_genre'
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):
        search = tmdb.Search()

        movie_title = tracker.get_slot("movie_name")
        query = search.movie(query=movie_title)
        movie_id = query.get("results")[0].get("id")
        response = tmdb.Movies(movie_id).info()
        all_movie_genres = response.get("genres")
        result = ""
        for i in range(len(all_movie_genres)):
           print(all_movie_genres[i].get("name"))
           result += str(all_movie_genres[i].get("name")) + " "
        
        dispatcher.utter_message(text=result)

        return []