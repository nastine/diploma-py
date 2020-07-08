import unittest
from unittest.mock import patch
import mainvk

class TestVK(unittest.TestCase):
    @patch('builtins.input', lambda *args: 'Россия')
    def get_country_code(self):
        self.assertEqual(mainvk.get_country_code(), 1)

    @patch('builtins.input', lambda *args: 'Москва')
    def test_get_city_id(self):
        self.assertEqual(mainvk.get_city_id('1'), 1)

    @patch('builtins.input', lambda *args: 'жен.')
    def test_check_sex(self):
        self.assertRaises(ValueError)

    @patch('builtins.input', lambda *args: 'двадцать-тридцать')
    def test_ckeck_age(self):
        self.assertRaises(ValueError)

    def test_invalid_token(self):
        self.assertRaises(KeyError)
    



if __name__ == "__main__":
    unittest.main()
