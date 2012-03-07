# _*_ coding: utf-8 _*_

from gi.repository import GObject, Peas, GdkPixbuf, Gtk, Notify # pylint: disable-msg=E0611
from gi.repository import Totem, Gio # pylint: disable-msg=E0611

from tag_identifier import identify_mp3
from chart_lyrics_model import ChartLyricsModel
from search_thread import SearchThread
from download_thread import DownloadThread
from sidebar import LyricsSidebar

class LyricsPlugin (GObject.Object, Peas.Activatable):
    __gtype_name__ = 'LyricsPlugin'

    object = GObject.property (type = GObject.Object)

    def __init__ (self):
        GObject.Object.__init__ (self)

        self._dialog = None # Reference to the dialog box
        self._totem = None # Reference to the player
        
        self._manager = None # UI manager of the player
        self._menu_id = None
        self._action_group = None
        self._action = None

        self._close_button = None
        self._apply_button = None
        self._refresh_button = None
        self._info_label = None

        self._model = None

        self._sidebar = None
        
    # totem.Plugin methods

    def do_activate (self):
        """
        Called when the plugin is activated.
        Here the sidebar page is initialized (set up the treeview, connect
        the callbacks, ...) and added to totem.
        """
        self._totem = self.object

        self._manager = self._totem.get_ui_manager ()
        self._append_menu() # Adds a menu item to the view menu

        self._totem.connect ('file-opened', self.__on_totem__file_opened)
        self._totem.connect ('file-closed', self.__on_totem__file_closed)

        # Init the model
        self._model = ChartLyricsModel ()

    def do_deactivate (self):
        """
        Include the Plugin destroying Actions

        """
        if self._dialog:
            self._dialog.destroy()

        if self._sidebar:
            self._sidebar.destroy()
        self._totem = None

        self._delete_menu() # get rid of the created menu item

    def _append_menu (self):
        """
        Adds a menu item to the view menu

        """
        self._action_group = Gtk.ActionGroup (name='LyricsPlugin')

        tooltip_text = "Search lyrics for the current song"
        self._action = Gtk.Action (name='lyricsplugin',
                                   label='Get Lyrics',
                                   tooltip=tooltip_text,
                                   stock_id=None)

        self._action_group.add_action (self._action)

        self._manager.insert_action_group (self._action_group, 0)

        self._menu_id = self._manager.new_merge_id ()

        merge_path = '/tmw-menubar/view' # location where the menu item inserted
        self._manager.add_ui (self._menu_id,       # merge id 
                              merge_path,          # merg path
                              'lyricsplugin',      # name of the ui
                              'lyricsplugin',      # name of the action
                              Gtk.UIManagerItemType.MENUITEM,
                              False)  # Top
        self._action.set_visible (True)
        
        self._manager.ensure_update ()

        self._action.connect ('activate', self._show_dialog)

        self._action.set_sensitive (self._totem.is_playing () and
                                    self._check_is_mp3())

    def _check_is_mp3 (self):
        """
        This check if the file playing is mp3

        """
        filename = self._totem.get_current_mrl ()
        if Gio.content_type_guess (filename, '')[0] == 'audio/mpeg':
            return True
        return False

    def _close_dialog(self, ):
        """
        Dialog box is hidden instead of destroying it
        """
        self._dialog.hide()
        

    def _delete_menu (self):
        self._manager.remove_action_group (self._action_group)
        self._manager.remove_ui (self._menu_id)

    def _build_dialog(self, ):
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
        self._refresh_button = builder.get_object ('refresh_button')
        self._info_label = builder.get_object ('info_label')
        self._tree_view = builder.get_object ('lyrics_treeview')
        self._list_store = builder.get_object ('lyrics_model')
        self._progress = builder.get_object ('progress_bar')

        self._apply_button.set_sensitive (False)

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
        self._close_button.connect ('clicked', self.__on_close_clicked)
        
        self._dialog.connect ('delete-event', self._dialog.hide_on_delete)
        self._dialog.set_transient_for (self._totem.get_main_window ())
        self._apply_button.connect ('clicked', self.__on_apply_clicked)
        self._refresh_button.connect('clicked', self.__on_refresh_clicked)

        # connect callbacks
        self._tree_view.get_selection ().connect ('changed',
                                            self.__on_treeview__row_change)
        
    def _show_dialog (self, _action):
        if not self._dialog:
            self._build_dialog()

        self._dialog.show_all()
        self._initiate_find()

        
    def _show_notification (self,title,description):
        """
        This method can be used to send notifications to desktop

        """
        Notify.init("Totem Lyrics Plugin")
        
        n = Notify.Notification(summary=title,	body=description)
        icon = GdkPixbuf.Pixbuf.new_from_file(self._get_file_path("icon.png"))
        n.set_icon_from_pixbuf(icon)
        
        n.set_timeout(1000)
        
        n.show()

    def _initiate_find(self):
        """
        Initiate the search

        """
        self._apply_button.set_sensitive (False)
        artist, title = identify_mp3(self._totem.get_current_mrl ())

        if artist == None or title == None:
            self._info_label.set_text("Could not identify the song file :(")
        else:
            song_info = title + ' by ' + artist
            self._info_label.set_text('Results for ' + song_info)
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
            self._show_sidebar(lyrics)
            self._close_dialog ()
        else:
            self._apply_button.set_sensitive(True)
        return False

    def _show_sidebar(self, lyrics):
        """
    
        Arguments:
        - `lyrics`:
        """
        if not self._sidebar:
            self._sidebar = LyricsSidebar(self._totem)

        self._sidebar.set_lyrics(lyrics)
        

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
        
    
    def __on_totem__file_opened(self, _totem, new_mrl):
        """
        This method will be called when a file is opened
        
        Arguments:
        - `_totem`: A TotemObject
        - `new_mrl`: the MRL opened
        """
        if self._check_is_mp3():
            self._action.set_sensitive(True)
        else:
            self._action.set_sensitive(False)

    def __on_totem__file_closed(self, _totem):
        """
        This method is called when the file is closed
    
        Arguments:
        - `_totem`: A TotemObject
        """

        self._action.set_sensitive(False)

    def __on_treeview__row_change (self, selection):
        if selection.count_selected_rows () == 1:
            self._apply_button.set_sensitive (True)
        else:
            self._apply_button.set_sensitive (False)

    def __on_refresh_clicked(self, _data):
        """
        Click event for refresh button
        """
        self._initiate_find()
        
        
