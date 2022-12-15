from finalcache import *
from HAM_data import *
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


class object:
    def __init__(self, title, url):
        self.title = title
        self.url = url


@app.route('/')
def index():
    return render_template('index.html') 

@app.route('/handle_form', methods=['POST'])
def get_HAM_params():
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



if __name__ == "__main__":
    app.run(debug=True) 