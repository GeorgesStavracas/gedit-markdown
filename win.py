from gi.repository import GLib, GObject, Gio, Gtk, Gedit, WebKit2
from .settings import MdSettings, settings
from .parser import MdParser
import markdown

class MdWinActivatable(GObject.Object, Gedit.WindowActivatable):
    
    window = GObject.property(type=Gedit.Window)
    
    ignored_states = {
        0,
        Gedit.WindowState.ERROR,
        Gedit.WindowState.PRINTING,
        Gedit.WindowState.SAVING
    }
    
    def do_activate(self):
        # Window signal
        self.window.connect("active-tab-changed", self.on_active_tab_changed)
        
        # Settings
        global settings
        
        if settings is None:
            settings = MdSettings()

        self.settings = settings
        self.settings.connect("css-file-selected", self.on_css_selected)
        self.settings.connect("margin-changed", self.on_margin_changed)
        #self.settings.connect("show-preview-window", self.on_show_preview_window)
        
        # Parser
        self.parser = MdParser()
        self.parser.webview.show()
        
        self.window.get_bottom_panel().add_titled(self.parser.webview, "markdown_preview", _("Markdown"))
        
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
        
    
    def do_deactivate(self):
        self.window.remove_action("markdown_preview")
        self.window.remove_action("markdown_settings")
        self.window.get_bottom_panel().remove(self.parser.webview)
    
    def do_update_state(self):
        # We don't want to show it every single time an event is fired
        if self.window.get_property("state") not in self.ignored_states:
            self.update_status()
    
    def on_active_tab_changed(self, unused_window, tab):
        self.update_status()
    
    # Parse the active-tab document text
    def do_markdown(self, unused_a=None, unused_b=None):
        self.parse_markdown()
        self.toggle_previewer()
        
    
    # Parse the current markdown file
    def parse_markdown(self, unused_a=None, unused_b=None):
        doc = self.window.get_active_document()
        
        if doc is None:
            return
        
        if not self.is_markdown_file(doc.get_short_name_for_display()):
            return
        
        margin = settings.margin.get_value_as_int()
        
        self.parser.parse(doc.get_property("text"), settings.get_css(), settings.get_html(), margin)
    
    # Enable/disable menu entries
    def update_status(self):
        # Update the Gear menu entries
        active_doc = self.window.get_active_document()
        
        # Make sure there really is an active document opened
        if active_doc is None:
            self.preview_action.set_enabled(False)
            self.toggle_previewer(False)
            return
        
        filename = active_doc.get_short_name_for_display()
        self.current_is_md = self.is_markdown_file(filename)
        self.preview_action.set_enabled(self.current_is_md)
        
        if settings.get_autopreview():
            self.parse_markdown()
            self.toggle_previewer(self.current_is_md)
            
            if self.current_is_md and not self.settings.get_show_preview_window():
                self.window.get_bottom_panel().set_visible_child(self.parser.webview)
        
        # Update connection
        self.update_document_connection()
        
    # Connect Gtk.TextBuffer::changed signal
    def update_document_connection(self):
        active_doc = self.window.get_active_document()
        
        if self.current_document is not None:
            
            if self.connection_id >= 0:
              self.current_document.disconnect(self.connection_id)
            
            self.connection_id = -1
        
        if self.current_is_md:
              self.current_document = active_doc
              self.connection_id = active_doc.connect ("changed", self.on_text_changed)
    
    # Toggle the preview window, or set a given visibility
    def toggle_previewer(self, show=None):
        widget = None
        
        if self.settings.get_show_preview_window():
            widget = self.settings.preview_window
        else:
            widget = self.window.get_bottom_panel()
        
        if show is None:
            widget.set_visible(not widget.get_visible())
        else:
            widget.set_visible(show)
        
    
    # Check if it's a Markdown file
    def is_markdown_file(self, filename):
      return filename.endswith(".md")
      
    def should_preview(self):
        active_doc = self.window.get_active_document()
        
        if active_doc is None:
            return False
        
        filename = active_doc.get_short_name_for_display()
        
        return self.is_markdown_file(filename)
        
    
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
    
    def on_margin_changed(self, unused_data):
        self.parse_markdown()
    
    def on_show_preview_window(self, unused_widget):
        # Remove from the current container
        self.parser.webview.get_parent().remove(self.parser.webview)
        
        if self.settings.get_show_preview_window():
            self.window.get_bottom_panel().set_visible(False)
            
            self.settings.preview_window_scroll.add(self.parser.webview)
            self.settings.preview_window.set_visible(self.should_preview())
            self.settings.preview_window.present()
            
        else:
            self.settings.preview_window.set_visible(False)
            self.window.get_bottom_panel().set_visible(self.should_preview())
        
        self.update_status()
        
