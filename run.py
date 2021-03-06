import os
import json
import datetime
from datetime import datetime as dt
from flask import Flask, redirect, render_template, request, url_for, session, flash
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
    player = {"player_name": player_name, "top_score": 0, "password": password, "active": False, "last_active": "2018-01-01 00:00:00"}
    players = read_json('data/players.json')
    players.append(player)
    write_json(file_name, players)

    return player

def change_online_status(player_name, file_name, status):
    data = read_json(file_name)
    for d in data:
        if d["player_name"] == player_name:
            d["active"] = status
            write_json('data/players.json', data)

def log_last_active(player_name, file_name):
    data = read_json(file_name)
    for d in data:
        if d["player_name"] == player_name:
            d["last_active"] = dt.now().strftime('%Y-%m-%d %H:%M:%S')
            write_json('data/players.json', data)

def log_off_inactive(file_name):
    data = read_json(file_name)
    now = dt.now()
    for d in data:
        last_active = dt.strptime(d['last_active'], '%Y-%m-%d %H:%M:%S')
        if now - last_active > datetime.timedelta(minutes=10):
            d['active'] = False
        write_json('data/players.json', data)

def get_riddle(file_name, ID):
    data = read_json('data/riddles.json')
    for d in data:
        if d["ID"] == ID:
            return d

def pass_riddle(answer):
    return len(answer) == 0

def correct_answer(riddle, answer):
    return answer.capitalize() in riddle["A"]

def update_score(player_name, score, file_name):
    data = read_json(file_name)
    for d in data:
        if d["player_name"] == player_name:
            d["top_score"] = score
            write_json('data/players.json', data)

# Clear sessions and prepare players.json when application starts for the first time.
@app.before_first_request
def startup():
    try:
        read_json('data/players.json')
        if 'player' in session: # pragma: no cover
            session.pop('player', None)
    except:
        write_json('data/players.json', [])

@app.before_request
def before_request():
    log_off_inactive('data/players.json')

@app.route('/', methods=['GET', 'POST'])
def index():

    #Handle POST requests
    if request.method == "POST":
        if get_player_detail(request.form['player_name'], 'data/players.json') == False:
            # Action to take if it's a new player
            player = add_new_player(request.form['player_name'], request.form['password'], 'data/players.json')
            log_last_active(request.form['player_name'], 'data/players.json')
            change_online_status(request.form['player_name'], 'data/players.json', True)
            session['player'] = player['player_name']
            return redirect(url_for('player', player_name=request.form['player_name']))
        else:
            # Action to take if it's a returning player
            player = get_player_detail(request.form['player_name'], 'data/players.json')
            if player['active']:
                return render_template("index.html", logged_in=True)
            elif request.form['password'] == player['password']:
                log_last_active(request.form['player_name'], 'data/players.json')
                change_online_status(request.form['player_name'], 'data/players.json', True)
                session['player'] = player['player_name']
                return redirect(url_for('player', player_name=request.form['player_name']))
            else:
                return render_template("index.html", login_failed=True)

    # Prevent player from going back to login page using unintended methods.
    if 'player' in session:
        return redirect(url_for('player', player_name=session['player']))

    return render_template("index.html", login_failed=False)

@app.route('/player/<player_name>')
def player(player_name):
    player = get_player_detail(player_name, 'data/players.json')

    if 'player' in session and session['player'] == player['player_name'] and player['active']:
        player = get_player_detail(player_name, 'data/players.json')
        session['qs'] = [str(x) for x in range(len(read_json('data/riddles.json')))]
        session['wrong_answers'] = []
        session['current_score'] = 0
        return render_template("player.html", player=player)

    return render_template("stray.html")

