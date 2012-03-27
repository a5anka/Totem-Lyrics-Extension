import unittest
from gi.repository import Gio
from tag_identifier import identify_mp3

class TestTagIdentifier (unittest.TestCase):
    def setUp(self):
        test_song = Gio.File.new_for_path("data/apev2-lyricsv2.mp3")
        link_address = test_song.get_uri()
        self.artist, self.track = identify_mp3(link_address)

    def test_artist_search(self):
        self.assertEqual(self.artist, "Auth")

    def test_track_search(self):
        self.assertEqual(self.track, "A song   ")

        
if __name__ == '__main__':
    unittest.main()
