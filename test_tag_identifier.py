import unittest
from tag_identifier import identify_mp3

class TestTagIdentifier (unittest.TestCase):

    def test_tag_search(self):
        link_address = "file:///home/asanka/Projects/lyrics-downloder/Thriller%20-%20Michael%20Jackson.mp3"
        artist, track = identify_mp3(link_address)
        self.assertEqual(artist, "Michael Jackson")
        self.assertEqual(track, "Thriller")

if __name__ == '__main__':
    unittest.main()
