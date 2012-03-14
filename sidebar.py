# _*_ coding: utf-8 _*_

from gi.repository import GObject, Peas, GdkPixbuf, Gtk, Notify # pylint: disable-msg=E0611
from gi.repository import Totem, Gio # pylint: disable-msg=E0611

from dialog_box import DialogBox

class LyricsSidebar(object):
    
    def __init__(self, totem):
        self._totem = totem

        self._dialog = DialogBox(self._totem, self)

        # Add sidebar GUI
        builder = Totem.plugin_load_interface ("lyrics-downloader",   #
                                               "sidebar.ui", 
                                               True,
                                               self._totem.get_main_window (),
                                               self)
        # GUI objects
        self._container = builder.get_object ('lyrics_vbox')
        self._lyrics_buffer = builder.get_object('lyrics_text_buffer')
        self._get_button = builder.get_object('get_button')

        # Add sidebar to totem
        self._totem.add_sidebar_page ("lyrics-view", ("Lyrics view"), 
                                      self._container)
        self._container.show_all()

        # Controlling supported files
        self._totem.connect ('file-opened', self.__on_totem__file_opened)
        self._totem.connect ('file-closed', self.__on_totem__file_closed)

        # Setup signals
        self._get_button.set_sensitive(self._totem.is_playing () and
                                    self._check_is_mp3())
        self._get_button.connect('clicked', self._dialog.show_dialog)

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
        if self._dialog:
            self._dialog.destroy()
        self._totem.remove_sidebar_page("lyrics-view")

    def _check_is_mp3 (self):
        """
        This check if the file playing is mp3

        """
        filename = self._totem.get_current_mrl ()
        if Gio.content_type_guess (filename, '')[0] == 'audio/mpeg':
            return True
        return False

    def __on_totem__file_opened(self, _totem, new_mrl):
        """
        This method will be called when a file is opened
        
        Arguments:
        - `_totem`: A TotemObject
        - `new_mrl`: the MRL opened
        """
        if self._check_is_mp3 ():
            self._get_button.set_sensitive(True)
        else:
            self._get_button.set_sensitive(False)

    def __on_totem__file_closed(self, _totem):
        """
        This method is called when the file is closed
    
        Arguments:
        - `_totem`: A TotemObject
        """

        self._get_button.set_sensitive(False)
