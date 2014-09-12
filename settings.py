from gi.repository import Gtk, GLib, GObject, Gio

class MdSettings(GObject.Object):
    
    def __init__(self):
        GObject.Object.__init__(self)
        
        self.ui = Gtk.Builder()
        self.ui.add_from_file('/home/georges/.local/share/gedit/plugins/gedit-markdown/settings.ui')
        
        # Dialog
        self.dialog = self.ui.get_object('settings_dialog')
        self.dialog.set_modal(True)
        
        # Buttons
        self.save_button = self.ui.get_object('save_button')
        self.cancel_button = self.ui.get_object('cancel_button')
        
        # Signals
        self.connect_signals()
        
    def connect_signals(self):
        self.save_button.connect("clicked", self.on_dialog_button_clicked)
        self.cancel_button.connect("clicked", self.on_dialog_button_clicked)
    
    def show_settings_window(self, parent):
        self.dialog.set_transient_for(parent)
        self.dialog.run()
    
    def on_dialog_button_clicked(self, button):
        if button is self.save_button:
            print("Save button")
        self.dialog.hide();
