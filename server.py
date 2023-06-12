from flask import Flask, render_template, make_response, request
import datetime
import json
import random
import csv
import os

TEMPLATE_PATH = "./templates"

app = Flask(__name__)

questions = [
    {
        "id": 1,
        "question": "Question 1",
        "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
        "graphImage": "../static/assets/graphs/graph1.png",
        "correctAnswer": 0,
    },
    {
        "id": 2,
        "question": "Question 2",
        "options": ["Option 10", "Option 2", "Option 3", "Option 4"],
        "graphImage": "../static/assets/graphs/graph2.png",
        "correctAnswer": 1,
    },
    {
        "id": 3,
        "question": "Question 3",
        "options": ["Option 10", "Option 2", "Option 3", "Option 4"],
        "graphImage": "../static/assets/graphs/graph3.png",
        "correctAnswer": 1,
    },
]


def getNumberOfFiles(path):
    return len(os.listdir(path))


def getFileName(path, index):
    return path + "/" + os.listdir(TEMPLATE_PATH + path)[index]


@app.route("/")
def home():
    fileName = "/index.html"
    resp = make_response(render_template(fileName))
    return resp


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/infographics")
def info_graphics():
    resp = make_response(render_template("infographics.html", questions=questions))
    resp.set_cookie("track_time", datetime.datetime.now().isoformat())
    return resp


def getQuestion(id):
    for question in questions:
        if question["id"] == id:
            return question
    return None


def getScore(data):
    score = 0
    for ele in data:
        # find the question with id
        question = getQuestion(ele["id"])
        if question["correctAnswer"] == ele["answer"]:
            score += 1

    return (score/len(data))


@app.route("/submit", methods=["POST"])
def submit():
    data = request.get_json()
    # print(request.cookies)
    # time_str = request.cookies["track_time"]
    # print(time_str)
    # old_time = datetime.datetime.fromisoformat(time_str)
    # curr_time = datetime.datetime.now()
    # time = (curr_time - old_time).seconds
    d = {"time": data["totalTime"], "score": getScore(data["answers"])}
    print(d)
    write_to_csv(d)
    return json.dumps({"success": True}), 200, {"ContentType": "application/json"}


@app.route("/analysis")
def analysis():
    X, Y = read_csv("./data.csv")
    fileName = "/analysis.html"
    print(fileName)
    resp = make_response(render_template(fileName, X=X, Y=Y))
    return resp


def write_to_csv(dict):
    field_names = ["time", "score"]

    with open("data.csv", "a") as csv_file:
        dict_object = csv.DictWriter(csv_file, fieldnames=field_names)

        dict_object.writerow(dict)


def read_csv(path):
    x = []
    y = []
    with open(path, "r") as file:
        reader = csv.reader(file)
        for row in reader:
            print(row)
            if row:
                x.append(float(row[0]))
                y.append(float(row[1]))
    return (x, y)


if __name__ == "__main__":
    app.run(debug=True)
