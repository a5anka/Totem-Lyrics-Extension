# _*_ coding: utf-8 _*_

from gi.repository import GObject, Peas, GdkPixbuf, Gtk, Notify # pylint: disable-msg=E0611
from gi.repository import Totem, Gio # pylint: disable-msg=E0611

from  tag_identifier import identify_mp3

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
        self._info_label = None
        
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

    def do_deactivate (self):
        """
        Include the Plugin destroying Actions

        """
        if self._dialog:
            self._dialog.destroy()
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
        self._info_label = builder.get_object ('info_label')
        self._tree_view = builder.get_object ('lyrics_treeview')
        self._list_store = builder.get_object ('lyrics_model')

        self._apply_button.set_sensitive (False)

        # Set up the results treeview
        renderer = Gtk.CellRendererText ()
        self._tree_view.set_model (self._list_store)
        column = Gtk.TreeViewColumn ("Song", renderer, text=0)
        column.set_resizable (True)
        column.set_expand (True)
        self._tree_view.append_column (column)
        column = Gtk.TreeViewColumn ("Artist", renderer, text=1)
        self._tree_view.append_column (column)


        #Some sample data
        self._list_store.clear()
        self._list_store.append(['Thriller','MJ'])
        self._list_store.append(['Beat it','MJ'])
        self._list_store.append(['Billie Jean','MJ'])
        self._list_store.append(['The Lazy song','Bruno Mars'])
        
        # Set up signals
        self._close_button.connect ('clicked', self.__on_close_clicked)
        
        self._dialog.connect ('delete-event', self._dialog.hide_on_delete)
        self._dialog.set_transient_for (self._totem.get_main_window ())
        
    def _show_dialog (self, _action):
        if not self._dialog:
            self._build_dialog()

        self._info_label.set_text('Results for ' + self._get_song_info())

        self._dialog.show_all()
        
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

    def _get_song_info(self):
        """
        Return a string about the current played mp3

        """
        artist, title = identify_mp3(self._totem.get_current_mrl ())

        if artist == None or title == None:
            return "Could not identify the song file :("
        
        return title + ' by ' + artist
        

    def _get_file_path(self, filename):
        """
        This method returns the a absolute path for the file.
        This should be used by plugin to find plugin-specific resource files.
    
        Arguments:
        - `filename`: filename of the resource file
        """
        return Totem.plugin_find_file("lyrics-downloader",filename)

    def __on_close_clicked(self, _data):
        """
        Clicke event of close button in the dialog box
    
        Arguments:
        - `_data`: 
        """
        self._close_dialog()
        
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
