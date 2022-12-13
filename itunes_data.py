import webbrowser
import requests
from finalcache import *


class Media:

    def __init__(self, title="No Title", author="No Author", release_year="No Release Year", url="No URL", json=None):
        self.title = title
        self.author = author
        self.release_year = release_year
        self.url = url

        self.json = json
        if self.json != None:
            try:
                self.title = json["trackName"]
            except:
                self.title = json['collectionName']
            self.author = json["artistName"]
            self.release_year = json["releaseDate"][:4]
            try:
                self.url = json["collectionViewUrl"]
            except:
                self.url = json["trackViewUrl"]
                    
                    
    
    def info(self):
        return self.title + " by " + self.author + " (" + str(self.release_year) + ")"

    def length(self):
        return 0




class Song(Media):
    
    def __init__(self, title="No Title", author="No Author", release_year="No Release Year", url="No URL", album="No Album", genre="No Genre", track_length=0, json=None):
        super().__init__(title, author, release_year, url, json)
        self.album = album
        self.genre = genre
        self.track_length = track_length
        if json != None:
            self.album = json["collectionName"]
            self.genre = json["primaryGenreName"]
            self.track_length = json["trackTimeMillis"]


    def info(self):
        return self.title + " by " + self.author + " (" + str(self.release_year) + ") " + "[" + self.genre + "]"

    def length(self):
        return round(self.track_length/1000)


class Movie(Media):
    def __init__(self, title="No Title", author="No Author", release_year="No Release Year", url="No URL", rating="No Rating", movie_length=0, json=None):
        super().__init__(title, author, release_year, url, json)
        self.rating = rating
        self.movie_length = movie_length
        if json != None:
            self.rating = json["contentAdvisoryRating"]
            self.movie_length = json["trackTimeMillis"]
                

    def info(self):
        return self.title + " by " + self.author + " (" + str(self.release_year) + ") " + "[" + self.rating + "]"

    def length(self):
        return round(self.movie_length/60000)

def make_request(baseurl, params):
    '''Make a request to the Web API using the baseurl and params
    Parameters
    ----------
    baseurl: string
        The URL for the API endpoint
    params: dictionary
        A dictionary of param: param_value pairs
    Returns
    -------
    string
        the results of the query as a Python object loaded from JSON
    '''
    response = requests.get(baseurl, params=params)
    return response.json()

def make_request_with_cache(baseurl, params, CACHE_DICT, CACHE_FILENAME):
    '''Check the cache for a saved result for this baseurl+params
    combo. If the result is found, return it. Otherwise send a new 
    request, save it, then return it.
    Parameters
    ----------
    baseurl: string
        The URL for the API endpoint
    params: dictionary
        A dictionary of param: param_value pairs
    CACHE_DICT:
        A dictionary of unique_key: result pairs
    
    Returns
    -------
    string
        the results of the query as a Python object loaded from JSON
    '''
    request_key = construct_unique_key(baseurl, params)
    if request_key in CACHE_DICT.keys():
        print("cache hit!", request_key)
        return CACHE_DICT[request_key]
    else:
        print("cache miss!", request_key)
        CACHE_DICT[request_key] = make_request(baseurl, params)
        save_cache(CACHE_DICT, CACHE_FILENAME)
        return CACHE_DICT[request_key]

term_test = 'portrait'

def main():
    
    CACHE_FILENAME_ITUNES = 'cache_itunes.json'
    CACHE_DICT_ITUNES = open_cache(CACHE_FILENAME_ITUNES)

    base_url_itunes = 'https://itunes.apple.com/search'

    params_itunes = {
        "term": term_test, "limit": 100
    }

    results_itunes = make_request_with_cache(base_url_itunes, params_itunes, CACHE_DICT_ITUNES, CACHE_FILENAME_ITUNES)
    itunes = results_itunes['results']

    media_list = []
    song_list = []
    movie_list = []

    for item in itunes:
        if item["wrapperType"] == "track":
            if item["kind"] == "song":
                try:
                    song_list.append(Song(json=item))
                except: 
                    pass
            elif item["kind"][-5:] == "movie":
                try:
                    movie_list.append(Movie(json=item))
                except:
                    pass
            else:
                try:
                    media_list.append(Media(json=item))
                except:
                    pass
        else:
            try:
                media_list.append(Media(json=item))
            except:
                pass

    media_count = len(media_list)
    song_count = len(song_list)
    movie_count = len(movie_list) 

    whole_list = song_list+movie_list+media_list

    if len(whole_list) == 0:
        print("No Results")

    else:
        print("SONGS")
        if song_count == 0:
            print("No Results in Songs")
        else:
            for i in range(0,song_count):
                s = whole_list[i]
                print(i+1, s.info())

        print("MOVIES")
        if movie_count == 0:
            print("No Results in Movies")
        else:
            for i in range(song_count, song_count+movie_count):
                m = whole_list[i]
                print(i+1, m.info())

        print("OTHER MEDIA")
        if media_count == 0:
            print("No results in Media")
        else:
            for i in range(song_count+movie_count, song_count+movie_count+media_count):
                m = whole_list[i]
                print(i+1, m.info())

    return whole_list

if __name__ == "__main__":
    main()