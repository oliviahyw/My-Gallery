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
    print("Root", file = treeFile)
    print(tree.data, file = treeFile)
    if tree.children == []:
        pass
    else:
        for region_node in tree.children:
            print("Region", file = treeFile)
            print(region_node.data, file = treeFile)
            for year_node in region_node.children:
                print("Yearmade", file = treeFile)
                print(year_node.data, file = treeFile)
                for class_node in year_node.children:
                    print("Class_id", file = treeFile)
                    print(class_node.data, file = treeFile)
                    objects_list = class_node.children[0]
                    print("Objects", file = treeFile)
                    print(objects_list.data, file = treeFile)


def loadTree(treeFile): 
    line = treeFile.readline().strip("\n")
    if line == "":
        return None
    else:
        if line == "Root":
                root_node = TreeNode(treeFile.readline().strip("\n"))
                line = treeFile.readline().strip("\n")
                if line == "":
                    return root_node
                else:
                    while True:
                        if line == "Region":       
                            region_node = TreeNode(treeFile.readline().strip("\n"))
                            root_node.add_child(region_node)
                            line = treeFile.readline().strip("\n")
                            year_node = TreeNode(treeFile.readline().strip("\n"))
                            region_node.add_child(year_node)
                            line = treeFile.readline().strip("\n")
                            class_node = TreeNode(treeFile.readline().strip("\n"))
                            year_node.add_child(class_node)
                            line = treeFile.readline().strip("\n")
                            objects_id = LeafNode(treeFile.readline().strip("\n"))
                            class_node.add_child(objects_id)
                            line = treeFile.readline().strip("\n")
                            if line == "":
                                break
                            else:
                                continue
                        if line == "Yearmade":
                            year_node = TreeNode(treeFile.readline().strip("\n"))
                            region_node.add_child(year_node)
                            line = treeFile.readline().strip("\n")
                            class_node = TreeNode(treeFile.readline().strip("\n"))
                            year_node.add_child(class_node)
                            line = treeFile.readline().strip("\n")
                            objects_id = LeafNode(treeFile.readline().strip("\n"))
                            class_node.add_child(objects_id)
                            line = treeFile.readline().strip("\n")
                            if line == "":
                                break
                            else:
                                continue
                        if line == "Class_id":
                            class_node = TreeNode(treeFile.readline().strip("\n"))
                            year_node.add_child(class_node)
                            line = treeFile.readline().strip("\n")
                            objects_id = LeafNode(treeFile.readline().strip("\n"))
                            class_node.add_child(objects_id)
                            line = treeFile.readline().strip("\n")
                            if line == "":
                                break
                            else:
                                continue      
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


def get_objects(region, yearmade, class_id):
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
            "apikey": HAMAPI_KEY, "region": region, "yearmade": yearmade, "classification": class_id, "page": page
        }

        results = make_request_with_cache(base_url, params, CACHE_DICT_OBJECT, CACHE_FILENAME_OBJECT)
        objects = results['records']
        for object in objects:
            objects_list.append({'id': object['id'], 'title': object['title'], 'url': object['url']})

    return objects_list


def search_or_add(tree, region, yearmade, class_id):
    if tree.children == []:
        r = TreeNode(region)
        tree.add_child(r)

        y = TreeNode(yearmade)
        r.add_child(y)

        c = TreeNode(class_id)
        y.add_child(c)

        objects_list = get_objects(region, yearmade, class_id)
        ol = LeafNode(objects_list)
        c.add_child(ol)

        return tree, objects_list

    else:
        region_flag = False
        for region_node in tree.children:
            if region != region_node.data:
                pass
            if region == region_node.data:
                region_flag = True
                r = region_node
                break
        if region_flag == False:
            r = TreeNode(region)
            tree.add_child(r)

            y = TreeNode(yearmade)
            r.add_child(y)

            c = TreeNode(class_id)
            y.add_child(c)

            objects_list = get_objects(region, yearmade, class_id)
            ol = LeafNode(objects_list)
            c.add_child(ol)

            return tree, objects_list

        if region_flag == True:
            year_flag = False
            for year_node in r.children:
                if yearmade != year_node.data:
                    pass
                if yearmade == year_node.data:
                    year_flag = True
                    y = year_node
                    break
            if year_flag == False:
                y = TreeNode(yearmade)
                r.add_child(y)

                c = TreeNode(class_id)
                y.add_child(c)

                objects_list = get_objects(region, yearmade, class_id)
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

                    objects_list = get_objects(region, yearmade, class_id)
                    ol = LeafNode(objects_list)
                    c.add_child(ol)

                    return tree, objects_list

                if class_flag == True:
                    ol = c.children[0]
                    return tree, ol.data


root = TreeNode("Art Objects")

file_name = 'treeFile.txt'

region_test = 'europe'
yearmade_test = '1800'
class_name_test = 'drawings'

if __name__ == '__main__':
    class_id_test = get_class_id(class_name_test)

    # tree_file = open(file_name, 'r')
    # tree = loadTree(tree_file)
    # tree_file.close()

    tree, objects_list = search_or_add(root, region_test, yearmade_test, class_id_test)
    tree_file = open(file_name, 'w')
    saveTree(tree, tree_file)
    tree_file.close()

    print(f'The art objects in {region_test}, {yearmade_test}, and in the form of {class_name_test} are:')
    for i in range(10):
        print(objects_list[i]['title'], '\n')

    


    





