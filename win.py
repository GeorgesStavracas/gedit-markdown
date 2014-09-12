import markdown
from gi.repository import GLib, GObject, Gio, Gtk, Gedit, WebKit
from .settings import MdSettings

class MdWinActivatable(GObject.Object, Gedit.WindowActivatable):
    
    window = GObject.property(type=Gedit.Window)
    
    def do_activate(self):
        # Window signals
        self.window.connect("active-tab-changed", self.on_active_tab_changed)
        
        # Bottom panel WebView
        self.webview = WebKit.WebView.new()
        
        viewport = Gtk.Viewport.new()
        viewport.add(self.webview)
        
        self.scroll = Gtk.ScrolledWindow.new()
        self.scroll.add(viewport)
        self.scroll.show_all()
        
        self.window.get_bottom_panel().add_titled(self.scroll, "markdown_preview", _("Markdown"))
        
        # Settings
        self.settings = MdSettings()
        
        # Actions
        self.preview_action = Gio.SimpleAction.new("markdown_preview", None)
        self.preview_action.connect("activate", self.do_markdown)
        
        self.settings_action = Gio.SimpleAction.new("markdown_settings", None)
        self.settings_action.connect("activate", self.do_show_settings)
        
        self.window.add_action(self.preview_action)
        self.window.add_action(self.settings_action)
    
    def do_deactivate(self):
        self.window.remove_action("markdown_preview")
        self.window.remove_action("markdown_settings")
    
    def do_update_state(self):
        pass
        
    def do_markdown(self, unused_a, unused_b):
        text = self.window.get_active_document().get_property("text")
        html = markdown.markdown(text)
        
        self.webview.load_html_string(html, "")
        
        self.window.get_bottom_panel().show()
        self.window.get_bottom_panel().set_visible_child(self.scroll)
    
    def on_active_tab_changed(self, unused_window, tab):
        filename = tab.get_document().get_short_name_for_display()
        is_md = self.is_markdown_file(filename)
        self.preview_action.set_enabled(is_md)
    
    def is_markdown_file(self, filename):
      return filename.endswith(".md")
      
    def do_show_settings(self, unused_a, unused_b):
        self.settings.show_settings_window(self.window)
