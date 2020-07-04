import unittest
import mainvk

class TestVK(unittest.TestCase):
    def test_get_country_id(self):
        self.assertEqual(mainvk.get_country_id('RU'), 1)

    def test_get_city_id(self):
        self.assertEqual(mainvk.get_city_id('Москва', '1'), 1)

    def test_invalid_token(self):
        self.assertRaises(KeyError)
    



if __name__ == "__main__":
    unittest.main()
