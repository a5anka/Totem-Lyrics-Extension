import urllib2
import threading
from xml.etree import ElementTree

SEARCH_URL = 'http://api.chartlyrics.com/apiv1.asmx/SearchLyric?artist=%s&song=%s'
DOWNLOAD_URL =  'http://api.chartlyrics.com/apiv1.asmx/GetLyric?lyricId=%s&lyricCheckSum=%s'

class ChartLyricsModel(object):
    """
    This contains the access logic of chartlyrics service
    """
    
    def __init__(self):
        self._lock = threading.Lock()

    def search_lyrics(self, artist, track):
        """
        Search the chart lyrics database and return results
        
        """
        self._lock.acquire (True)
        lyric_result_key = '{http://api.chartlyrics.com/}SearchLyricResult'        
        message = ''
        try:
            request = urllib2.urlopen(self._get_search_url(artist, track))
            response = request.read()
        except:
            self._lock.release ()
            return (None, "Could not contact the server.")
        
        lyric = ElementTree.fromstring(response)
        search_results = lyric.findall(lyric_result_key)
        actual_results = search_results[:-1]

        result_array = []
        
        if len(actual_results) == 0:
            message = 'No results found'
        else:
            for each in actual_results:
                data = self._parse_result(each)
                result_array.append(data)

        self._lock.release ()
        
        return result_array, message

    def download_lyrics(self, lyrics_checksum, lyrics_id):
        """
        Download the selected lyrics from chart lyrics
        
        Arguments:
        - `lyrics_checksum`:
        - `lyrics_id`:
        """
        self._lock.acquire (True)
        
        if lyrics_id == '0' or lyrics_checksum == '0':
            self._lock.release ()
            return (None, "Wrong id or checksum")
        
        url = DOWNLOAD_URL % (lyrics_id,lyrics_checksum)
        try:
            req = urllib2.urlopen(url)
            result = req.read()
        except:
            self._lock.release ()
            return (None , "Could not contact the server.")
        
        lyric = ElementTree.fromstring(result)

        self._lock.release ()
        return (lyric[9].text, '')


    def _get_search_url(self, artist, track):
        """
        return a url to retrive results for corresponding artist and track
        
        Arguments:
        - `artist`:
        - `track`:
        """
        return SEARCH_URL % (urllib2.quote(artist), urllib2.quote(track))

    def _parse_result(self, result):
        """
        Extract information from a result
    
        Arguments:
        - `result`:
        """
        data = {}
        
        for each in result:
            data[each.tag[29:]] = each.text # remove the preamble

        return data
    
