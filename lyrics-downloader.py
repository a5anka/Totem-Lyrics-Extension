# _*_ coding: utf-8 _*_

from gi.repository import GObject, Peas, GdkPixbuf, Gtk, Notify # pylint: disable-msg=E0611

class LyricsPlugin (GObject.Object, Peas.Activatable):
    __gtype_name__ = 'LyricsPlugin'

    object = GObject.property (type = GObject.Object)

    def __init__ (self):
        GObject.Object.__init__ (self)

        self._totem = None

        self._manager = None
        self._menu_id = None
        self._action_group = None
        self._action = None

    # totem.Plugin methods

    def do_activate (self):
        """
        Called when the plugin is activated.
        Here the sidebar page is initialized (set up the treeview, connect
        the callbacks, ...) and added to totem.
        """
        self._totem = self.object

        self._manager = self._totem.get_ui_manager ()
        self._append_menu()

    def do_deactivate (self):
        # Include the Plugin destroying Actions
        self._totem = None

        self._delete_menu()

    def _append_menu (self):
        self._action_group = Gtk.ActionGroup (name='LyricsPlugin')

        tooltip_text = "Search lyrics for the current song"
        self._action = Gtk.Action (name='lyricsplugin',
                                   label='Download Lyrics',
                                   tooltip=tooltip_text,
                                   stock_id=None)

        self._action_group.add_action (self._action)

        self._manager.insert_action_group (self._action_group, 0)

        self._menu_id = self._manager.new_merge_id ()
        print (self._menu_id)
        merge_path = '/tmw-menubar/view'
        self._manager.add_ui (self._menu_id,
                              merge_path,
                              'lyricsplugin',
                              'lyricsplugin',
                              Gtk.UIManagerItemType.MENUITEM,
                              False)
        self._action.set_visible (True)
        
        self._manager.ensure_update ()

        self._action.connect ('activate', self._show_dialog)
        """
        
        self._action.set_sensitive (self._totem.is_playing () and
        self._check_allowed_scheme () and
        not self._check_is_audio ())
        """

    def _delete_menu (self):
        self._manager.remove_action_group (self._action_group)
        self._manager.remove_ui (self._menu_id)
        
    def _show_dialog (self, _action):
        self._show_notification("Download Lyrics Clicked",
                                "Method still not implemented")

    def _show_notification (self,title,description):
        Notify.init("Totem Lyrics Plugin")
        
        n = Notify.Notification(summary=title,	body=description)
        plugin_path = ".local/share/totem/plugins/lyrics-downloader/"
        icon = GdkPixbuf.Pixbuf.new_from_file(plugin_path + "icon.png")
        n.set_icon_from_pixbuf(icon)
        
        n.set_timeout(1000)
        
        n.show()
