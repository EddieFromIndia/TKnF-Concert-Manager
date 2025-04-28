import json
import tkinter as ttk

from libs.supabase_client import Supabase
from pages.home import HomePage
from pages.concerts import ConcertsPage
from pages.stats import StatsPage

class App(ttk.Tk):
    def __init__(self):
        super().__init__()

        with open('config.json') as config_file:
            config = json.load(config_file)

        SUPABASE_URL = config["supabase_url"]
        SUPABASE_KEY = config["supabase_key"]
        self.supabase = Supabase(SUPABASE_URL, SUPABASE_KEY)

        self.iconbitmap("assets/images/icon.ico")
        self.title("TKnF Show Manager")

        # Set the window size and position
        width = 1280
        height = 680
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        x = (screen_width - width) // 2
        y = (screen_height - height - 80) // 2

        self.geometry(f"{width}x{height}+{x}+{y}")
        
        # Create container frame for switching pages
        self.container = ttk.Frame(self)
        self.container.pack(fill="both", expand=True)
        
        # Create page instances
        self.pages = {
            "home": HomePage(self.container, self.supabase, self.show_page),
            "concerts": ConcertsPage(self.container, self.supabase, self.show_page),
            "stats": StatsPage(self.container, self.supabase, self.show_page),
        }

        # Display the home page initially
        self.show_page("home")

    def show_page(self, page_name, data=None):
        """Function to switch pages by hiding the current frame and showing the next one."""
        for page in self.pages.values():
            page.pack_forget()  # Hide all pages

        page = self.pages[page_name]
        if page_name == "home" and data:
            page.load_concert(data)
        elif page_name == "home" and not data:
            page.clear_form()
        elif page_name == "concerts":
            page.load_concerts()
        elif page_name == "stats":
            page.load_stats()

        page.pack(fill="both", expand=True)

def main():
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()