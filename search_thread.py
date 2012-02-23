import threading
  
class SearchThread (threading.Thread):

  def __init__(self, model, artist, track):
    self._model = model
    self._artist = artist
    self._track = track

    self._done = False

    self._lock =  threading.Lock()
    self._results = None
    self._message = ''
    threading.Thread.__init__(self)
    
  def run (self):
    self._lock.acquire (True)
    (self._results,
     self._message) = self._model.search_lyrics (self._artist,
                                                    self._track)
    self._done = True
    self._lock.release ()

  def get_results (self):
    results = None
    
    self._lock.acquire (True)
    if self._done:
      results = self._results

    self._lock.release ()
      
    return results

  def get_message (self):
    message = _(u'Searching for subtitles…')
    
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
