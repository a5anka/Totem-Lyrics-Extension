# _*_ coding: utf-8 _*_

from gi.repository import GObject, Gtk # pylint: disable-msg=E0611
from gi.repository import Totem # pylint: disable-msg=E0611

from tag_identifier import identify_mp3
from chart_lyrics_model import ChartLyricsModel
from lyrdb_model import LyrdbModel
from search_thread import SearchThread
from download_thread import DownloadThread

class DialogBox (object):

    def __init__ (self, totem, sidebar):

        self._totem = totem # Reference to the player
        self._dialog = None
        
        self._close_button = None
        self._apply_button = None

        self._model = None
        self._sidebar = sidebar
        
        # Init the model
        self._model = ChartLyricsModel ()

    def destroy (self):
        """
        Include the dialog destroying actions

        """
        self._dialog.destroy()

    def _close_dialog(self, ):
        """
        Dialog box is hidden instead of destroying it
        """
        self._dialog.hide()
        
    def _build_dialog(self):
        """
        Builds the main gui of the lyrics plugin
        Uses the lyrics-downloader.ui file to build the GUI
        
        """
        builder = Totem.plugin_load_interface ("lyrics-downloader",
                                               "lyrics-downloader.ui", True,
                                               self._totem.get_main_window (),
                                               self)
        self._dialog = builder.get_object ('lyrics_dialog')
        self._close_button = builder.get_object ('close_button')
        self._apply_button = builder.get_object ('apply_button')
        self._find_button = builder.get_object ('find_button')
        self._tree_view = builder.get_object ('lyrics_treeview')
        self._list_store = builder.get_object ('lyrics_model')
        self._progress = builder.get_object ('progress_bar')
        combobox = builder.get_object('server_combobox')
        servers = builder.get_object('server_model')

        self._apply_button.set_sensitive (False)

        # Setup the combobox
        renderer = Gtk.CellRendererText ()
        sorted_servers = Gtk.TreeModelSort (model = servers)
        sorted_servers.set_sort_column_id (0, Gtk.SortType.ASCENDING)
        combobox.set_model (sorted_servers)
        combobox.pack_start (renderer, True)
        combobox.add_attribute (renderer, 'text', 0)

        itera = servers.append(["Chart Lyrics","1"])
        servers.append(["Lyrdb","2"])
        success, parentit = sorted_servers.convert_child_iter_to_iter(itera)
        combobox.set_active_iter(parentit)
        
        
        # Set up the results treeview
        renderer = Gtk.CellRendererText ()
        self._tree_view.set_model (self._list_store)
        # This is the title of the song
        column = Gtk.TreeViewColumn ("Song", renderer, text=0)
        column.set_resizable (True)
        column.set_expand (True)
        self._tree_view.append_column (column)
        # This is the Artist of the song
        column = Gtk.TreeViewColumn ("Artist", renderer, text=1)
        column.set_resizable (True)
        self._tree_view.append_column (column)

        
        # Set up signals
        combobox.connect ('changed', self.__on_combobox__changed)
        self._close_button.connect ('clicked', self.__on_close_clicked)
        
        self._dialog.connect ('delete-event', self._dialog.hide_on_delete)
        self._dialog.set_transient_for (self._totem.get_main_window ())
        self._apply_button.connect ('clicked', self.__on_apply_clicked)
        self._find_button.connect ('clicked', self.__on_find_clicked)
        self._tree_view.connect ('row-activated', 
                                 self.__on_treeview__row_activate)

        # connect callbacks
        self._tree_view.get_selection ().connect ('changed',
                                            self.__on_treeview__row_change)
        
    def show_dialog (self, _action):
        if not self._dialog:
            self._build_dialog()

        self._progress.set_text("")
        self._dialog.show_all()

    def _initiate_find(self):
        """
        Initiate the search

        """
        self._apply_button.set_sensitive (False)
        artist, title = identify_mp3(self._totem.get_current_mrl ())

        if artist == None or title == None:
            self._progress.set_text("Could not identify the song file :(")
        else:
            self._get_results(artist, title)


    def _get_file_path(self, filename):
        """
        This method returns the a absolute path for the file.
        This should be used by plugin to find plugin-specific resource files.
    
        Arguments:
        - `filename`: filename of the resource file
        """
        return Totem.plugin_find_file("lyrics-downloader",filename)

    def _get_results (self, artist, title):
        """
        This method retrieve data from online server
        and update the treeview
    
        Arguments:
        - `artist`:
        - `title`:
        """
        self._list_store.clear()

        search_thread = SearchThread (self._model, artist, title)
        search_thread.start()
        GObject.idle_add(self._populate_treeview, search_thread)

        self._progress.set_text('Searching Lyrics...')
        GObject.timeout_add(350, self._progress_bar_update, search_thread)

    def _populate_treeview(self, search_thread):
        """
        This method will populate the result tree 
        using the data retrieved by search thread
    
        Arguments:
        - `search_thread`:
        """
        if not search_thread.done:
            return True

        results = search_thread.get_results ()
        if results:
            for sub_data in results:
                if 'LyricChecksum' in sub_data:
                    self._list_store.append ([sub_data['Song'],
                                              sub_data['Artist'],
                                              sub_data['LyricId'],
                                              sub_data['LyricChecksum']])
        return False

    def _download_and_apply(self ):
        """
        Download the selected lyrics file and apply it to sidebar
        """
        self._apply_button.set_sensitive (False)
        self._tree_view.set_sensitive (False)
        
        model, rows = self._tree_view.get_selection ().get_selected_rows ()
        if rows:
            lyric_iter = model.get_iter (rows[0])
            lyric_id = model.get_value (lyric_iter, 2)
            lyric_checksum = model.get_value (lyric_iter, 3)

            download_thread = DownloadThread(self._model, 
                                             lyric_id, 
                                             lyric_checksum)
            download_thread.start()
            GObject.idle_add (self._apply_lyrics, download_thread)

            self._progress.set_text ('Downloading the lyrics...')
            GObject.timeout_add (350, 
                                 self._progress_bar_update, 
                                 download_thread)

    def _apply_lyrics(self, download_thread):
        """
        This method apply the downloaded lyrics to the player
    
        Arguments:
        - `download_thread`:
        """
        if not download_thread.done:
            return True

        lyrics = download_thread.get_lyrics ()

        if lyrics:
            self._show_lyrics(lyrics)
            self._close_dialog ()
        else:
            self._apply_button.set_sensitive(True)
        return False        

    def _progress_bar_update(self, thread):
        """
        This periodically update the progress bar
        """
        if not thread.done:
            self._progress_pulse ()
            return True

        message = thread.get_message ()
        self._progress.set_text (message)

        self._progress.set_fraction (0.0)

        self._tree_view.set_sensitive (True)
        return False

    def _show_lyrics(self, lyrics):
        """
    
        Arguments:
        - `lyrics`:
        """
        self._sidebar.set_lyrics(lyrics)

    def __on_close_clicked(self, _data):
        """
        Clicke event of close button in the dialog box
    
        Arguments:
        - `_data`: 
        """
        self._close_dialog()

    def __on_apply_clicked(self, _data):
        """
        Click event of apply button in the dialog button
    
        Arguments:
        - `_data`:
        """
        self._download_and_apply ()
        
    def __on_treeview__row_change (self, selection):
        if selection.count_selected_rows () == 1:
            self._apply_button.set_sensitive (True)
        else:
            self._apply_button.set_sensitive (False)

    def __on_treeview__row_activate(self, tree_path, column, data):
        """
        
        Arguments:
        - `tree_path`:
        - `column`:
        - `data`:
        """
        self._download_and_apply ()

    def __on_combobox__changed (self, combobox):
        self._list_store.clear()
        
        combo_iter = combobox.get_active_iter ()
        combo_model = combobox.get_model ()
        option = combo_model.get_value (combo_iter, 1)
        if option == "1":
            self._model = ChartLyricsModel()
        elif option == "2":
            self._model = LyrdbModel()

    def __on_find_clicked (self, _data):
        self._initiate_find()
