from gi.repository import Gio
from mutagen.easyid3 import EasyID3

def identify_mp3(filename):
    """
    This metrhod extract the information about 
    the Artist and the songname.
    
    Arguments:
    - `filename`: file path to the mp3 file
    """

    song_file = Gio.File.new_for_uri (filename)
    file_path = song_file.get_path()

    song_tags = EasyID3(file_path)

    artist, title = None, None
    
    if 'artist' in song_tags:
        artist = song_tags['artist'][0]
    if 'title' in song_tags:
        title = song_tags['title'][0]
    
    return artist , title
    
