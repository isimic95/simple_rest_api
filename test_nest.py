import unittest
import json

from nest import nest


class TestNest(unittest.TestCase):
    def setUp(self):
        with open('input.json') as js:
            self.input = json.load(js)

    def test_too_many_levels(self):
        result, success = nest(self.input, ['currency', 'amount', 'city', 'country'])

        self.assertFalse(success)

    def test_invalid_key(self):
        result, success = nest(self.input, ['currency', 'i_dont_exist'])

        self.assertFalse(success)

    def test_nesting_1_level(self):
        result, success = nest(self.input, ['currency'])
        expected = {'USD': [{'country': 'US', 'city': 'Boston', 'amount': 100}],
                    'EUR': [{'country': 'ES', 'city': 'Madrid', 'amount': 8.9}],
                    'GBP': [{'country': 'UK', 'city': 'London', 'amount': 12.2}],
                    'FBP': [{'country': 'UK', 'city': 'London', 'amount': 10.9}]}

        self.assertEqual(result, expected)

    def test_nesting_max_level(self):
        result, success = nest(self.input, ['currency', 'country', 'city'])
        expected = {'USD': {'US': {'Boston': [{'amount': 100}]}},
                    'EUR': {'ES': {'Madrid': [{'amount': 8.9}]}},
                    'GBP': {'UK': {'London': [{'amount': 12.2}]}},
                    'FBP': {'UK': {'London': [{'amount': 10.9}]}}}

        self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()
