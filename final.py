import requests
import json

HAMAPI_KEY = '97eb9bff-851e-4bd6-8987-03e58d8154e6'


CACHE_FILENAME_CLASS = 'cache_class.json'
CACHE_DICT_CLASS = {}

CACHE_FILENAME_OBJECT = 'cache_object.json'
CACHE_DICT_OBJECT = {}

def open_cache(CACHE_FILENAME):
    '''opens the cache file if it exists and loads the JSON into
    the cache dictionary.
    
    if the cache file doesn't exist, creates a new cache dictionary
    
    Parameters
    ----------
    CACHE_FILENAME: string

    Returns
    -------
    The opened cache
    '''
    try:
        cache_file = open(CACHE_FILENAME, 'r')
        cache_contents = cache_file.read()
        cache_dict = json.loads(cache_contents)
        cache_file.close()
    except:
        cache_dict = {}
    return cache_dict

def save_cache(cache_dict, CACHE_FILENAME):
    '''saves the current state of the cache to disk
    Parameters
    ----------
    cache_dict: dict
        the dictionary to save

    CACHE_FILENAME: string
        the file to save into

    Returns
    -------
    None
    '''
    dumped_json_cache = json.dumps(cache_dict)
    fw = open(CACHE_FILENAME, "w")
    fw.write(dumped_json_cache)
    fw.close()

def construct_unique_key(baseurl, params):
    ''' constructs a key that is guaranteed to uniquely and 
    repeatably identify an API request by its baseurl and params
    Parameters
    ----------
    baseurl: string
        The URL for the API endpoint
    params: dictionary
        A dictionary of param: param_value pairs
    Returns
    -------
    string
        the unique key as a string
    '''
    param_strings = []
    connector = '_'
    for k in params.keys():
        param_strings.append(f'{k}_{params[k]}')
    param_strings.sort()
    unique_key = baseurl + connector + connector.join(param_strings)
    return unique_key

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




CACHE_DICT_CLASS = open_cache(CACHE_FILENAME_CLASS)

base_url_class = 'https://api.harvardartmuseums.org/classification'
params_class = {
    "apikey": HAMAPI_KEY
}

params_class.update({"q": "drawings"})

results_class = make_request_with_cache(base_url_class, params_class, CACHE_DICT_CLASS, CACHE_FILENAME_CLASS)
classes = results_class['records']
# for c in classes:
#     print(c['name'])
#     print(c['id'])
classId = classes[0]['id']
print(classId)


CACHE_DICT_OBJECT = open_cache(CACHE_FILENAME_OBJECT)

base_url = 'https://api.harvardartmuseums.org/object'
params = {
    "apikey": HAMAPI_KEY
}

params['region'] = 'europe'
params['yearmade'] = 1800
params['classification'] = classId

results = make_request_with_cache(base_url, params, CACHE_DICT_OBJECT, CACHE_FILENAME_OBJECT)
objects = results['records']
for object in objects:
    print(object['title'])
    print(object['url'])
    print(object['people'][0]['name'])

