from run import *
import unittest

#Helper function to clear out player.json
def reset_json(file_name):
    with open(file_name, 'w') as f:
        json.dump([], f)
        
#Helper function to write a particular set of data into player.json
def write_json(file_name, data):
    with open(file_name, 'w') as f:
        json.dump(data, f)

class testRoute(unittest.TestCase):
    """
    Test class related to routing
    """
    #To test if Flask is set up correctly
    def test_index(self):
        tester = app.test_client(self)
        response = tester.get('/', content_type="html/text")
        self.assertEqual(response.status_code, 200)
        
     #To test if the page loads correctly (index.html)
    def test_index_loads(self):
        tester = app.test_client(self)
        response = tester.get('/', content_type="html/text")
        self.assertTrue(b'Riddle Me These' in response.data)
        
    #To test if page loads correctly (player.html)
    def test_player_loads(self):
        tester = app.test_client(self)
        response = tester.get('player/dummy_player')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(b'Welcome, dummy_player' in response.data)
        
    #To test if page loads correctly (riddles.html)
    def test_riddles_loads(self):
        tester = app.test_client(self)
        response = tester.get('player/dummy_player/riddles', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(b'Welcome, dummy_player' in response.data)
        self.assertTrue(b'Your challenges begins,' in response.data)
        
    #To test if page loads correctly (leaderboard.html)
    def test_leaderboard_loads(self):
        tester = app.test_client(self)
        response = tester.get('leaderboard')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(b'Leaderboard is empty!' in response.data)
        
    #To test if leaderboard.html load correctly from another route
    def test_player_leaderboard_loads(self):
        tester = app.test_client(self)
        response = tester.get('player/dummy_player/leaderboard')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(b'Leaderboard is empty!' in response.data)

class testPlayerJson(unittest.TestCase):
    """
    Test class related to data manipulation with player.json
    """
    
    #To set up player.json before each tests in this class
    def setUp(self):
        reset_json('data/player.json')
            
    #To remove all data from player.json after all tests in this class
    @classmethod
    def tearDownClass(cls):
        reset_json('data/player.json')
    
    #To test if data is written to player.json as expected
    def test_register_new_player(self):
        for x in range(5):
            register_new_player('dummy_player', 'data/player.json')
        data = read_json('data/player.json')
        self.assertEqual(len(data), 5)
            
    #To test if data is read from player.json as expected
    def test_read_json(self):
        expected_data = [{'player_name': 'dummy_player', 'score': 0}]
        register_new_player('dummy_player', 'data/player.json')
        data = read_json('data/player.json')
        self.assertEqual(data, expected_data)
        
    #To test if player login form behaves as expected
    def test_login_form(self):
        tester = app.test_client(self)
        response = tester.post('/', data=dict(player_name = 'dummy_player'), follow_redirects = True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(b'Welcome, dummy_player' in response.data)
        
    #To test if application can identify both existing and new player
    def test_identify_player(self):
        register_new_player('dummy_player', 'data/player.json')
        self.assertFalse(is_new_player('dummy_player', 'data/player.json'))
        self.assertTrue(is_new_player('player', 'data/player.json'))
        
    """
    To Test if application refrains from creating duplicates of player record
    (i.e. multiple records with same player name)
    """
    def test_no_duplicates(self):
        tester = app.test_client(self)
        for x in range(5):
            tester.post('/', data=dict(player_name = 'dummy_player'), follow_redirects = False)
        data = read_json('data/player.json')
        self.assertEqual(len(data), 1)

class testRiddles(unittest.TestCase):
    """
    Test class related to retrieving, displaying, and processing riddles
    """
    
     #To set up player.json before each tests in this class
    def setUp(self):
        reset_json('data/player.json')
            
    #To remove all data after all tests in this class
    @classmethod
    def tearDownClass(cls):
        reset_json('data/player.json')
    
    #To test if application can tell if player submitted a correct answer or not
    def test_answer_riddle(self):
        riddle = get_riddle('data/riddles.json', "Q1")
        self.assertTrue(correct_answer(riddle, "ice"))
        self.assertFalse(correct_answer(riddle, "something else"))
    
    #To test if scores are updated correctly
    def test_update_score(self):
        tester = app.test_client(self)
        tester.post('/', data=dict(player_name = 'dummy_player'), follow_redirects = False)
        tester.post('/', data=dict(player_name = 'dummy_player2'), follow_redirects = False)
        tester.get('player/dummy_player/riddles/Q1/ice')
        data = read_json('data/player.json')
        self.assertEqual(data[0]["score"], 1)
        self.assertEqual(data[1]["score"], 0)
        
    #To test if wrong answers are displayed properly
    def test_display_wrong_answers(self):
        tester = app.test_client(self)
        tester.post('/', data=dict(player_name = 'dummy_player'), follow_redirects = False)
        response = tester.get('player/dummy_player/riddles/Q1/something', follow_redirects=True)
        self.assertTrue(b"Here are the wrong answers you have entered so far:" in response.data)
        self.assertTrue(b"something" in response.data)
        
class testLeaderboard(unittest.TestCase):
    """
    Test class related to leaderboard
    """
    
    #To set up player.json before each tests in this class
    def setUp(self):
        reset_json('data/player.json')
        
    #To remove all data after all tests in this class
    @classmethod
    def tearDownClass(cls):
        reset_json('data/player.json')
    
    #To test if player.json is read correctly and displayed in leaderboard.html
    def test_leaderboard_reads(self):
        tester = app.test_client(self)
        tester.post('/', data=dict(player_name = 'dummy_player'), follow_redirects = False)
        response = tester.get('leaderboard')
        self.assertTrue(b'Checkout how players are doing in this game of riddles.' in response.data)
        self.assertTrue(b'Player' in response.data)
        self.assertTrue(b'Score' in response.data)
        self.assertTrue(b'dummy_player' in response.data)
        self.assertTrue(b'0' in response.data)
    
    #To test if scores are sorted in descending order
    def test_scores_sorted(self):
        test_data = [
            {"score": 0, "player_name": "a"}, 
            {"score": 5, "player_name": "b"}, 
            {"score": 3, "player_name": "c"}, 
            {"score": 2, "player_name": "d"}]
        write_json('data/player.json', test_data)
        tester = app.test_client(self)
        html_out =  str(tester.get('leaderboard').data)
        self.assertTrue(html_out.index("<td>5</td>") < html_out.index("<td>3</td>"))
        self.assertTrue(html_out.index("<td>3</td>") < html_out.index("<td>2</td>"))
        self.assertTrue(html_out.index("<td>2</td>") < html_out.index("<td>0</td>"))
        
    #To test if score is highlighted when leaderboard is accessed from player page
    def test_highlight_player_score(self):
        test_data = [
            {"score": 0, "player_name": "a"}, 
            {"score": 5, "player_name": "b"}, 
            {"score": 3, "player_name": "c"}, 
            {"score": 2, "player_name": "d"}]
        write_json('data/player.json', test_data)
        tester = app.test_client(self)
        html_out =  str(tester.get('player/a/leaderboard').data)
        self.assertTrue(html_out.index('id="player_score"') < html_out.index("<td>a</td>"))
        self.assertTrue(html_out.index('id="player_score"') < html_out.index("<td>0</td>"))
        self.assertTrue(html_out.index('id="player_score"') > html_out.index("<td>b</td>"))
        self.assertTrue(html_out.index('id="player_score"') > html_out.index("<td>5</td>"))
    
if __name__ == '__main__':
    unittest.main()