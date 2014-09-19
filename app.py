from gi.repository import GObject, Gio, Gedit

class MdAppActivatable(GObject.Object, Gedit.AppActivatable):
    
    app = GObject.property(type=Gedit.App)
    
    def __init__(self):
        GObject.Object.__init__(self)
    
    def do_activate(self):
        self.app.add_accelerator("<Primary><Shift>M", "win.markdown_preview", None)
        self.app.add_accelerator("<Primary><Alt>M", "win.markdown_settings", None)
        
        self.menu_extension = self.extend_menu("tools-section")
        item = Gio.MenuItem.new(_("Markdown"), None)
        
        menu = Gio.Menu.new()
        sub1 = Gio.MenuItem.new(_("Preview File"), "win.markdown_preview")
        sub2 = Gio.MenuItem.new(_("Settings"), "win.markdown_settings")
        
        menu.append_item(sub1)
        menu.append_item(sub2)
        
        item.set_submenu(menu)
        
        self.menu_extension.append_menu_item(item)
    
    def do_deactivate(self):
        self.app.remove_accelerator("win.markdown_preview", None)
        self.menu_extension = None
    

