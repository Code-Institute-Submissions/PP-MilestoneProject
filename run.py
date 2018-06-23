import os
import json
from flask import Flask, redirect, render_template, request

app = Flask(__name__)

def write_to_player_json(player_name, file_name):
    player = {"player_name": player_name, "score": 0}
    with open(file_name) as f:
        data = json.load(f)
    
    data.append(player)
    
    with open(file_name, 'w') as f:
        json.dump(data, f)

def is_new_player(player_name, file_name):
    with open(file_name, 'r') as f:
        players = json.load(f)
    for p in players:
        if p['player_name'] == player_name:
            return True
        else:
            return False

@app.route('/', methods=['GET', 'POST'])
def index():
    #Handle POST requests
    if request.method == "POST":
        if is_new_player(request.form['player_name'], 'data/player.json'):
            write_to_player_json(request.form["player_name"], 'data/player.json')
        return redirect(request.form["player_name"])
    return render_template("index.html")
    
@app.route('/<player_name>')
def player(player_name):
    player_detail = {}
    with open('data/player.json', 'r') as f:
        players = json.load(f)
        for player in players:
            if player["player_name"] == player_name:
                player_detail = player
    return render_template("player.html", player=player)
    
if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)