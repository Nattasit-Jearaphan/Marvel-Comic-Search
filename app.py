from ComicRecommendation import MarvelAPI, Comic, TreeNode
from ComicRecommendation import create_tree_from_tuple
from ComicRecommendation import save_to_json, load_from_json
from ComicRecommendation import filter_data, filter_character, filter_tree

from flask import Flask, render_template, request, redirect, url_for
import os

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

tree_questions = [
"Do you want to read a comic with more than five issues?",
"Do you want to read a comic with more than 20 pages?",
"Is it acceptable if a comic's price is higher than $3?"
]

recommended_comics = []

def ask_question(node, responses, recommended=[]):
    if not node.isLeaf():
        response = responses[node.key]
        if response == "yes":
            if node.hasLeftChild():
                ask_question(node.leftChild, responses, recommended)
        elif response == "no":
            if node.hasRightChild():
                ask_question(node.rightChild, responses, recommended)
        else:
            ask_question(node, responses, recommended)
    else:
        recommended.extend(node.key)

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def questions():
    if request.method == "POST":

        main_character = request.form.get("main_character")
        filtered_comics = filter_character(comics, main_character)
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
                "Do you want to read a comic with more than 20 pages?",
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
                "Do you want to read a comic with more than 20 pages?",
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

        global root
        root = create_tree_from_tuple(tree)   

        responses = {}
        for question in tree_questions:
            responses[question] = request.form.get(question)
        global recommended_comics
        recommended_comics.clear()
        ask_question(root, responses, recommended_comics)
        return redirect(url_for("recommend"))

    return render_template("questions.html", questions=tree_questions)

@app.route("/recommend")
def recommend():
    global recommended_comics
    return render_template("recommend.html", comics=recommended_comics)

if __name__ == '__main__':
    app.run(debug=True)
