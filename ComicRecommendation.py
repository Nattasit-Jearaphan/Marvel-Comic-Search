import requests
import json
import os
import hashlib
import time

class MarvelAPI:
    def __init__(self,public_key,private_key):
        self.public_key = public_key
        self.private_key = private_key
        self.base_url = "https://gateway.marvel.com/v1/public/"
    
    def auth(self):
        ts = str(int(time.time()))
        hash_string = ts + self.private_key + self.public_key
        hash_digest =  hashlib.md5(hash_string.encode()).hexdigest()
        return {"apikey": self.public_key, "ts": ts, "hash": hash_digest}
    
    def get_comic(self, params = None):
        url = self.base_url + "comics"
        auth_params = self.auth()
        if params is None:
            params = {}
        params.update(auth_params)
        response = requests.get(url, params=params)
        return response.json()

class Comic:
    def __init__(self, title=None, description=None, format=None, 
                 issueNumber=None, collectedIssues=None, 
                 collections=None, pageCount=None, dates=None, 
                 prices=None, characters=None, thumbnail=None):
        self.title = title
        self.description = description
        self.format = format
        self.issueNumber = issueNumber
        self.collectedIssues = collectedIssues
        self.collections = collections
        self.pageCount = pageCount
        self.dates = dates 
        self.prices = prices
        self.characters = characters
        self.thumbnail = thumbnail

    def __str__(self):
        return f"{self.title}"

class TreeNode:
    def __init__(self,key,val,left=None, right=None, parent=None):
        self.key = key
        self.payload = val
        self.leftChild = left
        self.rightChild = right
        self.parent = parent

    def hasLeftChild(self):
        return self.leftChild

    def hasRightChild(self):
        return self.rightChild

    def isLeftChild(self):
        return self.parent and self.parent.leftChild == self

    def isRightChild(self):
        return self.parent and self.parent.rightChild == self

    def isRoot(self):
        return not self.parent

    def isLeaf(self):
        return not (self.rightChild or self.leftChild)

    def hasAnyChildren(self):
        return self.rightChild or self.leftChild

    def hasBothChildren(self):
        return self.rightChild and self.leftChild

def save_to_json(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f)

def load_from_json(filename):
    with open(filename, 'r') as f:
        return json.load(f)

def create_tree_from_tuple(tree_tuple):
    key, left, right = tree_tuple
    node = TreeNode(key, {})

    if left is not None:
        node.leftChild = create_tree_from_tuple(left)
        node.leftChild.parent = node

    if right is not None:
        node.rightChild = create_tree_from_tuple(right)
        node.rightChild.parent = node

    return node

def filter_data(comics_data):
    filtered_data = comics_data
    
    filtered_data = list(filter(lambda comic: int(comic['characters']['available']) > 0, filtered_data))

    comic_objects = []
    for comic in filtered_data:
        title = comic['title']
        description = comic['description']
        format = comic['issueNumber']
        issueNumber = int(comic['issueNumber'])
        collections = comic['collections']
        pageCount = int(comic['pageCount'])
        dates = comic['dates']
        prices = float(comic['prices'][0]['price'])
        characters = [name['name'].strip().lower() for name in comic['characters']['items']]
        thumbnail = comic['thumbnail']['path'] + '.' + comic['thumbnail']['extension']
        comic_objects.append(Comic(title=title, description=description, format=format, issueNumber=issueNumber, 
                                   collections=collections, pageCount=pageCount, dates=dates, prices=prices, 
                                   characters=characters, thumbnail=thumbnail))

    return comic_objects

def ask_question(node):
    if not node.isLeaf():
        response = input(node.key + " (yes/no): ").strip().lower()
        if response == "yes":
            if node.hasLeftChild():
                ask_question(node.leftChild)
        elif response == "no":
            if node.hasRightChild():
                ask_question(node.rightChild)
        else:
            print("Invalid input. Please type 'yes' or 'no'.")
            ask_question(node)
    else:
        print("Your recommended comics: ")
        for comic in node.key:
            print(comic)

def print_tree(node, level=0):
    if node is not None:
        print("  " * level + str(node.key))
        if node.hasLeftChild():
            print_tree(node.leftChild, level + 1)
        if node.hasRightChild():
            print_tree(node.rightChild, level + 1)

def filter_character(comics,name):
    filtered_comics = []
    for comic in comics:
        if name.strip().lower() in comic.characters:
          filtered_comics.append(comic)
    return filtered_comics

