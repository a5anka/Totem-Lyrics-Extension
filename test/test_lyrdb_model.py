import unittest
from model.lyrdb_model import LyrdbModel

class TestLyrdbModel (unittest.TestCase):

    def setUp (self):
        self._model = LyrdbModel()
        
    def test_search_lyrics(self):
        result, message = self._model.search_lyrics("Michael Jackson", "thriller")
        if result:
            self.assertIsInstance(result,list)
            self.assertIsInstance(result[0],dict)
            self.assertEqual(result[0]['Artist'], "Michael Jackson")
        else:
            self.assertEqual(message, "Could not contact the server. Try again...")

    def test_download_lyrics(self):
        result,message = self._model.download_lyrics('131071',
                                             '2a3ea713422cbc97470b0c38c6e5a552')
        if result:
            self.assertIsInstance(result, str)
        else:
            self.assertEqual(message, "Could not contact the server. Try again...")
if __name__ == '__main__':
    unittest.main()
