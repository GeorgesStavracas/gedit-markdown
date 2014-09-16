import markdown
from gi.repository import GLib, GObject, Gio, Gtk, Gedit, WebKit2
from .settings import MdSettings, settings

class MdWinActivatable(GObject.Object, Gedit.WindowActivatable):
    
    window = GObject.property(type=Gedit.Window)
    
    def do_activate(self):
        # Window signal
        self.window.connect("active-tab-changed", self.on_active_tab_changed)
        
        # Bottom panel WebView
        self.webview = WebKit2.WebView()
        
        self.scroll = Gtk.ScrolledWindow()
        self.scroll.add(self.webview)
        
        self.scroll.show_all()
        self.window.get_bottom_panel().add_titled(self.scroll, "markdown_preview", _("Markdown"))
        
        # Settings
        global settings
        
        if settings is None:
            settings = MdSettings()

        self.settings = settings
        self.settings.connect("css-file-selected", self.on_css_selected)

        # Actions
        self.preview_action = Gio.SimpleAction.new("markdown_preview", None)
        self.preview_action.connect("activate", self.do_markdown)
        
        self.settings_action = Gio.SimpleAction.new("markdown_settings", None)
        self.settings_action.connect("activate", self.do_show_settings)
        
        self.window.add_action(self.preview_action)
        self.window.add_action(self.settings_action)
        
        # Document monitor
        self.current_is_md = False
        self.current_document = None
        
        if settings.get_show_preview_window() is True:
            self.current_webview = settings.get_window_webview()
        else:
            self.current_webview = self.webview
    
    def do_deactivate(self):
        self.window.remove_action("markdown_preview")
        self.window.remove_action("markdown_settings")
        self.window.get_bottom_panel().remove(self.scroll)
    
    def do_update_state(self):
        self.update_status()
    
    def on_active_tab_changed(self, unused_window, tab):
        self.update_status()
    
    # Parse the active-tab document text
    def do_markdown(self, unused_a=None, unused_b=None):
        bottom_panel = self.window.get_bottom_panel()
        
        self.parse_markdown()
        
        if bottom_panel.is_visible():
            bottom_panel.set_visible(False)
        else:
            bottom_panel.show()
            bottom_panel.set_visible_child(self.scroll)
    
    # Parse the current markdown file
    def parse_markdown(self, unused_a=None, unused_b=None):
        text = self.window.get_active_document().get_property("text")
        html = markdown.markdown(text)
        
        css = settings.get_css()
        html_base = settings.get_html() % (css, html)
        
        self.webview.load_html(html_base, None)
    
    # Enable/disable menu entries
    def update_status(self):
        # First, update the Gear menu entries
        active_doc = self.window.get_active_document()
        
        # Make sure there really is an active document opened
        if active_doc is None:
            self.preview_action.set_enabled(False)
            self.window.get_bottom_panel().set_visible(False)
            return
        
        filename = active_doc.get_short_name_for_display()
        self.current_is_md = self.is_markdown_file(filename)
        self.preview_action.set_enabled(self.current_is_md)
        
        if settings.get_autopreview():
            self.parse_markdown()
            self.window.get_bottom_panel().set_visible(self.current_is_md)
            
            if self.current_is_md:
                self.window.get_bottom_panel().set_visible_child(self.scroll)
        
        # Second, connect the signals
        if self.current_document is not None:
            
            if self.connection_id >= 0:
              self.current_document.disconnect(self.connection_id)
            
            self.connection_id = -1
        
        if self.current_is_md:
                self.current_document = active_doc
                self.connection_id = active_doc.connect ("changed", self.on_text_changed)
    
    # Check if it's a Markdown file
    def is_markdown_file(self, filename):
      return filename.endswith(".md")
      
    def do_show_settings(self, unused_a, unused_b):
        self.settings.show_settings_window(self.window)
    
    # Update Markdown view when editing an markdown file
    def on_text_changed(self, unused_widget):
        
        if self.current_is_md is False:
            self.window.get_bottom_panel().hide()
            return
        
        if self.settings.get_autopreview() is True:
            self.parse_markdown()
    
    # Change CSS automatically when it's selected        
    def on_css_selected(self, unused_widget):
        self.parse_markdown()
    
    def on_preview_switch_changed(self, switch):
        pass
