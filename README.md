# Practical Python Milestone Project

- The aim of this project is to build a web application game that asks players to guess the answer to a pictorial or text-based riddle.
- The player is presented with an image or text that contains the riddle.
- Players enter their answer into a textarea and submit their answer using a form.
- If a player guesses correctly, they are redirected to the next riddle. If a player guesses incorrectly, their incorrect guess is stored and printed below the riddle. The textarea is cleared so they can guess again.
- Multiple players can play an instance of the game at the same time. Users are identified by a unique username.
- A leaderboard is also available for users to check their top scores and how they fare against other players.

*****

## Technical details

- The Application will be styled with Bootstrap based theme and aiming for a responsive design.
- Riddles will be stored as JSON file. Each "riddle" will consists of the riddle - either as a string if it is text-based, or a URL to an image of it is pictorial. Ability to add new riddles from client side is not part of the requirement so should the riddle base requires update, they will be added to the JSON file directly.
- Due to requirement of displaying users scores, usernames and their scores will have to be stored in a file (likely on JSON format) on the server. Although this requirement can be achieved without having to store the data in a file (i.e. store data in a dictionary at runtime), such data will be lost if the application crashes. It is therefore more preferable to store these data in a file.
- For project purpose, the riddle base will be relatively small for example, 10 questions in total.
- However, as for incorrect answers to a riddle; it would be sufficient to store them only at runtime.
- As part of the requirement, the application allows multiple users to play the game at the same time whilst they are identified by a unique username. Because of this, the application will need to be able to identify when a user is trying to start the game with a username that is currently active and provide them with useful warning and guidance.
- Here is a rough representation of the flow:
  1. Users are prompted to enter their username. If the username entered is currently active a warning message will appear and promotes them to enter a new username.
  2. After logging in successfully, users will be provide a choice start the game right away or take a look at the leaderboard. At this point, it has been decided to have the actual game and leaderboard displayed separately, hence the need to let users choose what to do. This might change later on (i.e. have the game and leader board displayed at the same time so there will be no need to choose).
  3. As in requirement, users proceed to answer the riddles (retrieved from JSON file) with textarea provided.
    - If users answer correctly, they will be directed to the next riddle. For a added challenge to the users, the next riddle should be retrieved at random instead of the having the same order of riddles every time.
    - If users answer incorrectly, the answer will be stored in a list (only available at runtime) and displayed underneath the riddle.
    - As a extra option not specified in requirement, if users struggle with a riddle but would like to continue with the game, they are given the choice to pass. This can be implemented in forms of a button click or have the user send an answer consists of "nothing" (i.e. empty string).
  4. Users can quit the game at any time at which point the flow will start again from step 1.
- The application will follow a test-driven development strategy. Any details regarding testing will be provided [HERE](#Testing)
- Flask framework will be used and the application will be deployed using Heroku.

*****

## Change Log

### 23/06/2018
- Partial implementation of player.html
- Player login function implemented (without uniqueness check)

#### 14:26
- Template output for player.html implemented. This template will show when user attemp to change route/url directly instead of using form to login.

### 20/06/2018
- Riddles base (as json file) has been added. A new attribute "type" is added to each riddle. This is due to the fact that the application needs to identify what type of riddle has been chosen and use appropriate HTML to display the riddle correctly.

#### 15:21
- Added HTML templates.
- index.html implemented (UI only). 
- Added run.py (init script for the application) and its test script test_run.py.


*****

## <a name="Testing"></a>Testing

### Writing to player.json
For a starter the following pseudo code is used to test if data written to player.json as expected.
```python
def write_to_player_json():
    player = {"player_name": "dummy_player", "score": 0}
    with open('data/player.json') as f:
        data = json.load(f)
    
    data.append(player)
    
    with open('data/player.json', 'w') as f:
        json.dump(data, f)
```
And to test it:
```python
def test_write_to_player_json(self):
    with open('data/player.json', 'w') as f:
        json.dump([], f)
    for x in range(5):
        write_to_player_json()
    with open('data/player.json', 'r') as f:
        data = json.load(f)
        self.assertEqual(len(data), 5)
```
The reason why the function was called multiple times is to make sure new data is appended to player.json instead of overwritting the whole file. The function will be updated to take two parameters of player_name and file_name instead of hard-coded data.