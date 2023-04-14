# My Gallery

## Project Overview
In this project, I want to link the artworks from Harvard Art Museum with iTunes, and generate a personal gallery based ob users' interest.

The main program is in the ‘MyGallery.py’ file. To run my program, you can just run this python file, it will automatically run the server on “[http://127.0.0.1:5000](http://127.0.0.1:5000/)”. The api key is also in this file. When you run the file and open the flask app, you need to specify the value of three filters/parameters (culture, yearmade, classification) and then submit the form. It will visualize the search results on the response page. If there is no result for your search, you can start over and try other parameters. You can jump to the detail page of each art object on the response page. And based on the 100 records of your search results, the response page will visualize the 10 most frequent words in the artworks’ titles. You can then choose a word and generate a media gallery based on that keyword.

To make my program work, there are several packages you need to install: 

- flask
- re
- requests
- collections

## Data Structure

I use the tree data structure in this project.

The ‘tree.py’ file defines the tree class, and constructs the tree.
The TreeNode class has three values: data - its own data, parent - its parent node, children - a list of its children nodes; three methods: get_level - get the level of the tree node (there are four levels in total), print_tree - print the tree node, add_child - add a node as its child.
The LeafNode inherits the TreeNode, except its children is None.
The loadTree and saveTree functions are used to load and save tree from the ‘treeFile.json’ file. 
The search_or_add function will search if a leaf node is in the tree, if not, it will add the leaf into the tree.

The ‘treeFile.json’ file stores the tree in the form of dictionary.

