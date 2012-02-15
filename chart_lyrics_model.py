import urllib2
from xml.etree import ElementTree

SEARCH_URL = 'http://api.chartlyrics.com/apiv1.asmx/SearchLyric?artist=%s&song=%s'
DOWNLOAD_URL =  'http://api.chartlyrics.com/apiv1.asmx/GetLyric?lyricId=%s&lyricCheckSum=%s'

class ChartLyricsModel(object):
    """
    This contains the access logic of chartlyrics service
    """
    
    def __init__(self):
        pass

    def search_lyrics(self, artist, track):
        """
        Search the chart lyrics database and return results
        
        """
        try:
            request = urllib2.urlopen(self._get_search_url(artist, track))
            response = request.read()
        except:
            return None
        
        lyric = ElementTree.fromstring(response)
        lyric_result_key = '{http://api.chartlyrics.com/}SearchLyricResult'
        search_results = lyric.findall(lyric_result_key)

        actual_results = search_results[:-1]

        result_array = []
        
        for each in actual_results:
            data = self._parse_result(each)
            result_array.append(data)

        return result_array

    def download_lyrics(self, lyrics_checksum, lyrics_id):
        """
        Download the selected lyrics from chart lyrics
        
        Arguments:
        - `lyrics_checksum`:
        - `lyrics_id`:
        """
        if lyrics_id == '0' or lyrics_checksum == '0':
            return None
        
        url = DOWNLOAD_URL % (lyrics_id,lyrics_checksum)
        try:
            req = urllib2.urlopen(url)
            result = req.read()
        except:
            return None
        
        lyric = ElementTree.fromstring(result)
        
        return lyric[9].text


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
    
