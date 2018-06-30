# Practical Python Milestone Project
<details><summary>Details</summary>

- The aim of this project is to build a web application game that asks players to guess the answer to a pictorial or text-based riddle.
- The player is presented with an image or text that contains the riddle.
- Players enter their answer into a textarea and submit their answer using a form.
- If a player guesses correctly, they are redirected to the next riddle. If a player guesses incorrectly, their incorrect guess is stored and printed below the riddle. The textarea is cleared so they can guess again.
- Multiple players can play an instance of the game at the same time. Users are identified by a unique username.
- A leaderboard is also available for users to check their top scores and how they fare against other players.

</details>

*****

## Technical details

<details><summary>Details</summary>
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

</details>

*****

## Change Log

### 30/06/2018
- Further improve routing so that player can log in directly by entering the correct URL.
- Added warning message when player enter a name that is currently being used when attempting to log in.
- Added button to go back to player page when leaderboard is accessed from there.

### 27/06/2018
- leaderboard.html implemented.
- Further improve routing to accommodate the addition of leaderboard.
- Added test class related to leaderboard.
- Updated testRoute test class to reflect new routing.

### 25/06/2018
- Functionality related to riddles processing has been implemented in full (checks for correct answer and update score), except for simultaneous use case scenario.

### 24/06/2018
- Added player options to player.html in form of buttons.
- Player login now also does uniquesness check so that no duplicates of player name are allowed in player.json
- riddles.html template implemented.

#### 21:04
- riddles.html will now display riddle with answer text space below. A new riddle will be chosen randomly on each load.
- Improved routing on riddles

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

### Data manuipluation with player.json
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

As the function to identify whether or not a player name entered exists in player.json has been implemented, further tests has been put in place to ensure that the application will not create duplicates of player record in player.json. This serves as the first step of implementing the requirement "Multiple players can play an instance of the game at the same time" where players are identified by a unique player name.

### Logic of processing riddles
Players are instructed that if they want to pass a riddle, they can do so by submitting a blank answer. This will also in turn saves the effort of implementing code to check "whether a blank answer is the correct answer" or possible bug that may arise by submitting a blank answer. What the application does actually is that when player submits a blank answer, the page reloads and display a new riddle, nothing else. 

As for handling POST request, the code will look something like this:
```python
if request.method == "POST":
        if pass_riddle(request.form["answer"]):
            return render_template("riddles.html", player=player_detail, riddle=riddle)
        else:
            print("checking answer")
```
At this stage it might be better to test the result manually rather writting tests since all that is needed it to check if the string "checking answer" printed onto the console when something is entered into the text space.

That said, it would be reasonable to write tests to test the behaviour of the overall logic of processing riddles once the code is in a more complete state. The elementes that need to be tested are:
- Identifying whether player has submitted a correct answer or not.
- Updating scores.
- Displaying wrong answers as per requirements.

### Sorting out player scores and displaying on leaderboard.html
First of all, leaderboard.html can be reached via 2 different routes:
- /leaderboard
- /player/<player_name>/leaderboard

As far as routing test is concerned, both route needs to be tested independently.

On the other hand, in order to simplify testing for sorting scores and displaying them on leaderboard.html, a preset of data is used as follows:
```python
test_data = [
            {"score": 0, "player_name": "a"}, 
            {"score": 5, "player_name": "b"}, 
            {"score": 3, "player_name": "c"}, 
            {"score": 2, "player_name": "d"}]
write_json('data/player.json', test_data)
```
where write_json is a function from run.py for writing data directly into player.json
```python
def write_json(file_name, data):
    with open(file_name, 'w') as f:
        json.dump(data, f)
```
As for actually testing whether scores are sorted and displayed correctly, we can check where does certain data exist in the html document and see if certain elements exists before some other. This can be achieved by first converting html document into string and use .index() to find out location of certain elements, which will then be used for comparison to check if order is correct.

### Multiple users use case scenario
Since it was not mentioned in the requirement that user authentication is required, as long as all current players within the instance are unique to each other (identified by their player name) it would suffice. This can be tested by submitting multiple log in request with the same player name. Once the first request has been processed the application should not allow further log in attempts with the same name until the said name is no longer active.