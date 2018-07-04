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
    
def write_json(file_name, data):
    with open(file_name, 'w') as f:
        json.dump(data, f)
        
def create_new_jsonfile(file_name):
    with open(file_name, 'w') as f:
        json.dump([], f)
    
def read_player_detail(player_name, file_name):
    players = read_json('data/players.json')
    if len(players) == 0:
        return {"player_name": "temp_player", "score": 0}
    for p in players:
        if p["player_name"] == player_name:
            return p

def register_new_player(player_name, file_name):
    player = {"player_name": player_name, "score": 0}
    players = read_json('data/players.json')
    
    players.append(player)
    
    write_json(file_name, players)

def is_new_player(player_name, file_name):
    players = read_json('data/players.json')
    
    if len(players) == 0:
        return True
    else:
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

def add_active_player(player_name):
    active_players = read_json('data/active_players.json')
    active_players.append(player_name)
    write_json('data/active_players.json', active_players)

def is_player_active(player_name):
    active_players = read_json('data/active_players.json')
    return player_name in active_players
    
def player_logout(player_name):
    active_players = read_json('data/active_players.json')
    active_players.remove(player_name)
    write_json('data/active_players.json', active_players)
    

@app.route('/', methods=['GET', 'POST'])
def index():
    if not os.path.exists('data/players.json'):
        create_new_jsonfile('data/players.json')
    if not os.path.exists('data/active_players.json'):
        create_new_jsonfile('data/active_players.json')
    #Handle POST requests
    if request.method == "POST":
        if is_player_active(request.form["player_name"]):
            return render_template("index.html", login_failed=True, player_access=False)
        else:
            return redirect('/login/' + request.form["player_name"])
    return render_template("index.html", login_failed=False, player_access=False)

@app.route('/login/<player_name>')
def login(player_name):
    if is_new_player(player_name, 'data/players.json'):
        register_new_player(player_name, 'data/players.json')
        add_active_player(player_name)
        return redirect('/player/' + player_name)
    else:
        add_active_player(player_name)
        return redirect('/player/' + player_name)

@app.route('/player/<player_name>')
def player(player_name):
    if not is_player_active(player_name):
        return redirect('/stray')
    clean_wrong_answers(player_name)
    player_detail = read_player_detail(player_name, 'data/players.json')
    return render_template("player.html", player=player_detail, player_name=player_name, player_access=True)
    
@app.route('/player/<player_name>/riddles')
def riddles(player_name):
    if not is_player_active(player_name):
        return redirect('/stray')
    riddleID = get_riddleID('data/riddles.json')
    return redirect(url_for('riddle', player_name=player_name, riddleID=riddleID))
    
@app.route('/player/<player_name>/riddles/<riddleID>', methods=['GET', 'POST'])
def riddle(player_name, riddleID):
    if not is_player_active(player_name):
        return redirect('/stray')
    player_detail = read_player_detail(player_name, 'data/players.json')
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
    if not is_player_active(player_name):
        return redirect('/stray')
    riddle = get_riddle('data/riddles.json', riddleID)
    if correct_answer(riddle, answer):
        update_score(player_name, 'data/players.json')
        clean_wrong_answers(player_name)
        return redirect(url_for('riddles', player_name=player_name))
    else:
        file_name = "data/" + player_name + "_wa.txt"
        add_wrong_answer(file_name, answer)
        return redirect(url_for('riddle', player_name=player_name, riddleID=riddleID))
        
@app.route('/leaderboard')
def leaderboard():
    scores = sorted(read_json('data/players.json'), key=itemgetter('score'), reverse=True)
    return render_template("leaderboard.html", scores=scores, player_access=False)
    
@app.route('/leaderboard/<player_name>')
def player_leaderboard(player_name):
    scores = sorted(read_json('data/players.json'), key=itemgetter('score'), reverse=True)
    return render_template("leaderboard.html", scores=scores, player_name=player_name, player_access=True)
    
@app.route('/player/<player_name>/logout')
def logout(player_name):
    active_players = read_json('data/active_players.json')
    if player_name in active_players:
        player_logout(player_name)
    
    return redirect('/')
    
@app.route('/stray')
def stray():
    return render_template("stray.html")
    
if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=False, threaded=True)