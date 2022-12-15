from HAM_data import *
from finalcache import *

HAMAPI_KEY = '97eb9bff-851e-4bd6-8987-03e58d8154e6'

CACHE_FILENAME_CLASS = 'cache_class.json'
CACHE_DICT_CLASS = {}

CACHE_FILENAME_OBJECT = 'cache_object.json'
CACHE_DICT_OBJECT = {}


class TreeNode:
    def __init__(self, data):
        self.data = data
        self.children = []
        self.parent = None

    def get_level(self):
        level = 0
        p = self.parent
        while p:
            level += 1
            p = p.parent
        return level

    def print_tree(self):
        spaces = ' ' * self.get_level() * 3
        prefix = spaces + "|__" if self.parent else ""
        print(prefix, self.data)
        if self.children:
            for child in self.children:
                child.print_tree()


    def add_child(self, child):
        child.parent = self
        self.children.append(child)

class LeafNode(TreeNode):
    def __init__(self, data):
        self.data = data
        self.children = None
        self.parent = None

def saveTree(tree, treeFile):
    root = tree.data
    tree_dict = {}
    tree_dict[root] = {}
    
    for region_node in tree.children:
        tree_dict[root][region_node.data] = {}
        for year_node in region_node.children:
            tree_dict[root][region_node.data][year_node.data] = {}
            for class_node in year_node.children:
                class_id = class_node.data
                objects_list = class_node.children[0]
                tree_dict[root][region_node.data][year_node.data][class_id] = objects_list.data
    save_cache(tree_dict, treeFile)


def loadTree(treeFile): 
    tree_dict = open_cache(treeFile)
    root_data = list(tree_dict.keys())[0]
    root_node = TreeNode(root_data)
    for region in tree_dict[root_data].keys():
        region_node = TreeNode(region)
        root_node.add_child(region_node)
        for yearmade in tree_dict[root_data][region].keys():
            year_node = TreeNode(yearmade)
            region_node.add_child(year_node)
            for class_id in tree_dict[root_data][region][yearmade].keys():
                class_node = TreeNode(class_id)
                year_node.add_child(class_node)
                objects_list = tree_dict[root_data][region][yearmade][class_id]
                objects_node = LeafNode(objects_list)
                class_node.add_child(objects_node)
    return root_node

    
def get_class_id(class_name):
    CACHE_DICT_CLASS = open_cache(CACHE_FILENAME_CLASS)

    base_url_class = 'https://api.harvardartmuseums.org/classification'
    params_class = {
        "apikey": HAMAPI_KEY, "q": class_name
    }

    results_class = make_request_with_cache(base_url_class, params_class, CACHE_DICT_CLASS, CACHE_FILENAME_CLASS)

    classes = results_class['records']
    # for c in classes:
    #     print(c['name'])
    #     print(c['id'])
    class_id = classes[0]['id']
    # print(classId)
    return class_id

def get_objects(culture, yearmade, class_id):
    CACHE_DICT_OBJECT = open_cache(CACHE_FILENAME_OBJECT)

    pages = []
    for i in range(10):
        pages.append(str(i+1))

    base_url = 'https://api.harvardartmuseums.org/object'
    params = {
        "apikey": HAMAPI_KEY
    }

    objects_list = []


    for page in pages:
        params = {
            "apikey": HAMAPI_KEY, "culture": culture, "yearmade": yearmade, "classification": class_id, "page": page
        }

        results = make_request_with_cache(base_url, params, CACHE_DICT_OBJECT, CACHE_FILENAME_OBJECT)
        objects = results['records']
        for object in objects:
            objects_list.append({'id': object['id'], 'title': object['title'], 'url': object['url']})

    return objects_list


def search_or_add(tree, culture, yearmade, class_id):
    if tree.children == []:
        cu = TreeNode(culture)
        tree.add_child(cu)

        y = TreeNode(yearmade)
        cu.add_child(y)

        c = TreeNode(class_id)
        y.add_child(c)

        objects_list = get_objects(culture, yearmade, class_id)
        ol = LeafNode(objects_list)
        c.add_child(ol)

        return tree, objects_list

    else:
        culture_flag = False
        for culture_node in tree.children:
            if culture != culture_node.data:
                pass
            if culture == culture_node.data:
                culture_flag = True
                cu = culture_node
                break
        if culture_flag == False:
            cu = TreeNode(culture)
            tree.add_child(cu)

            y = TreeNode(yearmade)
            cu.add_child(y)

            c = TreeNode(class_id)
            y.add_child(c)

            objects_list = get_objects(culture, yearmade, class_id)
            ol = LeafNode(objects_list)
            c.add_child(ol)

            return tree, objects_list

        if culture_flag == True:
            year_flag = False
            for year_node in cu.children:
                if yearmade != year_node.data:
                    pass
                if yearmade == year_node.data:
                    year_flag = True
                    y = year_node
                    break
            if year_flag == False:
                y = TreeNode(yearmade)
                cu.add_child(y)

                c = TreeNode(class_id)
                y.add_child(c)

                objects_list = get_objects(culture, yearmade, class_id)
                ol = LeafNode(objects_list)
                c.add_child(ol)

                return tree, objects_list

            if year_flag == True:
                class_flag = False
                for class_node in y.children:
                    if class_id != class_node.data:
                        pass
                    if class_id == class_node.data:
                        class_flag = True
                        c = class_node
                        break
                if class_flag == False:
                    c = TreeNode(class_id)
                    y.add_child(c)

                    objects_list = get_objects(culture, yearmade, class_id)
                    ol = LeafNode(objects_list)
                    c.add_child(ol)

                    return tree, objects_list

                if class_flag == True:
                    ol = c.children[0]
                    return tree, ol.data




    


    





