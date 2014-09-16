from gi.repository import Gtk, GLib, GObject, Gio, WebKit2
import os

# Single instance
settings = None

# Auxiliary methods
def plugin_dir():
  user_data_dir = os.path.join(GLib.get_user_data_dir(), "gedit")
  user_plugin_dir = os.path.join(user_data_dir, "plugins")
  return os.path.join(user_plugin_dir, "gedit-markdown")

def css_dir():
  return os.path.join(plugin_dir(), "css")

def css_file(var):
  return os.path.join(css_dir(), var)

def data_file(var):
  return os.path.join(plugin_dir(), var)

def config_file():
  path = os.path.join(GLib.get_user_config_dir(), "gedit-markdown")
  return os.path.join(path, "settings.conf")

def html_file():
  path = os.path.join(plugin_dir(), "data")
  return os.path.join(path, "html")

def is_css(f):
  return f.endswith(".css")

def check_config_file():
  path = os.path.join(GLib.get_user_config_dir(), "gedit-markdown")
  
  if not os.path.exists(path):
    os.mkdir(path)
    
  if not os.path.exists(config_file()):
    # Create the config file when it doesn't exists
    file = open(config_file(), "w+")
    file.close()
    
    return False
  
  return True

def get_stylesheet_title(css):
    f = open(css, "r")
    first_line = f.readline()
    return first_line.replace("/*","").replace("*/","").strip()

# MdSettings
class MdSettings(GObject.Object):
    
    __gsignals__ = {
        "css-file-selected": (GObject.SIGNAL_RUN_FIRST, None, ()),
        "show-preview-window": (GObject.SIGNAL_RUN_FIRST, None, ())
    }
    
    def __init__(self):
        GObject.Object.__init__(self)
        
        # Builder
        self.ui = Gtk.Builder()
        self.ui.add_from_file(data_file("settings.ui"))
        
        # Dialog
        self.dialog = self.ui.get_object('settings_dialog')
        self.dialog.set_modal(True)
        
        self.listbox = self.ui.get_object('listbox')
        self.listbox.connect("row-activated", self.on_listbox_row_activated)
        
        # Preview window
        self.preview_window = self.ui.get_object('preview_window')
        self.webview = WebKit2.WebView()
        
        self.ui.get_object('preview_scroll').add(self.webview)
        self.webview.show()
        
        # CSS files
        self.css_files = [f for f in os.listdir(css_dir()) if is_css(os.path.join(css_dir(), f))]
        self.update_css_list()
        
        # Buttons
        self.save_button = self.ui.get_object('save_button')
        self.cancel_button = self.ui.get_object('cancel_button')
        
        # Switches
        self.auto_switch = self.ui.get_object('auto_switch')
        self.preview_switch = self.ui.get_object('attached_switch')
        
        # Signals
        self.connect_signals()
        
        # Settings file
        file_exists = check_config_file()
        
        self.key_file = GLib.KeyFile()
        self.key_file.load_from_file(config_file(), GLib.KeyFileFlags.NONE)
        
        # Update dialog preferences
        if file_exists:
            self.auto_switch.set_active(self.key_file.get_boolean("Config", "AutoPreview"))
            self.preview_switch.set_active(self.key_file.get_boolean("Config", "ShowPreviewWindow"))
        else:
            self.key_file.set_boolean("Config", "AutoPreview", False)
            self.key_file.set_boolean("Config", "ShowPreviewWindow", False)
            self.key_file.set_string("Config", "CSS", css_file("github.css"))
            self.key_file.save_to_file(config_file())
    
    def connect_signals(self):
        self.save_button.connect("clicked", self.on_dialog_button_clicked)
        self.cancel_button.connect("clicked", self.on_dialog_button_clicked)
        self.preview_switch.connect("notify::active", self.on_preview_switch_activate)
    
    def show_settings_window(self, parent):
        self.dialog.run()
    
    def show_preview_window(self):
        self.preview_window.show()
    
    def on_dialog_button_clicked(self, button):
        # Save config contents
        if button is self.save_button:
            self.key_file.set_boolean("Config", "AutoPreview", self.auto_switch.get_active())
            self.key_file.set_boolean("Config", "ShowPreviewWindow", self.preview_switch.get_active())
            self.key_file.save_to_file(config_file())
        
        self.dialog.hide();
    
    def update_css_list(self):
        
        for css_file in self.css_files:
            
            css_entry = CssListItem()
            css_entry.name.set_text(get_stylesheet_title(os.path.join(css_dir(), css_file)))
            css_entry.filename.set_text(css_file)
            
            css_entry.show()
            
            self.listbox.add(css_entry)
    
    def on_listbox_row_activated(self, unused_widget, row):
        self.key_file.set_string("Config", "CSS", css_file(row.filename.get_text()))
        self.emit("css-file-selected")
    
    # Get AutoPreview option
    def get_autopreview(self):
        return self.auto_switch.get_active()
    
    def get_show_preview_window(self):
        return self.preview_switch.get_active()
    
    def get_window_webview(self):
        return self.webview
    
    # Get base html content
    def get_html(self):
        f = open(html_file(), "r")
        html_content = f.read()
        f.close()
        
        return html_content
    
    def on_preview_switch_activate(self, unused_switch, unused_data):
        self.emit("show-preview-window")
    
    # Get selected CSS content
    def get_css(self):
        css_f = self.key_file.get_string("Config", "CSS")
        
        if css_f is None:
            return ""
        
        path = css_file(css_f)
        
        css = open(path, "r")
        css_content = css.read()
        css.close()
        
        return css_content
            

# CssList item entry    
class CssListItem(Gtk.ListBoxRow):
    
    def __init__(self):
        Gtk.ListBoxRow.__init__(self)
        
        self.ui = Gtk.Builder()
        self.ui.add_from_file(data_file("settings.ui"))
        
        self.add (self.ui.get_object('listbox_child'))
        self.name = self.ui.get_object('name_label')
        self.filename = self.ui.get_object('filename_label')
    
    