def filter_tree(comics,issue,page,price):
    filtered_comics = []
    issue_limit = 2
    page_limit = 100
    price_limit = 3
    for comic in comics:
      if issue:
          if page:
              if price:
                #true, true, true
                if len(comic.collections) > 0:
                  if len(comic.collections) > issue_limit and comic.pageCount > page_limit and comic.prices < price_limit:
                    filtered_comics.append(comic)
                else:
                  if comic.issueNumber > issue_limit and comic.pageCount > page_limit and comic.prices < price_limit:
                    filtered_comics.append(comic)
              else:
                #true, true, false
                if len(comic.collections) > 0:
                  if len(comic.collections) > issue_limit and comic.pageCount > page_limit and comic.prices > price_limit:
                    filtered_comics.append(comic)
                else:
                  if comic.issueNumber > issue_limit and comic.pageCount > page_limit and comic.prices > price_limit:
                    filtered_comics.append(comic)
          else:
              if price:
                #true, false, true
                if len(comic.collections) > 0:
                  if len(comic.collections) > issue_limit and comic.pageCount < page_limit and comic.prices < price_limit:
                    filtered_comics.append(comic)
                else:
                  if comic.issueNumber > issue_limit and comic.pageCount < page_limit and comic.prices < price_limit:
                    filtered_comics.append(comic)
              else:
                #true, false, false
                if len(comic.collections) > 0:
                  if len(comic.collections) > issue_limit and comic.pageCount < page_limit and comic.prices > price_limit:
                    filtered_comics.append(comic)
                else:
                  if comic.issueNumber > issue_limit and comic.pageCount < page_limit and comic.prices > price_limit:
                    filtered_comics.append(comic)
      else:
          if page:
              if price:
                #false, true, true
                if len(comic.collections) > 0:
                  if len(comic.collections) < issue_limit and comic.pageCount > page_limit and comic.prices < price_limit:
                    filtered_comics.append(comic)
                else:
                  if comic.issueNumber < issue_limit and comic.pageCount > page_limit and comic.prices < price_limit:
                    filtered_comics.append(comic)
              else:
                #false, true, false
                if len(comic.collections) > 0:
                  if len(comic.collections) < issue_limit and comic.pageCount > page_limit and comic.prices > price_limit:
                    filtered_comics.append(comic)
                else:
                  if comic.issueNumber < issue_limit and comic.pageCount > page_limit and comic.prices > price_limit:
                    filtered_comics.append(comic)
          else:
              if price:
                #false, false, true
                if len(comic.collections) > 0:
                  if len(comic.collections) < issue_limit and comic.pageCount < page_limit and comic.prices < price_limit:
                    filtered_comics.append(comic)
                else:
                  if comic.issueNumber < issue_limit and comic.pageCount < page_limit and comic.prices < price_limit:
                    filtered_comics.append(comic)
              else:
                #false, false, false
                if len(comic.collections) > 0:
                  if len(comic.collections) < issue_limit and comic.pageCount < page_limit and comic.prices > price_limit:
                    filtered_comics.append(comic)
                else:
                  if comic.issueNumber < issue_limit and comic.pageCount < page_limit and comic.prices > price_limit:
                    filtered_comics.append(comic)

    return filtered_comics

if __name__ == '__main__':

    file_name = 'Comics.json'

    if not os.path.exists(file_name):       
        public_key = "15a4ef923e07840bb4920f6e5640be9c"
        private_key = "e8ef0eb73c15cebfd8976e101e5215ad96fa5c4a"
        api = MarvelAPI(public_key, private_key)
        comics_data = api.get_comic()
        comics_data = comics_data['data']['results']
        save_to_json(comics_data, file_name)
    else:
        comics_data = load_from_json(file_name)
    
    comics = filter_data(comics_data)

    while True:
        i = input("Insert the name of main Marvel character of a comic:")
        filtered_comics = filter_character(comics,i)
        filtered_data = {
        "1": filter_tree(filtered_comics,True,True,True),
        "2": filter_tree(filtered_comics,True,True,False),
        "3": filter_tree(filtered_comics,True,False,True),
        "4": filter_tree(filtered_comics,True,False,False),
        "5": filter_tree(filtered_comics,False,True,True),
        "6": filter_tree(filtered_comics,False,True,False),
        "7": filter_tree(filtered_comics,False,False,True),
        "8": filter_tree(filtered_comics,False,False,False)
        }
        tree = (
        # Root Question
        "Do you want to read a comic with more than five issues?",
        (    
            # Node1 (Root Yes)
            "Do you want to read a comic released later than the 20th century?",
            (
                # Node3 (Node1 Yes)
                "Is it acceptable if a comic's price is higher than $3?",
                    (filtered_data["1"],None,None),
                    (filtered_data["2"],None,None)
            ),
            (
                # Node4 (Node1 No)
                "Is it acceptable if a comic's price is higher than $3?",
                    (filtered_data["3"],None,None),
                    (filtered_data["4"],None,None)
            )
        ),
        (
            # Node2 (Root No)
            "Do you want to read a comic released later than the 20th century?",
            (
                # "Node5 (Node2 Yes)"
                "Is it acceptable if a comic's price is higher than $3?",
                    (filtered_data["5"],None,None),
                    (filtered_data["6"],None,None)
            ),
            (
                # Node6 (Node2 No)
                "Is it acceptable if a comic's price is higher than $3?",
                    (filtered_data["7"],None,None),
                    (filtered_data["8"],None,None)
            )
        )
        )
        root = create_tree_from_tuple(tree)
        ask_question(root)
        again = input("Do you want to try again? (yes/no): ").strip().lower()
        if again != "yes":
            break