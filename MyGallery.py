import re
from collections import Counter

from finalcache import *
from HAM_data import *
from itunes_data import *
from tree import *

from flask import Flask, render_template, request

app = Flask(__name__)



HAMAPI_KEY = '97eb9bff-851e-4bd6-8987-03e58d8154e6'

CACHE_FILENAME_CLASS = 'cache_class.json'
CACHE_DICT_CLASS = {}

CACHE_FILENAME_OBJECT = 'cache_object.json'
CACHE_DICT_OBJECT = {}


tree_file = 'treeFile.json'


def get_class_id(class_name):
    '''Get the id of a classification API of HAM.
    Parameters
    ----------
    class_name: string
        The name of the classification
    
    Returns
    -------
    string
        The id of the classification
        Or 'any' if the class_name is 'any'
    '''

    if class_name == 'any':
        return 'any'
    CACHE_DICT_CLASS = open_cache(CACHE_FILENAME_CLASS)

    base_url_class = 'https://api.harvardartmuseums.org/classification'
    params_class = {
        "apikey": HAMAPI_KEY, "q": class_name
    }

    results_class = make_request_with_cache(base_url_class, params_class, CACHE_DICT_CLASS, CACHE_FILENAME_CLASS)

    classes = results_class['records']

    class_id = classes[0]['id']

    return class_id





def get_the_10_most_common_words(list):
    '''Find the 10 most frequent words in a titile list.
    Parameters
    ----------
    list: list
        A list of title strings
    
    Returns
    -------
    list
        The list of the 10 most frequent words in the list of titles
    '''

    words_10_Most_Common = []
    words_list = []

    for title in list:
        title_list = title.split()
        words_list.extend(title_list)

    new_list = []

    for word in words_list:
        word = re.sub(r'[^\w\s]','',word)
        new_list.append(word)

    new_list = [word.lower() for word in new_list]
    new_list = [word for word in new_list if not word.isdigit()]    

    common_words = ['a', 'an', 'from', 'to', 'by', 'of', 'in', 'the', 'for', 'with', 'and', 'on']
    new_list = [word for word in new_list if word not in common_words] 

    words_counter = Counter(new_list)
    words_most_common = words_counter.most_common(10)

    for item in words_most_common:
        words_10_Most_Common.append(item[0])
    
    return words_10_Most_Common



@app.route('/')
def index():
    '''The index page of My Gallery.'''

    return render_template('index.html') 


@app.route('/handle_form', methods=['POST', 'GET'])
def get_HAM_params():
    '''Get the value of three parameters (from user input), render the first 10 results (art obejcts).
    Every result visualizes the title of that art object.
    Every result links to the detail information page of that art object.
    If there is no result found, it will visualize an empty page, and let the user to start over.

    Visualizes the 10 most frequent words appeared in the 100 records of artworks' titles.
    Let the user to choose a word to generate a media gallery.
    '''

    culture = request.form['cultures']
    yearmade = request.form['yearmade']
    classification = request.form['classes']
    class_id = get_class_id(classification)

    tree = loadTree(tree_file)

    tree, objects_list = search_or_add(tree, culture, yearmade, class_id)

    objects = []
    objects_titles = []

    n = len(objects_list)

    if n >= 10:
        for i in range(10):
            objects.append(object(objects_list[i]['title'], objects_list[i]['url']))
            objects_titles.append(objects_list[i]['title'])

    elif n == 0:
        return render_template('no_result.html')

    else:
        for i in range(n):
            objects.append(object(objects_list[i]['title'], objects_list[i]['url']))
            objects_titles.append(objects_list[i]['title'])
            
    saveTree(tree, tree_file)

    ten_words = get_the_10_most_common_words(objects_titles)
    
    return render_template('response.html',
        culture_p = culture,
        yearmade_p = yearmade,
        class_p = classification,
        titles = objects_titles,
        objects_p = objects,
        words = ten_words)


@app.route('/generate_media', methods=['POST'])
def generate_media():
    '''Generate a media gallery based on the keyword that user chose.'''

    keyword = request.form['word_options']

    CACHE_FILENAME_ITUNES = 'cache_itunes.json'
    CACHE_DICT_ITUNES = open_cache(CACHE_FILENAME_ITUNES)

    base_url_itunes = 'https://itunes.apple.com/search'

    params_itunes = {
        "term": keyword, "limit": 50
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
        return render_template('no_result.html')

    return render_template('media_gallery.html',
        term = keyword,
        s_count = song_count,
        m_count = movie_count,
        me_count = media_count,
        s_list = song_list,
        m_list = movie_list,
        me_list = media_list)



if __name__ == "__main__":
    app.run(debug=True) 