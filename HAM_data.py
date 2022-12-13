import requests
import os
import json
import webbrowser
from finalcache import *


HAMAPI_KEY = '97eb9bff-851e-4bd6-8987-03e58d8154e6'


CACHE_FILENAME_CLASS = 'cache_class.json'
CACHE_DICT_CLASS = {}

CACHE_FILENAME_OBJECT = 'cache_object.json'
CACHE_DICT_OBJECT = {}


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

def main():
    CACHE_DICT_CLASS = open_cache(CACHE_FILENAME_CLASS)

    base_url_class = 'https://api.harvardartmuseums.org/classification'
    params_class = {
        "apikey": HAMAPI_KEY, "q": "drawings"
    }

    results_class = make_request_with_cache(base_url_class, params_class, CACHE_DICT_CLASS, CACHE_FILENAME_CLASS)

    classes = results_class['records']
    # for c in classes:
    #     print(c['name'])
    #     print(c['id'])
    classId = classes[0]['id']
    # print(classId)

    CACHE_DICT_OBJECT = open_cache(CACHE_FILENAME_OBJECT)

    pages = []
    for i in range(10):
        pages.append(str(i+1))

    base_url = 'https://api.harvardartmuseums.org/object'
    params = {
        "apikey": HAMAPI_KEY
    }

    # artists = []
    objectsId = []
    for page in pages:
        params = {
            "apikey": HAMAPI_KEY, "region": "europe", "yearmade": '1800', "classification": classId, "page": page
        }

        results = make_request_with_cache(base_url, params, CACHE_DICT_OBJECT, CACHE_FILENAME_OBJECT)
        objects = results['records']
        for object in objects:
            objectsId.append(object['id'])
            # print(object['title'])
            # print(object['url'])
            # webbrowser.get('chrome').open(object['url'])
            # try:
            #     print(object['people'][0]['name'])
            #     artists.append(object['people'][0]['name'])
            # except:
            #     pass
        print(page,objectsId)

    

if __name__ == "__main__":
    main()















