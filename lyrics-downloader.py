# _*_ coding: utf-8 _*_

from gi.repository import GObject, Peas, GdkPixbuf, Gtk, Notify # pylint: disable-msg=E0611

from sidebar import LyricsSidebar

class LyricsPlugin (GObject.Object, Peas.Activatable):
    __gtype_name__ = 'LyricsPlugin'

    object = GObject.property (type = GObject.Object)

    def __init__ (self):
        GObject.Object.__init__ (self)

        self._totem = None # Reference to the player
        
        self._sidebar = None
        
    # totem.Plugin methods

    def do_activate (self):
		"""
		Called when the plugin is activated.
        Here the sidebar page is initialized (set up the treeview, connect
        the callbacks, ...) and added to totem.

		"""
		self._totem = self.object
	 
		self._sidebar = LyricsSidebar (self._totem)

    def do_deactivate (self):
		"""
		Include the Plugin destroying Actions

		"""
		self._sidebar.destroy ()
		self._totem = None
