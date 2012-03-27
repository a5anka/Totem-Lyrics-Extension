import unittest
from test.test_chart_lyrics_model import TestChartLyricsModel
from test.test_tag_identifier import TestTagIdentifier
from test.test_lyrdb_model import TestLyrdbModel

# Loading ChartLyricsModel test cases
testSuit = unittest.TestLoader().loadTestsFromTestCase(TestChartLyricsModel)

# Loading TagIdentifier test cases
testSuit.addTest(
    unittest.TestLoader().loadTestsFromTestCase(TestLyrdbModel))
                 
# Loading TagIdentifier test cases
testSuit.addTest(unittest.TestLoader().loadTestsFromTestCase(TestTagIdentifier))

unittest.TextTestRunner().run(testSuit)
