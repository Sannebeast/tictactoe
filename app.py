from flask import Flask, request, jsonify
from google.cloud import firestore
from datetime import datetime

app = Flask(__name__)
db = firestore.Client(project="cloudcomputing-498308")

games = {}

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
}

h1 {
    margin-bottom: 10px;
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
    transition: 0.2s;
}

button.cell:hover {
    background: #f0f0f0;
}

.x { color: red; }
.o { color: blue; }

.newgame {
    margin-top: 15px;
    padding: 12px 24px;
    font-size: 16px;
    font-weight: 600;
    cursor: pointer;
    border: none;
    border-radius: 12px;
    color: blue;
    background: #007bff;
    box-shadow: 0 4px 15px rgba(0,0,0,0.15);
    transition: all 0.2s ease;
}

.newgame:hover {
    background: #0069d9;
    transform: scale(1.03);
}

.savegame {
    margin-top: 15px;
    padding: 12px 24px;
    font-size: 16px;
    font-weight: 600;
    cursor: pointer;
    border: none;
    border-radius: 12px;
    color: green;
    background: #28a745;
    box-shadow: 0 4px 15px rgba(0,0,0,0.15);
    transition: all 0.2s ease;
}

.savegame:hover {
    background: #218838;
    transform: scale(1.03);
}

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
    <p>Click "New Game" to start playing!</p>

    <div id="status"></div>
    <div id="board"></div>
    <div id="buttons"></div>
</div>

<script>

async function newGame(){
    await fetch('/new');
    load();
}

async function saveGame(){
    let res = await fetch('/save', { method: 'POST' });
    let data = await res.json();

    if (res.ok) {
        alert("Game saved! ID: " + data.gameId);
    } else {
        alert("Save failed: " + data.error);
    }
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

    let status = "";
    let buttons = "";

    if (data.winner) {
        status = "🏆 Winner: " + data.winner;

        buttons = `
            <button class="savegame" onclick="saveGame()">Save game</button>
            <button class="newgame" onclick="newGame()">New Game</button>
        `;
    } else {
        status = "Turn: " + data.turn;

        buttons = `
            <button class="newgame" onclick="newGame()">New Game</button>
        `;
    }

    document.getElementById("status").innerHTML = status;
    document.getElementById("buttons").innerHTML = buttons;
}

load();

</script>

</body>
</html>
"""


@app.route("/new")
def new_game():
    games["current"] = {
        "board": create_board(),
        "turn": "X",
        "winner": None
    }
    return jsonify(games["current"])


@app.route("/state")
def state():
    return jsonify(games.get("current", {
        "board": create_board(),
        "turn": "X",
        "winner": None
    }))


@app.route("/move", methods=["POST"])
def move():
    pos = request.json["pos"]

    game = games.get("current")
    if not game:
        return "No game", 400

    if game.get("winner"):
        return jsonify(game)

    if game["board"][pos] == "":
        game["board"][pos] = game["turn"]

        winner = check_winner(game["board"])

        if winner:
            game["winner"] = winner
        else:
            game["turn"] = "O" if game["turn"] == "X" else "X"

    return jsonify(game)


@app.route("/save", methods=["POST"])
def save():
    try:
        game = games.get("current")

        if not game:
            return jsonify({"error": "No active game"}), 400

        game_id = "game-" + datetime.now().strftime("%Y%m%d-%H%M%S")

        print("ABOUT TO WRITE TO FIRESTORE")

        db.collection("games").document(game_id).set({
            "board": game["board"],
            "turn": game["turn"],
            "winner": game.get("winner"),
            "createdAt": firestore.SERVER_TIMESTAMP
        })

        print("WRITE SUCCESS")

        return jsonify({
            "status": "saved",
            "gameId": game_id
        })

    except Exception as e:
        print("FIRESTORE ERROR:", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)