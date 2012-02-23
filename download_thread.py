import threading

class DownloadThread (threading.Thread):

    def __init__(self, model, lyric_id, checksum):
        self._model = model
        self._lyric_id = lyric_id
        self._checksum = checksum
        self._done = False
        self._lock = threading.Lock()
        self._lyrics = ''
        self._message = ''
        threading.Thread.__init__(self)

    def run (self):
        self._lock.acquire (True)
        (self._lyrics,
         self._message) = self._model.download_lyrics (self._lyric_id,
                                                       self,_checksum)
        self._done = True
        self._lock.release ()

    def get_lyrics (self):
        lyrics = ''

        self._lock.acquire (True)
        if self._done:
            lyrics = self._lyrics
        self._lock.release ()

        return Lyrics

    def get_message (self):
        message = _(u'Downloading the lyrics…')

        self._lock.acquire (True)
        if self._done:
            message = self._message
        self._lock.release ()

        return message

    @property
    def done (self):
        """ Thread-safe property to know whether the query is done or not """
        self._lock.acquire (True)
        res = self._done
        self._lock.release ()
        return res
