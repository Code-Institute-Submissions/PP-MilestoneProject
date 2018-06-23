from run import *
import unittest

class testSuite(unittest.TestCase):
    """
    Test suite for this project
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
    
    #To test if data is written to player.json as expected
    def test_write_to_player_json(self):
        with open('data/dummy_player.json', 'w') as f:
            json.dump([], f)
        for x in range(5):
            write_to_player_json('dummy_player', 'data/dummy_player.json')
        with open('data/dummy_player.json', 'r') as f:
            data = json.load(f)
            self.assertEqual(len(data), 5)
    
    #To test if page loads correctly (player.html)
    def test_player_loads(self):
        tester = app.test_client(self)
        response = tester.get('/dummy_player')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(b'Welcome, dummy_player' in response.data)
        
    #To test if player login behaves as expected
    def test_login(self):
        tester = app.test_client(self)
        response = tester.post('/', data=dict(player_name = 'dummy_player'), follow_redirects = True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(b'Welcome, dummy_player' in response.data)
        
    #To test if application can identify both existing and new player
    def test_identify_player(self):
        self.assertTrue(is_new_player('dummy_player', 'data/dummy_player.json'))
        self.assertFalse(is_new_player('player', 'data/dummy_player.json'))
    
if __name__ == '__main__':
    unittest.main()