@app.route('/player/<player_name>/riddles')
def riddles(player_name):
    player = get_player_detail(player_name, 'data/players.json')

    if 'player' in session and session['player'] == player['player_name'] and player['active']:
        if len(session['qs']) > 0:
            session['q'] = random.choice(session['qs'])
            return redirect(url_for('riddle', player_name=player_name, riddleID=session['q']))
        else:
           return redirect(url_for('game_finish', player_name=player_name))

    return render_template("stray.html")

@app.route('/player/<player_name>/riddles/<riddleID>', methods=['GET', 'POST'])
def riddle(player_name, riddleID):
    player = get_player_detail(player_name, 'data/players.json')

    # fall back logic if player skipped the 'riddles' route in a game loop
    if 'q' not in session:
        session['q'] = str(riddleID)

    if 'player' in session and session['player'] == player['player_name'] and player['active']:
        # Pick another question if player attempts to use URL to go back to
        #a question already attempted.
        if str(riddleID) not in session['qs']:
            return redirect(url_for('riddles', player_name=player_name))

        # Reassign session['q'] if player access directly with URL
        if str(riddleID) != session['q']: # pragma: no cover
            session['wrong_answers'] = []
            session['q'] = str(riddleID)

        riddle = get_riddle('data/riddles.json', riddleID)
        if request.method == "POST":
            if pass_riddle(request.form["answer"]):
                session['wrong_answers'] = []
                session['qs'].remove(str(session['q']))
                return redirect(url_for('riddles', player_name=player_name))
            else:
                return redirect(url_for('answer', player_name=player_name, riddleID=riddleID, answer=request.form["answer"]))
        if len(session['wrong_answers']) == 0:
            return render_template("riddles.html", riddle=riddle)
        else:
            return render_template("riddles.html", riddle=riddle, wa=session['wrong_answers'])

    return render_template("stray.html")

@app.route('/player/<player_name>/riddles/<riddleID>/<answer>', methods=['GET', 'POST'])
def answer(player_name, riddleID, answer):
    player = get_player_detail(player_name, 'data/players.json')

    if 'player' in session and session['player'] == player['player_name'] and player['active']:
        riddle = get_riddle('data/riddles.json', riddleID)

        if str(riddleID) not in session['qs']:
            return redirect(url_for('riddles', player_name=player_name))

        if correct_answer(riddle, answer):
            session['current_score'] += 1
            session['wrong_answers'] = []
            session['qs'].remove(str(session['q']))
            return redirect(url_for('riddles', player_name=player_name))
        else:
            wrong_answers = session['wrong_answers']
            wrong_answers.append(answer.capitalize())
            session['wrong_answers'] = wrong_answers
            return redirect(url_for('riddle', player_name=player_name, riddleID=riddleID))

    return render_template("stray.html")

@app.route('/player/<player_name>/game_finish')
def game_finish(player_name):
    player = get_player_detail(player_name, 'data/players.json')

    if 'player' in session and session['player'] == player['player_name'] and player['active']:
        # Current score from a recently finished game session will be recorded as top scores
        # if and only the current score is higher than top score recorded in file.
        if int(session['current_score']) > int(player['top_score']):
            update_score(player['player_name'], session.get('current_score'), 'data/players.json')

        flash("Here is the result of your last session:")
        flash("Score: " + str(session['current_score']))
        flash("Good job!")
        return redirect(url_for('player', player_name=player_name))

    return render_template("stray.html")

@app.route('/leaderboard')
def leaderboard():
    scores = sorted(read_json('data/players.json'), key=itemgetter('top_score'), reverse=True)
    return render_template("leaderboard.html", scores=scores)

@app.route('/player/<player_name>/logout')
def logout(player_name):
    change_online_status(player_name, 'data/players.json', False)
    session.pop('player', None)
    return redirect('/')

if __name__ == '__main__': # pragma: no cover
    if os.environ.get('IP') and os.environ.get('PORT'):
        app.run(host=os.environ.get('IP'),
                port=int(os.environ.get('PORT')),
                debug=False, threaded=True)
    else:
        app.run(debug=True, threaded=True)
