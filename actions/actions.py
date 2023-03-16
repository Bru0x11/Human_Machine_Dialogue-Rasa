from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

import requests
import tmdbsimple as tmdb

api_key = "a3d485e7dbba8ea69c0d9041ab46207a"
tmdb.API_KEY = api_key
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

        request_url = "https://api.themoviedb.org/3/movie/{}/credits?api_key={}".format(str(movie_id), api_key)
        raw = requests.get(request_url).json()
        composer = ""
        for crew_element in raw["crew"]:
            if "Original Music Composer" == crew_element["job"]:
                composer += crew_element["name"]  
        
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
        director = ""
        for crew_element in raw["crew"]:
            if "Director" == crew_element["job"]:
                director += crew_element["name"]   
        
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
        producer = ""
        for crew_element in raw["crew"]:
            if "Producer" == crew_element["job"]:
                producer += crew_element["name"]  
        
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
        request_url = "https://api.themoviedb.org/3/discover/movie?api_key={}&language=en-US&sort_by=popularity.desc&include_adult=false&include_video=false&page=1&with_watch_monetization_types=flatrate".format(api_key)

        genre_dictionary = {
            "action": "28", "adventure": "12", "animation": "16", "comedy": "35", "crime": "80", "documentary": "99", "drama": "18", "family": "10751", "fantasy": "14", "history": "36", "horror": "27",
            "music": "10402", "mistery": "9648", "romance": "10749", "science fiction": "878", "tv movie": "10770", "thriller": "53", "war": "10752", "western": "37"
        }

        retrieve_year = tracker.get_slot("release_date")
        retrieve_movie_time_period = tracker.get_slot("movie_time_period")
        retrieve_vote = tracker.get_slot("rating")
        retrieve_cast = tracker.get_slot("cast")
        retrieve_genre = genre_dictionary.get(tracker.get_slot("genre"))
        retrieve_runtime = tracker.get_slot("runtime")
        retrieve_runtime_time_period = tracker.get_slot("runtime_time_period")

        print(retrieve_genre, retrieve_vote)

        if retrieve_year != None:
            if retrieve_movie_time_period == "After":
                add_year_gte = "&primary_release_date.gte={}".format(retrieve_year)
                request_url += add_year_gte
            elif retrieve_movie_time_period == "Before":
                add_year_lte = "&primary_release_date.lte={}".format(retrieve_year)
                request_url += add_year_lte
            else: 
                add_exact_year = "&primary_release_year={}".format(retrieve_year)
                request_url += add_exact_year

        if retrieve_vote!= None:
            add_vote_average_gte = "&vote_average.gte={}".format(retrieve_vote)
            request_url += add_vote_average_gte

        if retrieve_cast != None:
            add_cast = "&with_cast={}".format(retrieve_cast)
            request_url += add_cast

        if retrieve_genre != None:
            add_genre = "&with_genres={}".format(retrieve_genre)
            request_url += add_genre

        if retrieve_runtime != None:
            if retrieve_runtime_time_period == "Longer":
                add_runtime_gte = "&with_runtime.gte={}".format(retrieve_runtime)
                request_url += add_runtime_gte
            else:
                add_runtime_lte = "&with_runtime.lte={}".format(retrieve_runtime)
                request_url += add_runtime_lte

        print(request_url)
        raw = requests.get(request_url).json()
        response = raw.get("results")[0]

        title = response.get("original_title")
        plot = response.get("overview")
        release_date = response.get("release_date")

        return[SlotSet("movie_name", title), SlotSet("plot", plot), SlotSet("release_date", release_date)]
