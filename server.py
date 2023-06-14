from flask import Flask, render_template, make_response, request
import datetime
import json
import random
import csv
import os

TEMPLATE_PATH = "./templates"

app = Flask(__name__)

graphSet = [
    {
        "id": 1,
        "graphImage": "../static/assets/graphs/graph1.png",
        "questions": [
            {
                "id": 1,
                "question": "Question 1",
                "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
                "correctAnswer": 0,
            },
            {
                "id": 2,
                "question": "Question 2",
                "options": ["Option 10", "Option 2", "Option 3", "Option 4"],
                "correctAnswer": 1,
            },
            {
                "id": 3,
                "question": "Question 3",
                "options": ["Option 10", "Option 2", "Option 3", "Option 4"],
                "correctAnswer": 1,
            },
        ],
    },
]

def getGraphIds():
    ids = [ele["id"] for ele in graphSet]
    return ids


def getRandomGraph():
    randomNumber = random.randint(0, len(graphSet) - 1)
    return graphSet[randomNumber]


def getNumberOfFiles(path):
    return len(os.listdir(path))


def getFileName(path, index):
    return path + "/" + os.listdir(TEMPLATE_PATH + path)[index]

@app.route("/")
def home():
    fileName = "/index.html"
    resp = make_response(render_template(fileName, graphIds=getGraphIds()))
    return resp

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/infographics")
def info_graphics():
    resp = make_response(
        render_template("infographics.html", graphSet=getRandomGraph())
    )
    resp.set_cookie("track_time", datetime.datetime.now().isoformat())
    return resp


def getGraphSet(graphId):
    for ele in graphSet:
        if ele["id"] == graphId:
            return ele
    return None


def getQuestion(graphId, id):
    graphSet = getGraphSet(graphId)
    for question in graphSet["questions"]:
        if question["id"] == id:
            return question
    return None


def getScore(graphId, data):
    score = 0
    for ele in data:
        # find the question with id
        question = getQuestion(graphId, ele["id"])
        if question["correctAnswer"] == ele["answer"]:
            score += 1

    return score / len(data)


@app.route("/submit", methods=["POST"])
def submit():
    data = request.get_json()
    d = {
        "graphId": data["graphId"],
        "time": data["totalTime"],
        "score": getScore(data["graphId"], data["answers"]),
    }
    write_to_csv(d)
    return json.dumps({"success": True}), 200, {"ContentType": "application/json"}


@app.route("/analysis")
def analysis():
    graphId = int(request.args.get("graphId"))
    X, Y = read_csv("./data.csv", graphId)

    fileName = "/analysis.html"
    resp = make_response(
        render_template(
            fileName, X=X, Y=Y, graphImage=getGraphSet(graphId)["graphImage"]
        )
    )
    return resp


def write_to_csv(dict):
    field_names = ["graphId", "time", "score"]

    with open("data.csv", "a") as csv_file:
        dict_object = csv.DictWriter(csv_file, fieldnames=field_names)

        dict_object.writerow(dict)


def read_csv(path, graphId):
    x = []
    y = []
    with open(path, "r") as file:
        reader = csv.reader(file)
        for row in reader:
            if row:
                x.append(float(row[1]))
                y.append(float(row[2]))
    return (x, y)


if __name__ == "__main__":
    app.run(debug=True)
