# -*- coding: utf-8 -*-

from gi.repository import GObject, Peas # pylint: disable-msg=E0611

class LyricsPlugin (GObject.Object, Peas.Activatable):
	__gtype_name__ = 'LyricsPlugin'

	object = GObject.property (type = GObject.Object)

	def __init__ (self):
		GObject.Object.__init__ (self)

		self._totem = None

	# totem.Plugin methods

	def do_activate (self):
		"""
		Called when the plugin is activated.
		Here the sidebar page is initialized (set up the treeview, connect
		the callbacks, ...) and added to totem.
		"""
		self._totem = self.object

	def do_deactivate (self):
		# Include the plugin destroying Actions
		self._totem = None
