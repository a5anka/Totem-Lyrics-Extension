import urllib2
import threading

SEARCH_URL = 'http://www.lyrdb.com/lookup.php?q=%s|%s&for=match&agent=totem-plugin'
DOWNLOAD_URL =  'http://www.lyrdb.com/getlyr.php?q=%s'

class LyrdbModel(object):
    """
    This contains the access logic of lyrdb  webservice
    """
    
    def __init__(self):
        self._lock = threading.Lock()

    def search_lyrics(self, artist, track):
        """
        Search the chart lyrics database and return results
        
        """
        self._lock.acquire (True)
        message = ''
        try:
            url = SEARCH_URL % (urllib2.quote(artist), urllib2.quote(track))
            print url
            request = urllib2.urlopen(url)
            response = request.read()
        except:
            self._lock.release ()
            return (None, "Could not contact the server. Try again...")
        
        result_array = []


        if len(response) == 0:
            message = "No results found"
        else:
            results = response.split('\n')

            for each in results:
                data = {}
                fields = each.split('\\')
                data['LyricId'] = fields[0]
                data['Song'] = fields[1]
                data['Artist'] = fields[2]
                data['LyricChecksum'] = fields[0]

                result_array.append(data)
        
        self._lock.release ()
        
        return result_array, message

    def download_lyrics(self, lyrics_id, lyrics_checksum):
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
        
        url = DOWNLOAD_URL % (lyrics_id)
        try:
            req = urllib2.urlopen(url)
            result = req.read()
        except:
            self._lock.release ()
            return (None , "Could not contact the server. Try again...")
        
        lyric = result

        self._lock.release ()
        return (result, '')

