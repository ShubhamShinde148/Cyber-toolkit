import unittest
from app import app

class AppTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()

    def test_dashboard_page_loads(self):
        response = self.client.get('/dashboard')
        self.assertEqual(response.status_code, 200)
    
    def test_api_stats_returns_json(self):
        response = self.client.get('/api/stats')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.is_json)
        json_data = response.get_json()
        self.assertIn('version', json_data)
        self.assertIn('features', json_data)

    def test_index_page_loads(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
