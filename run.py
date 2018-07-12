import os
import json
from flask import Flask, redirect, render_template, request, url_for, session
import random
from operator import itemgetter

app = Flask(__name__)
app.secret_key = os.urandom(24)

def read_json(file_name):
    with open(file_name, 'r') as f:
        data = json.load(f)
    return data
    
def write_json(file_name, data):
    with open(file_name, 'w') as f:
        json.dump(data, f)
    
def get_player_detail(player_name, file_name):
    players = read_json('data/players.json')
    if len(players) == 0:
        return False
    for p in players:
        if p["player_name"] == player_name:
            return p
    return False

def add_new_player(player_name, password, file_name):
    player = {"player_name": player_name, "top_score": 0, "current_score": 0, "password": password, "logged_in": False}
    players = read_json('data/players.json')
    players.append(player)
    write_json(file_name, players)
    
    return player
    
def change_online_status(player_name, file_name, status):
    data = read_json(file_name)
    for d in data:
        if d["player_name"] == player_name:
            d["logged_in"] = status
            with open(file_name, 'w') as f:
                json.dump(data, f)
            return
        
def all_log_off(file_name):
    data = read_json(file_name)
    for d in data:
        d["logged_in"] = False
        with open(file_name, 'w') as f:
            json.dump(data, f)
        return
    
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
    return answer.capitalize() in riddle["A"]
    
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

@app.before_first_request
def startup():
    try:
        session.pop('player', None)
        all_log_off('data/players.json')
    except:
        write_json('data/players.json', [])


@app.route('/', methods=['GET', 'POST'])
def index():
    
    #Handle POST requests
    if request.method == "POST":
        if get_player_detail(request.form['player_name'], 'data/players.json') == False:
            player = add_new_player(request.form['player_name'], request.form['password'], 'data/players.json')
            change_online_status(request.form['player_name'], 'data/players.json', True)
            session['player'] = player
            return redirect(url_for('player', player_name=request.form['player_name']))
        else:
            player = get_player_detail(request.form['player_name'], 'data/players.json')
            if player['logged_in']:
                return render_template("index.html", logged_in=True)
            elif request.form['password'] == player['password']:
                change_online_status(request.form['player_name'], 'data/players.json', True)
                session['player'] = player
                return redirect(url_for('player', player_name=request.form['player_name']))
            else:
                return render_template("index.html", login_failed=True)
    
    # Prevent player from going back to login page using unintended methods.         
    if 'player' in session:
        return redirect(url_for('player', player_name=session['player']['player_name']))
        
    return render_template("index.html", login_failed=False)

@app.route('/player/<player_name>')
def player(player_name):
    if 'player' in session:
        player = session['player']
        session['qs'] = [x+1 for x in range(len(read_json('data/riddles.json')))]
        session['wrong_answers'] = []
        return render_template("player.html", player=player, player_name=player_name, player_access=True)
    return render_template("stray.html")
    
@app.route('/player/<player_name>/riddles')
def riddles(player_name):
    if 'player' in session:
        session['q'] = random.choice(session['qs'])
        return redirect(url_for('riddle', player_name=player_name, riddleID=session['q']))
        
    return render_template("stray.html")
    
@app.route('/player/<player_name>/riddles/<riddleID>', methods=['GET', 'POST'])
def riddle(player_name, riddleID):
    if 'player' in session:
        player = session['player']
        riddle = get_riddle('data/riddles.json', riddleID)
        if request.method == "POST":
            if pass_riddle(request.form["answer"]):
                session['wrong_answers'] = []
                return redirect(url_for('riddles', player_name=player_name))
            else:
                return redirect(url_for('answer', player_name=player_name, riddleID=riddleID, answer=request.form["answer"]))
        if len(session['wrong_answers']) == 0:
            return render_template("riddles.html", player=player, riddle=riddle)
        else:
            return render_template("riddles.html", player=player, riddle=riddle, wa=session['wrong_answers'])
    return render_template("stray.html")

@app.route('/player/<player_name>/riddles/<riddleID>/<answer>', methods=['GET', 'POST'])
def answer(player_name, riddleID, answer):
    if 'player' in session:
        riddle = get_riddle('data/riddles.json', riddleID)
        if correct_answer(riddle, answer):
            session['player']['current_score'] += 1
            session['wrong_answers'] = []
            session['qs'].remove(int(session['q']))
            print(str(session['qs']))
            return redirect(url_for('riddles', player_name=player_name))
        else:
            wrong_answers = session['wrong_answers']
            wrong_answers.append(answer.capitalize())
            session['wrong_answers'] = wrong_answers
            print(str(session['wrong_answers']))
            return redirect(url_for('riddle', player_name=player_name, riddleID=riddleID))
    return render_template("stray.html")
        
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
    change_online_status(player_name, 'data/players.json', False)
    session.pop('player', None)
    return redirect('/')
    
if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True, threaded=True)