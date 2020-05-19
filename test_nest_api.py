import unittest
import json
import sqlite3

from nest_api import app, DBInteraction


class TestNestAPI(unittest.TestCase):
    def setUp(self):
        self.api = app.test_client()
        self.db = DBInteraction(sqlite3.connect("nest_test.db"))
        with open('input.json') as js:
            self.input = json.load(js)

    def test_username_not_exists(self):
        self.assertFalse(self.db.user_exists('User1'))

    def test_username_exists(self):
        self.db.add_new_user('User1', 'password123')

        self.assertTrue(self.db.user_exists('User1'))
        self.db.delete_user('User1')

    def test_credentials(self):
        self.db.add_new_user('User2', 'password1234')

        self.assertTrue(self.db.verify_credentials('User1', 'password123'))
        self.db.delete_user('User2')

    def test_register(self):
        response = self.api.post(
            '/register', headers={"Content-Type": "application/json"},
            json={"username": "User1", "password": "password123"})

        self.assertEqual(200, response.status_code)
        self.db.delete_user('User1')

    def test_register_existing_username(self):
        self.api.post(
            '/register', headers={"Content-Type": "application/json"},
            json={"username": "User1", "password": "password123"})

        response = self.api.post(
            '/register', headers={"Content-Type": "application/json"},
            json={"username": "User1", "password": "password123"})

        self.assertEqual(409, response.status_code)
        self.db.delete_user('User1')

    def test_nest(self):
        self.api.post(
            '/register', headers={"Content-Type": "application/json"}, json={
                "username": "User1", "password": "password123"})

        response = self.api.post(
            '/nest?levels=currency,country,city',
            headers={"Content-Type": "application/json"},
            json={"username": "User1", "password": "password123", "data": self.input})

        self.assertEqual(response.json, {
            "EUR": {"ES": {"Madrid": [{"amount": 8.9}]}},
            "FBP": {"UK": {"London": [{"amount": 10.9}]}},
            "GBP": {"UK": {"London": [{"amount": 12.2}]}},
            "USD": {"US": {"Boston": [{"amount": 100}]}}
        })
        self.assertEqual(200, response.status_code)
        self.db.delete_user('User1')

    def test_nest_error(self):
        self.api.post('/register', headers={"Content-Type": "application/json"}, json={
                      "username": "User1", "password": "password123"})

        response = self.api.post(
            '/nest?levels=currency,country,city,idonotexist',
            headers={"Content-Type": "application/json"}, json={
                "username": "User1", "password": "password123",
                "data": self.input})

        self.assertEqual(400, response.status_code)
        self.db.delete_user('User1')


if __name__ == '__main__':
    unittest.main()
