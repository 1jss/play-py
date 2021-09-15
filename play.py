#!/usr/bin/python3

import os
import gi
gi.require_version('Gtk', '3.0')

from gi.repository import Gtk
from gi.repository.GdkPixbuf import Pixbuf

COL_NAME = 0
COL_PIXBUF = 1
COL_EXEC = 2
SELECTION_SINGLE = 1

class Play():
    def delete_event(self, widget, event, data=None):
        return False

    def destroy(self, widget, data=None):
        Gtk.main_quit()

    def __init__(self):
        self.window = Gtk.Window()
        self.window.set_icon_from_file('/usr/share/icons/hicolor/64x64/apps/play.svg')

        self.window.connect("delete_event", self.delete_event)
        self.window.connect("destroy", self.destroy)
        self.window.set_default_size(810, 600)
        self.window.set_title("Play")

        self.current_directory = os.path.realpath("/usr/share/applications/") # get applications directory
        self.container = Gtk.VBox(homogeneous=False, spacing=0)
        self.window.add(self.container)

        self.toolbar = Gtk.Toolbar()
        self.container.pack_start(self.toolbar, False, False, 0)

        self.current_filter = ""
        self.searchBar = Gtk.SearchEntry()
        self.searchBarToolItem = Gtk.ToolItem.new()
        self.searchBarToolItem.set_expand(True)
        self.searchBarToolItem.add(self.searchBar)
        self.toolbar.insert(self.searchBarToolItem, -1)
        self.searchBar.connect("search-changed", self.load_filter)
        self.searchBar.grab_focus()

        self.view = Gtk.ScrolledWindow()
        self.container.pack_start(self.view, True, True, 0)
        
        self.genericAppIcon = "gtk-file"
        self.store = Gtk.ListStore(str, Pixbuf, str)
        self.fill_store()
        self.iconView = Gtk.IconView.new()
        self.iconView.set_selection_mode(Gtk.SelectionMode(SELECTION_SINGLE))
        self.iconView.set_margin(16)
        self.iconView.set_item_width(64)
        self.iconView.set_activate_on_single_click(True)
        self.iconView.set_model(self.store)
        self.iconView.set_text_column(COL_NAME)
        self.iconView.set_pixbuf_column(COL_PIXBUF)
        self.iconView.connect("item-activated", self.on_item_activated)

        self.view.add(self.iconView)
        self.window.show_all()
        
    def get_icon(self, name):
        theme = Gtk.IconTheme.get_default()
        return theme.load_icon(name, 64, 0)

    def fill_store(self):
        self.store.clear()

        self.theme = Gtk.IconTheme.get_default() # get default theme
        for fl in sorted(os.listdir(self.current_directory),key=str.lower):
            if fl.find(".desktop") != -1:
                self.hideItem = False
                self.appName = ""
                self.appIcon = ""
                self.appIconName = "" # path to app icon or icon name
                self.appExecPath = ""

                self.path = os.path.join(self.current_directory, fl) # current file
                with open(self.path) as f:
                    for line in f:
                        if line.find('NoDisplay=true') != -1:
                            self.hideItem = True
                            break # Quit looping the file
                        elif line.find('Terminal=true') != -1:
                            self.hideItem = True
                            break # Quit looping the file
                        elif line.find('Shortcut Group') != -1:
                            break # Quit looping the file
                        elif line.find('Name=') != -1 and line.find('Generic') == -1:
                            self.appName = line.split('=')[1].rstrip()
                        elif line.find('Icon=') != -1:
                            self.appIconName = line.split('=')[1].rstrip()
                        elif line.find('Exec=') != -1 and line.find('Try') == -1:
                            self.appExecPath = line.split('=')[1].split(' ')[0].rstrip()
                if fl.find(self.current_filter) == -1 and self.appName.lower().find(self.current_filter) == -1: # Apply search in nice app name and executable name
                    self.hideItem = True
                if self.theme.has_icon(self.appIconName): # check if theme has current icon
                    self.appIcon = self.get_icon(self.appIconName) # set icon
                elif os.path.exists(self.appIconName):
                    self.appIcon = Pixbuf.new_from_file(self.appIconName)
                else:
                    self.appIcon = self.get_icon(self.genericAppIcon) # set generic icon
                if not self.hideItem:
                    self.store.append([self.appName, self.appIcon, self.appExecPath]) # fill store

    # Take text in searchBar and load it as current directory
    def load_filter(self, widget):
        self.current_filter = self.searchBar.get_text()
        self.fill_store()

    # When activating (left-click, enter or space) on an icon
    def on_item_activated(self, widget, item):
        import subprocess
        model = widget.get_model()
        execPath = model[item][COL_EXEC]
        subprocess.Popen(execPath, shell=False)
        self.destroy(widget)

    def main(self):
        Gtk.main()

if __name__ == "__main__":
    play = Play()
    play.main()
