# Practical Python Milestone Project
The aim of this project is to build a web application game that asks players to guess the answer to a pictorial or text-based riddle. Players will be identified by their player name of choice and go through a game loop of ten questions. Multiple player can access to the same instance of the game at the same time. Each time player achieve a new high score the said score will be saved and displayed on leaderboard.

## UX
As this project has gaming elements involved, it is necessary to make the game easy to approach and user-friendly for any kind of users. In other words, users should find this app enjoyable to use.

As a basic flow of this web app:
1. User will first log into the game using a player name and password of their choice.
2. They will then be directed to their individual user page at which point they can start the game right away or head to leaderboard.
3. Once they decided to start the game, they will be given ten questions to answer. The order of questions is random each time users start a new game.
4. To proceed with the game, users need to give the correct answer and the game will end once they have answered 10 questions. If users are stuck they can reveal hint which they might help helpful. Furthermore, users are given the choice to pass a question or end the game any time they want.
5. Once a game session is finished, users will be directed back to their player's page with a pop-up reporting their result from their recent session.

The flow above serves as the main loop of this web app. Users can continue to loop through the game until they decide to log out.

## Features
- User login: as part of requirement, the web app needs to be capable of having multiple users in the same instance of the game, each being unique. Due to this requirement a pseudo user login system has been implemented. When a user is logged in with a particular player name, that player record will be marked as active in data file and no other users can log in using that player name until the active mark has been removed. Also, to prevent unforeseen situations where a player record has been marked active despite no user actually using it all player record will have their active mark removed automatically after 10 minutes of inactivity.
- Player's page: once a user is logged in they will be first directed to their player's page. At this point the player's page also becomes the user's home page.
- Leaderboard: a separate page showing all players' top score. If users are logged in their top score will be highlighted.
- Riddle game: the main feature of this web app. The riddles used in the game are stored in a JSON file and is picked at random during the game. Due to how the routes are designed, users can play the game almost entirely through URL only, except for passing a question (i.e. users can directly access a question by changing URL, as well as answering it by appending the answer to URL).
- Hint: an add-on block to the riddle game. There is a hint button on riddle game's page and if users are struggling with a question they can click the hint button to reveal the hint.
- Game session report: after a game session is finished, whether by going all 10 questions or stopping midway, users will be directed back to their player's page. The report will be shown in forms of a modal.

### Features to be implemented
- Password change: as of this build of the web app there is no way to change the password of a player record as proper user authentication is not part of the requirements for this project however from the point of UX it is a feature that should be implemented.
- Add new riddles from within the app: in the case of expanding the library of riddles, new riddles can be added directly to the JSON file storing the riddles. However, this means that the web app needs to be re-deployed every time new riddles are added. This is very costly and should be avoided if possible. As a countermeasure a feature to add new riddles from within the app could be implemented. Furthermore, by making this feature available to all users it could help expanding the riddles library.

## Technologies Used
- [Flask](http://flask.pocoo.org/): Used as the framework of this project.
- [Bootstrap 4.0](https://getbootstrap.com/)
	- Toolkit for frontend styling. This is used in conjunction with custom CSS code to provide a unified style throughout different page of the web app.
    - [Flatly](https://bootswatch.com/flatly/) theme from [Bootswatch](https://bootswatch.com) has been used for this project.
- [JQuery](https://jquery.com/)
	- Simplifying DOM manipulation. In the scope of this project, it has been used for handling modal component.
- [coverage](https://coverage.readthedocs.io/en/v4.5.x/)
	- It is used during testing to ensure high coverage of code tested.

## Testing
Since this web app is mainly written in Python, it is possible to use unittest package of Python to automate tests. Elements being tested are:
- If routes can be reached without raising any errors.
- Redirecting to a particular route if users enter invalid URL.
- If the correct templates have been used for each route.
- Data manipulation of JSON files.
- Game logic:
	- Picking a question at random.
	- Submitting a correct answer.
	- Submitting an incorrect answer and displaying it afterwards.
	- Passing a question.
	- If all questions are used within a single game session.
	- Post game session processing such as producing a report.
All tests are included test_run.py file. Simply run the file to carry out tests. Furthermore, [coverage](https://coverage.readthedocs.io/en/v4.5.x/) has been used to ensure high level coverage of code tested and the coverage report is hosted on [GitHub Pages](https://comacoma.github.io/PP-MilestoneProject/).

### Responsive Design
Another thing to take note of is the responsive design of this project. Using a mobile-first approach, the web app has different layout depending on screen size. To be specific:
- A 1 column layout is used on small screens whilst components are more evenly spread across the page on large screens.
- By using Bootstrap, navigation bar becomes a collapsible menu on smaller screens and expand to a full bar on larger screens.
- Apart from layout difference, UX is pretty much the same in terms of how user can navigate throughout the app.

## Deployment
[Heroku](https://www.heroku.com/home) has been used to host this project, click [HERE](https://pp-milestone-colman.herokuapp.com/) to check out the hosted build of this project. Settings for both deployment model and development model are contained within the same file due to how the code is written, it is therefore the difference between deployment model and development model is very little. In particular:
- Debug mode will activate depending on whether environment variables are for IP and PORT are provided. If said values are provided, for example on Heroku, then debug mode is turned off (i.e. running in deployment settings). Otherwise debug mode
is turned on (i.e. running in development settings).

## Credits
### Riddles
- Riddles used (as well as image used for pictorial riddles) in this project are obtained from [doriddles.com](https://www.doriddles.com).
