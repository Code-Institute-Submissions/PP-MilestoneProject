import os
import json
from flask import Flask, redirect, render_template, request, url_for
import random
from operator import itemgetter

app = Flask(__name__)

def read_json(file_name):
    with open(file_name, 'r') as f:
        data = json.load(f)
    return data
    
def read_player_detail(player_name, file_name):
    if zero_player(file_name):
        return {"player_name": player_name, "score": 0}
    else:
        players = read_json('data/player.json')
        for p in players:
            if p["player_name"] == player_name:
                return p
        # Return template data if player name is not found in file
        return {"player_name": player_name, "score": 0}

def register_new_player(player_name, file_name):
    player = {"player_name": player_name, "score": 0}
    players = read_json('data/player.json')
    
    players.append(player)
    
    with open(file_name, 'w') as f:
        json.dump(players, f)
        
def zero_player(file_name):
    players = read_json('data/player.json')
    return len(players) == 0

def is_new_player(player_name, file_name):
    players = read_json('data/player.json')
        
    for p in players:
        if p['player_name'] == player_name:
            return False
        else:
            return True
    
def get_riddleID(file_name):
    data = read_json('data/riddles.json')
    return "Q" + str(random.randint(1, len(data)))
    
def get_riddle(file_name, ID):
    data = read_json('data/riddles.json')
    for d in data:
        if d["ID"] == ID:
            return d

def pass_riddle(answer):
    return len(answer) == 0

def correct_answer(riddle, answer):
    return riddle["A"] == answer.capitalize()
    
def update_score(player_name, file_name):
    data = read_json(file_name)
    for d in data:
        if d["player_name"] == player_name:
            d["score"] += 1
            with open(file_name, 'w') as f:
                json.dump(data, f)
            return

def add_wrong_answer(file_name, answer):
    with open(file_name, 'a') as f:
        f.writelines(answer + "\n")
        
def get_wrong_answers(file_name):
    wa = []
    with open(file_name, 'r') as f:
        wa = f.readlines()
    return wa
    
def clean_wrong_answers(player_name):
    file_name = "data/" + player_name + "_wa.txt"
    if os.path.isfile(file_name):
        os.remove(file_name)
    else:
        return

@app.route('/', methods=['GET', 'POST'])
def index():
    #Handle POST requests
    if request.method == "POST":
        if is_new_player(request.form['player_name'], 'data/player.json') or zero_player('data/player.json'):
            register_new_player(request.form["player_name"], 'data/player.json')
        return redirect(url_for('player', player_name=request.form["player_name"]))
    return render_template("index.html")
    
@app.route('/player/<player_name>')
def player(player_name):
    clean_wrong_answers(player_name)
    player_detail = read_player_detail(player_name, 'data/player.json')
    return render_template("player.html", player=player_detail) # Return template output if read failed.
    
@app.route('/player/<player_name>/riddles', methods=['GET', 'POST'])
def riddles(player_name):
    riddleID = get_riddleID('data/riddles.json')
    return redirect(url_for('riddle', player_name=player_name, riddleID=riddleID))
    
@app.route('/player/<player_name>/riddles/<riddleID>', methods=['GET', 'POST'])
def riddle(player_name, riddleID):
    player_detail = read_player_detail(player_name, 'data/player.json')
    riddle = get_riddle('data/riddles.json', riddleID)
    file_name = "data/" + player_name + "_wa.txt"
    if request.method == "POST":
        if pass_riddle(request.form["answer"]):
            clean_wrong_answers(player_name)
            return redirect(url_for('riddles', player_name=player_name))
        else:
            return redirect(url_for('answer', player_name=player_name, riddleID=riddleID, answer=request.form["answer"]))
    if os.path.isfile(file_name):
        wa = get_wrong_answers(file_name)
        return render_template("riddles.html", player=player_detail, riddle=riddle, wa=wa)
    else:
        return render_template("riddles.html", player=player_detail, riddle=riddle)

@app.route('/player/<player_name>/riddles/<riddleID>/<answer>', methods=['GET', 'POST'])
def answer(player_name, riddleID, answer):
    riddle = get_riddle('data/riddles.json', riddleID)
    if correct_answer(riddle, answer):
        update_score(player_name, 'data/player.json')
        clean_wrong_answers(player_name)
        return redirect(url_for('riddles', player_name=player_name))
    else:
        file_name = "data/" + player_name + "_wa.txt"
        add_wrong_answer(file_name, answer)
        return redirect(url_for('riddle', player_name=player_name, riddleID=riddleID))
        
@app.route('/leaderboard')
def leaderboard():
    scores = sorted(read_json('data/player.json'), key=itemgetter('score'), reverse=True)
    return render_template("leaderboard.html", scores=scores)
    
if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)