# _*_ coding: utf-8 _*_

from gi.repository import GObject, Peas, GdkPixbuf, Gtk, Notify # pylint: disable-msg=E0611
from gi.repository import Totem, Gio # pylint: disable-msg=E0611
        
class LyricsSidebar(object):
    
    def __init__(self, totem):
        self._totem = totem
        builder = Totem.plugin_load_interface ("lyrics-downloader",   #
                                               "sidebar.ui", 
                                               True,
                                               self._totem.get_main_window (),
                                               self)
        
        self._container = builder.get_object ('lyrics_vbox')

        self._lyrics_buffer = builder.get_object('lyrics_text_buffer')

        self._totem.add_sidebar_page ("lyrics-view", ("Lyrics view"), 
                                      self._container)
        self._container.show_all()

        
    def set_lyrics(self, lyrics):
        """
        
        Arguments:
        - `lyrics`:
        """
        start, end = self._lyrics_buffer.get_bounds() 
        self._lyrics_buffer.delete(start, end)
        begining = self._lyrics_buffer.get_start_iter()
        self._lyrics_buffer.insert(begining, lyrics)
        

    def destroy(self):
        self._totem.remove_sidebar_page("lyrics-view")
