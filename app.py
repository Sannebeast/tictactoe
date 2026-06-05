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
    return """
<!DOCTYPE html>
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

    display: flex;
    flex-direction: column;
    align-items: center;
}

#board {
    display: grid;
    grid-template-columns: repeat(3, 100px);
    gap: 8px;
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

    display: flex;
    align-items: center;
    justify-content: center;

    transition: 0.15s;
}

button.cell:hover:not(:disabled) {
    transform: scale(1.05);
    background: #f0f0f0;
}

.x { color: red; }
.o { color: blue; }

.status {
    margin-top: 15px;
    font-size: 20px;
    font-weight: 600;
}

.newgame {
    margin-top: 10px;
    margin-bottom: 10px;
    padding: 10px 20px;
    font-size: 16px;
    font-weight: 600;

    cursor: pointer;
    border: none;
    border-radius: 12px;

    background: #4f46e5;
    color: white;

    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    transition: 0.2s;
}

.newgame:hover {
    background: #4338ca;
    transform: scale(1.05);
}
</style>

</head>

<body>

<div class="container">
    <h1>Tic Tac Toe</h1>

    <button class="newgame" onclick="newGame()">New Game</button>

    <div id="status"></div>
    <div id="board"></div>
</div>

<script>

async function newGame(){
    await fetch('/new', { method: 'POST' });
    await new Promise(r => setTimeout(r, 100));
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

        let display = v ? v : "";

        html += `<button class="cell ${cls}"
            onclick="move(${i})"
            ${v || data.winner ? "disabled" : ""}>
            ${display}
        </button>`;
    });

    document.getElementById("board").innerHTML = html;

    document.getElementById("status").innerHTML =
        data.winner ? "🏆 Winner: " + data.winner : "Turn: " + data.turn;
}

load();

</script>

</body>
</html>
"""


@app.route("/new", methods=["POST"])
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
        return jsonify({
            "board": create_board(),
            "turn": "X",
            "winner": None
        })

    return jsonify(doc.to_dict())


@app.route("/move", methods=["POST"])
def move():
    pos = request.json["pos"]

    doc_ref = games_ref.document("current")
    doc = doc_ref.get()

    if not doc.exists:
        return "No game", 400

    game = doc.to_dict()

    if game.get("winner"):
        return jsonify(game)

    if game["board"][pos] == "":
        game["board"][pos] = game["turn"]

        winner = check_winner(game["board"])

        if winner:
            game["winner"] = winner
        else:
            game["turn"] = "O" if game["turn"] == "X" else "X"

        doc_ref.set(game)

    return jsonify(game)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)