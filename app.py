from flask import Flask, request, jsonify

app = Flask(__name__)

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

<style>
body {
    font-family: Arial;
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

.x {
    color: red;
}

.o {
    color: blue;
}

.status {
    margin-top: 15px;
    font-size: 20px;
    font-weight: bold;
}

.newgame {
    margin-top: 15px;
    padding: 10px 20px;
    font-size: 16px;
    cursor: pointer;
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

    let status = "";
    if (data.winner) {
        status = "🏆 Winner: " + data.winner;
    } else {
        status = "Turn: " + data.turn;
    }

    document.getElementById("status").innerHTML = status;
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

    # stop if game already won
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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)