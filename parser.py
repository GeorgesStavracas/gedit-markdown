from gi.repository import GLib, GObject, Gio, WebKit2, JavaScriptCore
import markdown

class MdParser(GObject.Object):
    
    get_y_scroll = "document.pageYOffset";
    
    def __init__(self):
        GObject.Object.__init__(self)
        self.webview = WebKit2.WebView()
    
    def parse(self, text="", css="", html="%d%s%s", margin=0, base_uri="file://"):
        parsed_md = markdown.markdown(text)
        
        page = html % (margin, css, parsed_md)
        
        # Async function
        #scroll = self.get_scroll()
        self.webview.load_html(page, base_uri)
        
    def get_scroll(self):
        self.webview.run_javascript(self.get_y_scroll, None, self.get_scroll_finished, None)
    
    def get_scroll_finished(self, unused_webview, parent_result, unused_data=None):
        result = self.webview.run_javascript_finish(parent_result)
        
        if result is None:
            return
        
        val = result.get_global_context()
