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
    return """<!DOCTYPE html>
<html>
<head>
<title>Tic Tac Toe</title>

<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap" rel="stylesheet">

<style>
body {
    font-family: 'Poppins', sans-serif;
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
    margin: 0;
    background: #f4f6f8;
}

.container {
    text-align: center;
    background: white;
    padding: 30px;
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
}

#board {
    display: grid;
    grid-template-columns: repeat(3, 100px);
    grid-gap: 8px;
    justify-content: center;
    margin-top: 20px;
}

button.cell {
    width: 100px;
    height: 100px;
    font-size: 32px;
    font-weight: bold;
    cursor: pointer;
    border: 2px solid #333;
    background: #fff;
}

.x { color: red; }
.o { color: blue; }

.status {
    margin-top: 15px;
    font-size: 20px;
    font-weight: 600;
}
</style>

</head>

<body>

<div class="container">
    <h1>Tic Tac Toe</h1>

    <button onclick="newGame()">New Game</button>

    <div id="status"></div>
    <div id="board"></div>
</div>

<script>

async function newGame(){
    await fetch('/new');
    load();
}

async function move(i){
    await fetch('/move', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({pos:i})
    });
    load();
}

async function load(){
    let res = await fetch('/state');
    let data = await res.json();

    let html = "";

    data.board.forEach((v,i)=>{

        let cls = "";
        if (v === "X") cls = "x";
        if (v === "O") cls = "o";

        html += `<button class="cell ${cls}"
                    onclick="move(${i})"
                    ${v || data.winner ? "disabled" : ""}>
                    ${v}
                 </button>`;
    });

    document.getElementById("board").innerHTML = html;

    document.getElementById("status").innerHTML =
        data.winner ? "🏆 Winner: " + data.winner : "Turn: " + data.turn;
}

load();

</script>

</body>
</html>"""


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