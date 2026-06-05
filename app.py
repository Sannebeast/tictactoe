from flask import Flask, request, jsonify
import random

app = Flask(__name__)

# in-memory fallback (we will later connect Firestore properly)
games = {}

def create_board():
    return [""] * 9

def check_winner(b):
    wins = [
        [0,1,2],[3,4,5],[6,7,8],
        [0,3,6],[1,4,7],[2,5,8],
        [0,4,8],[2,4,6]
    ]

    for a,b1,c in wins:
        if b[a] == b[b1] == b[c] and b[a] != "":
            return b[a]
    return None


@app.route("/")
def home():
    return """
    <h2>Tic Tac Toe</h2>
    <button onclick="fetch('/new').then(r=>r.json()).then(d=>location.reload())">
        New Game
    </button>
    <div id="board"></div>

    <script>
    async function load() {
        let res = await fetch('/state');
        let data = await res.json();

        let html = "";
        data.board.forEach((v,i)=>{
            html += `<button onclick="move(${i})" style="width:40px;height:40px">${v}</button>`;
            if ((i+1)%3==0) html += "<br>";
        });

        document.getElementById("board").innerHTML = html;
    }

    async function move(i){
        await fetch('/move', {
            method:'POST',
            headers:{'Content-Type':'application/json'},
            body: JSON.stringify({pos:i})
        });
        load();
    }

    load();
    </script>
    """


@app.route("/new")
def new_game():
    games["current"] = {
        "board": create_board(),
        "turn": "X"
    }
    return jsonify(games["current"])


@app.route("/state")
def state():
    return jsonify(games.get("current", {"board": create_board(), "turn":"X"}))


@app.route("/move", methods=["POST"])
def move():
    pos = request.json["pos"]

    game = games.get("current")
    if not game:
        return "No game", 400

    if game["board"][pos] == "":
        game["board"][pos] = game["turn"]

        winner = check_winner(game["board"])
        if winner:
            game["winner"] = winner
        else:
            game["turn"] = "O" if game["turn"] == "X" else "X"

    return jsonify(game)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)