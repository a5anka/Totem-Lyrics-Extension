import unittest
from model.chart_lyrics_model import ChartLyricsModel

class TestChartLyricsModel (unittest.TestCase):

    def setUp (self):
        self._model = ChartLyricsModel()
        
    def test_search_lyrics(self):
        result, message = self._model.search_lyrics("Michael Jackson", "bad")
        self.assertIsInstance(result,list)
        self.assertIsInstance(result[0],dict)
        self.assertEqual(result[0]['Artist'], "Michael Jackson")

    def test_download_lyrics(self):
        result,message = self._model.download_lyrics('1710',
                                             '2a3ea713422cbc97470b0c38c6e5a552')
        self.assertIsInstance(result, str)

if __name__ == '__main__':
    unittest.main()
