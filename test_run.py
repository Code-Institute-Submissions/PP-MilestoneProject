from run import *
import unittest

class testRoute(unittest.TestCase):
    """
    Test class for routing
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
        response = tester.get('/dummy_player')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(b'Welcome, dummy_player(guest)' in response.data)


class testSuite(unittest.TestCase):
    """
    Test suite for this project
    """
    
    #To set up player.json before each tests
    def setUp(self):
        with open('data/player.json', 'w') as f:
            json.dump([], f)
            
    #To remove all data from player.json after all tests
    @classmethod
    def tearDownClass(cls):
        with open('data/player.json', 'w') as f:
            json.dump([], f)
    
    #To test if data is written to player.json as expected
    def test_write_to_player_json(self):
        for x in range(5):
            write_to_player_json('dummy_player', 'data/player.json')
        data = read_player_json('data/player.json')
        self.assertEqual(len(data), 5)
            
    #To test if data is read from player.json as expected
    def test_read_player_json(self):
        expected_data = [{'player_name': 'dummy_player', 'score': 0}]
        write_to_player_json('dummy_player', 'data/player.json')
        data = read_player_json('data/player.json')
        self.assertEqual(data, expected_data)
        
    #To test if player login form behaves as expected
    def test_login_form(self):
        tester = app.test_client(self)
        response = tester.post('/', data=dict(player_name = 'dummy_player'), follow_redirects = True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(b'Welcome, dummy_player' in response.data)
        
    #To test if application can identify both existing and new player
    def test_identify_player(self):
        write_to_player_json('dummy_player', 'data/player.json')
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
        data = read_player_json('data/player.json')
        self.assertEqual(len(data), 1)
    
if __name__ == '__main__':
    unittest.main()