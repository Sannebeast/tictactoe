from flask import Flask, request, jsonify
from google.cloud import firestore

app = Flask(__name__)

db = firestore.Client()
games_ref = db.collection("games")

def create_board():
    return [""] * 9

def check_winner(b):
    wins = [
        [0,1,2],[3,4,5],[6,7,8],
        [0,3,6],[1,4,7],[2,5,8],
        [0,4,8],[2,4,6]
    ]

    for a, b1, c in wins:
        if b[a] == b[b1] == b[c] and b[a] != "":
            return b[a]
    return None


@app.route("/")
def home():
    return """YOUR HTML STAYS EXACTLY THE SAME (no change needed)"""


@app.route("/new")
def new_game():
    game = {
        "board": create_board(),
        "turn": "X",
        "winner": None
    }

    games_ref.document("current").set(game)
    return jsonify(game)


@app.route("/state")
def state():
    doc = games_ref.document("current").get()

    if not doc.exists:
        game = {
            "board": create_board(),
            "turn": "X",
            "winner": None
        }
        return jsonify(game)

    return jsonify(doc.to_dict())


@app.route("/move", methods=["POST"])
def move():
    pos = request.json["pos"]

    doc_ref = games_ref.document("current")
    doc = doc_ref.get()

    if not doc.exists:
        return "No game", 400

    game = doc.to_dict()

    # stop if game already finished
    if game.get("winner"):
        return jsonify(game)

    # valid move only
    if game["board"][pos] == "":
        game["board"][pos] = game["turn"]

        winner = check_winner(game["board"])

        if winner:
            game["winner"] = winner
        else:
            game["turn"] = "O" if game["turn"] == "X" else "X"

        # SAVE TO FIRESTORE
        doc_ref.set(game)

    return jsonify(game)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)