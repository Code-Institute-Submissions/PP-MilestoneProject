import os
import json
from flask import Flask, redirect, render_template, request

app = Flask(__name__)

def read_player_json(file_name):
    with open(file_name, 'r') as f:
        data = json.load(f)
    return data
    
def read_player_detail(player_name, file_name):
    if zero_player(file_name):
        return {"player_name": player_name + "(guest)", "score": "place_holder"}
    else:
        players = read_player_json('data/player.json')
        for p in players:
            if p["player_name"] == player_name:
                player_detail = p
                return player_detail

def write_to_player_json(player_name, file_name):
    player = {"player_name": player_name, "score": 0}
    players = read_player_json('data/player.json')
    
    players.append(player)
    
    with open(file_name, 'w') as f:
        json.dump(players, f)
        
def zero_player(file_name):
    players = read_player_json('data/player.json')
    return len(players) == 0

def is_new_player(player_name, file_name):
    with open(file_name, 'r') as f:
        players = json.load(f)
        
    for p in players:
        if p['player_name'] == player_name:
            return False
        else:
            return True

@app.route('/', methods=['GET', 'POST'])
def index():
    #Handle POST requests
    if request.method == "POST":
        if is_new_player(request.form['player_name'], 'data/player.json') or zero_player('data/player.json'):
            write_to_player_json(request.form["player_name"], 'data/player.json')
        return redirect(request.form["player_name"])
    return render_template("index.html")
    
@app.route('/<player_name>')
def player(player_name):
    player_detail = read_player_detail(player_name, 'data/player.json')
    return render_template("player.html", player=player_detail) # Return template output if read failed.
    
@app.route('/<player_name>/riddles')
def riddles(player_name):
    player_detail = read_player_detail(player_name, 'data/player.json')
    return render_template("riddles.html", player=player_detail)
    
if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)