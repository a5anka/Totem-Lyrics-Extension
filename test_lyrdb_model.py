import unittest
from model.lyrdb_model import LyrdbModel

class TestChartLyricsModel (unittest.TestCase):

    def setUp (self):
        self._model = LyrdbModel()
        
    def test_search_lyrics(self):
        result, message = self._model.search_lyrics("Michael Jackson", "thriller")
        self.assertIsInstance(result,list)
        self.assertIsInstance(result[0],dict)
        self.assertEqual(result[0]['Artist'], "Michael Jackson")

    def test_ydownload_lyrics(self):
        result,message = self._model.download_lyrics('131071',
                                             '2a3ea713422cbc97470b0c38c6e5a552')
        self.assertIsInstance(result, str)

if __name__ == '__main__':
    unittest.main()
