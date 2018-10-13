from run import *
import datetime
from datetime import datetime as dt
import unittest

#Helper function to clear out players.json
def reset_json(file_name):
    with open(file_name, 'w') as f:
        json.dump([], f)

class TestRoute(unittest.TestCase):
    """
    Test class related to routing
    """

    #To set up a test client before every tests.
    def setUp(self):
        reset_json('data/players.json')
        self.app = app.test_client()
        app.config['SERVER_NAME'] = 'localhost'
        app.config['SECRET_KEY'] = 'secret_key'

     #To reset some values after each test
    def tearDown(self):
        with self.app.session_transaction() as sess:
            sess['q'] = None

    #To remove all data after all tests in this class
    @classmethod
    def tearDownClass(cls):
        reset_json('data/players.json')

    #To test if Flask is set up correctly
    def test_index(self):
        response = self.app.get('/', content_type="html/text")
        self.assertEqual(response.status_code, 200)

     #To test if the page loads correctly (index.html)
    def test_index_loads(self):
        response = self.app.get('/', content_type="html/text")
        self.assertTrue(b'Riddle Me These' in response.data)

    # To test if player is redirected back to their player's page is they are already logged in.
    def test_index_redirects(self):
        self.app.post('/', data=dict(player_name = 'dummy_player', password = 'dummy_player'), follow_redirects = True)
        response = self.app.get('/', follow_redirects = True)
        self.assertTrue(b'Welcome, dummy_player' in response.data)

    # To test if password are validated properly.
    def test_password_check(self):
        add_new_player('dummy_player', 'dummy_player', 'data/players.json')
        response = self.app.post('/', data=dict(player_name = 'dummy_player', password = 'wrong password'), follow_redirects = True)
        self.assertTrue(b"Login failed. Please make sure you have entered the details correctly." in response.data)

    #To test if page loads correctly (player.html)
    def test_player_loads(self):
        response = self.app.post('/', data=dict(player_name = 'dummy_player', password = 'dummy_player'), follow_redirects = True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(b'Welcome, dummy_player' in response.data)

    #To test if page loads correctly (riddles.html)
    def test_riddles_loads(self):
        self.app.post('/', data=dict(player_name = 'dummy_player', password = 'dummy_player'), follow_redirects = True)
        with self.app.session_transaction() as sess:
            sess['player'] = 'dummy_player'
            sess['qs'] = [str(x) for x in range(len(read_json('data/riddles.json')))]
            sess['wrong_answers'] = []
            sess['current_score'] = 0

        response = self.app.get('player/dummy_player/riddles', follow_redirects = True)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(b'Hi, dummy_player' in response.data)
        self.assertTrue(b'Your challenges begins,' in response.data)

    #To test if page loads correctly (riddles.html when accessed directly with URL)
    def test_riddles_direct_loads(self):
        self.app.post('/', data=dict(player_name = 'dummy_player', password = 'dummy_player'), follow_redirects = True)
        with self.app.session_transaction() as sess:
            sess['player'] = 'dummy_player'
            sess['qs'] = [str(x) for x in range(len(read_json('data/riddles.json')))]
            sess['q'] = '0'
            sess['wrong_answers'] = []
            sess['current_score'] = 0
        response = self.app.get('player/dummy_player/riddles/0', follow_redirects = True)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(b'Hi, dummy_player' in response.data)
        self.assertTrue(b'Your challenges begins,' in response.data)
        self.assertTrue(b'water' in response.data)

    # to test fall back logic when player skipped 'riddles' route in a game loop - extension to test above.
    def test_fall_back(self):
        self.app.post('/', data=dict(player_name = 'dummy_player', password = 'dummy_player'), follow_redirects = True)
        with self.app.session_transaction() as sess:
            sess['player'] = 'dummy_player'
            sess['qs'] = [str(x) for x in range(len(read_json('data/riddles.json')))]
            sess['wrong_answers'] = []
            sess['current_score'] = 0
        response = self.app.get('player/dummy_player/riddles/0', follow_redirects = True)

        self.assertEqual(response.status_code, 200)

    #To test if page loads correctly (leaderboard.html without player data)
    def test_leaderboard_loads(self):
        response = self.app.get('leaderboard')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(b'Leaderboard is empty!' in response.data)

    #To test if page loads correctly (leaderboard.html with player data)
    def test_leaderboard_loads_with_player_data(self):
        test_data = [{"player_name": "dummy_player", "password": "dummy_player", "top_score": 0, "active": False, "last_active": "2018-01-01 00:00:00"}]
        write_json('data/players.json', test_data)
        response = self.app.get('leaderboard')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(b'Rank' in response.data)
        self.assertTrue(b'Player' in response.data)
        self.assertTrue(b'Top Score' in response.data)
        self.assertTrue(b'dummy_player' in response.data)

    #To test if player is redirected to stray.html when routes are accessed without authentication
    def test_stray_loads(self):
        resp1 = self.app.get('player/a') # Non exising player 'a'
        resp2 = self.app.get('player/a/riddles')
        resp3 = self.app.get('player/a/riddles/0')
        resp4 = self.app.get('player/a/riddles/0/ice')
        resp5 = self.app.get('player/a/riddles/0/something')
        resp6 = self.app.get('player/a/game_finish')
        self.assertTrue(b'Hold on a second!' in resp1.data)
        self.assertTrue(b'Hold on a second!' in resp2.data)
        self.assertTrue(b'Hold on a second!' in resp3.data)
        self.assertTrue(b'Hold on a second!' in resp4.data)
        self.assertTrue(b'Hold on a second!' in resp5.data)
        self.assertTrue(b'Hold on a second!' in resp6.data)

    # To test if player can logout properly
    def test_logout(self):
        self.app.post('/', data=dict(player_name = 'dummy_player', password = 'dummy_player'), follow_redirects = True)
        player = get_player_detail('dummy_player', 'data/players.json')
        self.assertTrue(player['active'] == True)
        self.app.get('player/dummy_player/logout')
        player = get_player_detail('dummy_player', 'data/players.json')
        self.assertTrue(player['active'] == False)

class TestJsonManipulation(unittest.TestCase):
    """
    Test class related to data manipulation with .json file
    """

    #To set up player.json before each tests in this class
    def setUp(self):
        reset_json('data/players.json')
        app.config['SECRET_KEY'] = "test_key"
        self.app = app.test_client()

    #To remove all data from player.json after all tests in this class
    @classmethod
    def tearDownClass(cls):
        reset_json('data/players.json')

    #To test if application can create new data file when it is being used for the first time.
    def test_create_new_datafile(self):
        os.remove('data/players.json')
        self.app.get('/')
        self.assertTrue(os.path.exists('data/players.json'))

    #To test if data is written to player.json as expected
    def test_add_new_player(self):
        for x in range(5):
            add_new_player('dummy_player', 'password', 'data/players.json')
        data = read_json('data/players.json')
        self.assertEqual(len(data), 5)

    #To test if data is read from player.json as expected
    def test_read_json(self):
        expected_data = [{"player_name": 'dummy_player', "top_score": 0, "password": 'dummy_player', "active": False, "last_active": "2018-01-01 00:00:00"}]
        add_new_player('dummy_player', 'dummy_player', 'data/players.json')
        data = read_json('data/players.json')
        self.assertEqual(data, expected_data)

    #To test if application can identify new player
    def test_identify_player(self):
        add_new_player('dummy_player', 'dummy_player', 'data/players.json')
        self.assertFalse(get_player_detail('player', 'data/players.json')) # Identify as new player

    """
    To Test if application refrains from creating duplicates of player record
    (i.e. multiple records with same player name)
    """
    def test_no_duplicates(self):
        for x in range(5):
            self.app.post('/', data=dict(player_name = 'dummy_player', password = 'dummy_player'), follow_redirects = True)
        data = read_json('data/players.json')
        self.assertEqual(len(data), 1)

class TestRiddles(unittest.TestCase):
    """
    Test class related to retrieving, displaying, and processing riddles
    """

    #To set up player.json before each tests in this class
    def setUp(self):
        reset_json('data/players.json')
        self.app = app.test_client()
        app.config['SERVER_NAME'] = 'localhost'
        app.config['SECRET_KEY'] = 'secret_key'

    #To reset some values after each test
    def tearDown(self):
        with self.app.session_transaction() as sess:
            sess['q'] = None

    #To remove all data after all tests in this class
    @classmethod
    def tearDownClass(cls):
        reset_json('data/players.json')

    #To test if the function 'correct_answer' behaves as expected
    def test_answer_riddle(self):
        riddle = get_riddle('data/riddles.json', "0")
        self.assertTrue(correct_answer(riddle, "ice"))
        self.assertFalse(correct_answer(riddle, "something else"))

    #To test if application can tell if player submitted a correct answer or not
    def test_player_answer_riddle(self):
        self.app.post('/', data=dict(player_name = 'dummy_player', password = 'dummy_player'), follow_redirects = True)
        with self.app.session_transaction() as sess:
            sess['player'] = 'dummy_player'
            sess['qs'] = [str(x) for x in range(len(read_json('data/riddles.json')))]
            sess['q'] = '0'
            sess['wrong_answers'] = []
            sess['current_score'] = 0
        response = self.app.post('player/dummy_player/riddles/0', data={'answer': 'ice'}, follow_redirects = True)
        self.assertFalse(b"I AM THE SON OF WATER BUT WHEN I RETURN TO WATER. I DIE. WHO AM I?" in response.data)
        self.assertTrue(b'Your current score is 1' in response.data)

    #To test if current score is updated correctly
    def test_update_current_score(self):
        self.app.post('/', data=dict(player_name = 'dummy_player', password = 'dummy_player'), follow_redirects = True)
        with self.app.session_transaction() as sess:
            sess['player'] = 'dummy_player'
            sess['qs'] = [str(x) for x in range(len(read_json('data/riddles.json')))]
            sess['q'] = '0'
            sess['wrong_answers'] = []
            sess['current_score'] = 0
        response = self.app.get('player/dummy_player/riddles/0/ice', follow_redirects = True)
        self.assertTrue(b'Your current score is 1' in response.data)

    # To test if top scores are update correctly
    def test_update_top_score(self):
        self.app.post('/', data=dict(player_name = 'dummy_player', password = 'dummy_player'), follow_redirects = True)
        with self.app.session_transaction() as sess:
            sess['player'] = 'dummy_player'
            sess['qs'] = [str(x) for x in range(len(read_json('data/riddles.json')))]
            sess['q'] = '0'
            sess['wrong_answers'] = []
            sess['current_score'] = 1 # Assumed player answered 1 question correctly and decides to end the game.
        response = self.app.get('player/dummy_player/game_finish', follow_redirects = True)
        player = get_player_detail('dummy_player', 'data/players.json')
        self.assertEqual(player['top_score'], 1)

    #To test if wrong answers are displayed properly
    def test_display_wrong_answers(self):
        self.app.post('/', data=dict(player_name = 'dummy_player', password = 'dummy_player'), follow_redirects = True)
        with self.app.session_transaction() as sess:
            sess['player'] = 'dummy_player'
            sess['qs'] = [str(x) for x in range(len(read_json('data/riddles.json')))]
            sess['q'] = '0'
            sess['wrong_answers'] = []
            sess['current_score'] = 0
        response = self.app.get('player/dummy_player/riddles/0/something', follow_redirects=True)
        self.assertTrue(b"Here are the wrong answers you have entered so far:" in response.data)
        self.assertTrue(b"Something" in response.data)

    #To test if game loops through all questions
    def test_game_loop(self):
        self.app.post('/', data=dict(player_name = 'dummy_player', password = 'dummy_player'), follow_redirects = True)
        with self.app.session_transaction() as sess:
            sess['player'] = 'dummy_player'
            sess['qs'] = [str(x) for x in range(len(read_json('data/riddles.json')))]
            sess['wrong_answers'] = []
            sess['current_score'] = 0

            for y in range(len(read_json('data/riddles.json'))):
                sess['q'] = random.choice(sess['qs'])
                sess['qs'].remove(str(sess['q']))

        response = self.app.get('player/dummy_player/riddles', follow_redirects = True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(b'Here is the result of your last session:' in response.data)

    # To test if game prevents player from accessing the same question within a game loop
    def test_prevent_access_duplicate(self):
        self.app.post('/', data=dict(player_name = 'dummy_player', password = 'dummy_player'), follow_redirects = True)
        with self.app.session_transaction() as sess:
            sess['player'] = 'dummy_player'
            sess['qs'] = [str(x) for x in range(len(read_json('data/riddles.json')))]
            sess['q'] = '0'
            sess['wrong_answers'] = []
            sess['current_score'] = 0

        self.app.get('player/dummy_player/riddles/0/ice', follow_redirects=True)
        response = self.app.get('player/dummy_player/riddles/0', follow_redirects=True)
        self.assertFalse(b"I AM THE SON OF WATER BUT WHEN I RETURN TO WATER. I DIE. WHO AM I?" in response.data)

    # To test if game prevents player from actually answering the same question within a game loop through URL
    def test_prevent_answer_duplicate(self):
        self.app.post('/', data=dict(player_name = 'dummy_player', password = 'dummy_player'), follow_redirects = True)
        with self.app.session_transaction() as sess:
            sess['player'] = 'dummy_player'
            sess['qs'] = [str(x) for x in range(len(read_json('data/riddles.json')))]
            sess['q'] = '0'
            sess['wrong_answers'] = []
            sess['current_score'] = 0

        self.app.get('player/dummy_player/riddles/0/ice', follow_redirects=True)
        response = self.app.get('player/dummy_player/riddles/0/ice', follow_redirects=True)
        self.assertFalse(b"I AM THE SON OF WATER BUT WHEN I RETURN TO WATER. I DIE. WHO AM I?" in response.data)

    # To test if game proceeds as expected if player decides to skip a question
    def test_skip_question(self):
        self.app.post('/', data=dict(player_name = 'dummy_player', password = 'dummy_player'), follow_redirects = True)
        with self.app.session_transaction() as sess:
            sess['player'] = 'dummy_player'
            sess['qs'] = [str(x) for x in range(len(read_json('data/riddles.json')))]
            sess['q'] = '0'
            sess['wrong_answers'] = []
            sess['current_score'] = 0
        response = self.app.post('player/dummy_player/riddles/0', data={'answer': ''}, follow_redirects=True)
        self.assertFalse(b"I AM THE SON OF WATER BUT WHEN I RETURN TO WATER. I DIE. WHO AM I?" in response.data)

class TestLeaderboard(unittest.TestCase):
    """
    Test class related to leaderboard
    """

    #To set up player.json before each tests in this class
    def setUp(self):
        reset_json('data/players.json')
        self.app = app.test_client()
        app.config['SERVER_NAME'] = 'localhost'
        app.config['SECRET_KEY'] = 'secret_key'

    #To remove all data after all tests in this class
    @classmethod
    def tearDownClass(cls):
        reset_json('data/players.json')

    #To test if scores are sorted in descending order
    def test_scores_sorted(self):
        test_data = [
            {"top_score": 0, "player_name": "a", "password": "password", "active": False, "last_active": "2018-01-01 00:00:00"},
            {"top_score": 5, "player_name": "b", "password": "password", "active": False, "last_active": "2018-01-01 00:00:00"},
            {"top_score": 3, "player_name": "c", "password": "password", "active": False, "last_active": "2018-01-01 00:00:00"},
            {"top_score": 2, "player_name": "d", "password": "password", "active": False, "last_active": "2018-01-01 00:00:00"}]
        write_json('data/players.json', test_data)
        html_out = str(self.app.get('leaderboard').data)
        self.assertTrue(html_out.index("<td>b</td>") < html_out.index("<td>c</td>"))
        self.assertTrue(html_out.index("<td>c</td>") < html_out.index("<td>d</td>"))
        self.assertTrue(html_out.index("<td>d</td>") < html_out.index("<td>a</td>"))

    #To test if score is highlighted when player is logged in
    def test_highlight_player_score(self):
        test_data = [
            {"top_score": 0, "player_name": "a", "password": "password", "active": False, "last_active": "2018-01-01 00:00:00"},
            {"top_score": 5, "player_name": "b", "password": "password", "active": False, "last_active": "2018-01-01 00:00:00"},
            {"top_score": 3, "player_name": "c", "password": "password", "active": False, "last_active": "2018-01-01 00:00:00"},
            {"top_score": 2, "player_name": "d", "password": "password", "active": False, "last_active": "2018-01-01 00:00:00"}]
        write_json('data/players.json', test_data)
        self.app.post('/', data=dict(player_name = 'b', password = 'password'), follow_redirects = True)
        response = self.app.get('leaderboard')
        html_out = str(response.data)
        self.assertTrue(b'<tr class="table-success" id="player_score">' in response.data)
        self.assertTrue(html_out.index('<tr class="table-success" id="player_score">') < html_out.index("<td>b</td>"))

class TestMultipleUsers(unittest.TestCase):
    """
    Test class related to multiple concurrent users use case scenario
    """

    #To set up a test client before every tests.
    def setUp(self):
        reset_json('data/players.json')
        self.app = app.test_client()
        app.config['SERVER_NAME'] = 'localhost'
        app.config['SECRET_KEY'] = 'secret_key'

    #To remove all data after all tests in this class
    @classmethod
    def tearDownClass(cls):
        reset_json('data/players.json')

    #To test if application restricts login when player enters a name that is currently active
    def test_fail_login(self):
        self.app.post('/', data=dict(player_name = 'dummy_player', password = 'dummy_player'), follow_redirects = True)
        response = self.app.post('/', data=dict(player_name = 'dummy_player', password = 'dummy_player'), follow_redirects = True)
        self.assertTrue(b'This player is currently logged in on another machine. Please try again later.' in response.data)

if __name__ == '__main__':
    unittest.main()
