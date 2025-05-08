import tkinter as tk
import ttkbootstrap as ttk
from calendar import month_name

from libs.supabase_client import Supabase
from libs.utils import lighten_color

class StatsPage(ttk.Frame):
    def __init__(self, parent: ttk.Frame, supabase: Supabase, show_page_callback):
        super().__init__(parent)
        self.show_page_callback = show_page_callback
        self.supabase = supabase

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        ttk.Label(self, text="Tanmay Kar and Friends Concert Stats", font=("Arial Black", 24), anchor="center") \
            .grid(row=0, column=0, columnspan=2, sticky="ew", pady=10)
        
        self.style = ttk.Style()
        theme_bg = self.style.lookup("TFrame", "background")
        self.card_bg = lighten_color(theme_bg, amount=0.1)

        self.style.configure("Card.TFrame", background=self.card_bg, borderwidth=1, relief="solid")
        self.style.configure("Card.TLabel", background=self.card_bg)
        
        self.district_stats = ttk.Frame(self, style="Card.TFrame")
        self.district_stats.grid(row=1, rowspan=3, column=0, sticky="news", padx=(40, 20), pady=(10, 0))

        self.yearly_stats = ttk.Frame(self, style="Card.TFrame")
        self.yearly_stats.grid(row=1, column=1, sticky="news", padx=(20, 40), pady=(10, 0))

        self.monthly_stats = ttk.Frame(self, style="Card.TFrame")
        self.monthly_stats.grid(row=2, column=1, sticky="news", padx=(20, 40), pady=(30, 0))

        button_frame = ttk.Frame(self)
        button_frame.grid(row=3, column=1, sticky="news", padx=(20, 40), pady=(10, 0))

        back_btn = ttk.Button(button_frame, text="Back", command=lambda: self.show_page("home"))
        back_btn.pack(side="right", padx=5, pady=(50, 0), ipady=5)

        view_btn = ttk.Button(button_frame, text="View Concerts", width=16, command=lambda: self.show_page("concerts"))
        view_btn.pack(side="right", padx=15, pady=(50, 0), ipady=5)
    

    def load_stats(self):
        for stats in [self.district_stats, self.yearly_stats, self.monthly_stats]:
            for widget in stats.winfo_children():
                widget.destroy()
        
        year_stats, district_stats, month_stats = self.supabase.get_stats()

        # Create district stats
        ttk.Label(self.district_stats, text=f"District Stats", font=("Arial Black", 12), style="Card.TLabel", anchor="center") \
            .grid(row=0, column=0, columnspan=2, sticky="ew", padx=2, pady=(10, 0))
        
        for index, (district, count) in enumerate(list(district_stats.items())[:12]):
            if count == 0:
                ttk.Label(self.district_stats, text=f"{district}: {count}", font=("Arial", 12), style="Card.TLabel", anchor="center", foreground="#ff4d4d") \
                    .grid(row=index + 1, column=0, sticky="ew", padx=30, pady=(0, 20))
            else:
                ttk.Label(self.district_stats, text=f"{district}: {count}", font=("Arial", 12), style="Card.TLabel", anchor="center") \
                    .grid(row=index + 1, column=0, sticky="ew", padx=30, pady=(0, 20))
        
        for index, (district, count) in enumerate(list(district_stats.items())[12:], start=12):
            if count == 0:
                ttk.Label(self.district_stats, text=f"{district}: {count}", font=("Arial", 12), style="Card.TLabel", anchor="center", foreground="#ff4d4d") \
                    .grid(row=index - 11, column=1, sticky="ew", padx=30, pady=(0, 20))
            else:
                ttk.Label(self.district_stats, text=f"{district}: {count}", font=("Arial", 12), style="Card.TLabel", anchor="center") \
                    .grid(row=index - 11, column=1, sticky="ew", padx=30, pady=(0, 20))
        
        self.district_stats.grid_columnconfigure(0, weight=1)
        self.district_stats.grid_columnconfigure(1, weight=1)
        self.district_stats.grid_rowconfigure(0, weight=1)
        self.district_stats.grid_rowconfigure(1, weight=1)
        self.district_stats.grid_rowconfigure(2, weight=1)
        self.district_stats.grid_rowconfigure(3, weight=1)
        self.district_stats.grid_rowconfigure(4, weight=1)
        self.district_stats.grid_rowconfigure(5, weight=1)
        self.district_stats.grid_rowconfigure(6, weight=1)
        self.district_stats.grid_rowconfigure(7, weight=1)
        self.district_stats.grid_rowconfigure(8, weight=1)
        self.district_stats.grid_rowconfigure(9, weight=1)
        self.district_stats.grid_rowconfigure(10, weight=1)
        self.district_stats.grid_rowconfigure(11, weight=1)
        self.district_stats.grid_rowconfigure(12, weight=1)

        # Create yearly stats
        ttk.Label(self.yearly_stats, text=f"Yearly Stats", font=("Arial Black", 12), style="Card.TLabel", anchor="center") \
            .grid(row=0, column=0, columnspan=2, sticky="ew", padx=2, pady=10)
        
        ttk.Label(self.yearly_stats, text=f"Last Year: {year_stats['previous']}", font=("Arial", 12), style="Card.TLabel", anchor="center") \
            .grid(row=1, column=0, sticky="ew", padx=2, pady=(0, 20))
        
        ttk.Label(self.yearly_stats, text=f"This Year: {year_stats['current']}", font=("Arial", 12), style="Card.TLabel", anchor="center") \
            .grid(row=1, column=1, sticky="ew", padx=2, pady=(0, 20))
        
        self.yearly_stats.grid_columnconfigure(0, weight=1)
        self.yearly_stats.grid_columnconfigure(1, weight=1)
        self.yearly_stats.grid_rowconfigure(0, weight=1)
        self.yearly_stats.grid_rowconfigure(1, weight=1)
        
        # Create monthly stats
        ttk.Label(self.monthly_stats, text=f"Monthly Stats", font=("Arial Black", 12), style="Card.TLabel", anchor="center") \
            .grid(row=0, column=0, columnspan=2, sticky="ew", padx=2, pady=(10, 0))
            
        for month in range(1, 7):
            padding = (0, 20) if month == 6 else (0, 10)
            if month_stats.get(month, 0) == 0:
                ttk.Label(self.monthly_stats, text=f"{month_name[month]}: {month_stats.get(month, 0)}",
                          font=("Arial", 12), style="Card.TLabel", anchor="center", foreground="#ff4d4d") \
                          .grid(row=month, column=0, sticky="ew", padx=30, pady=padding)
            else:
                ttk.Label(self.monthly_stats, text=f"{month_name[month]}: {month_stats.get(month, 0)}",
                          font=("Arial", 12), style="Card.TLabel", anchor="center") \
                          .grid(row=month, column=0, sticky="ew", padx=30, pady=padding)
        
        for month in range(7, 13):
            padding = (0, 20) if month == 12 else (0, 0)
            if month_stats.get(month, 0) == 0:
                ttk.Label(self.monthly_stats, text=f"{month_name[month]}: {month_stats.get(month, 0)}",
                          font=("Arial", 12), style="Card.TLabel", anchor="center", foreground="#ff4d4d") \
                          .grid(row=month - 6, column=1, sticky="ew", padx=30, pady=padding)
            else:
                ttk.Label(self.monthly_stats, text=f"{month_name[month]}: {month_stats.get(month, 0)}",
                          font=("Arial", 12), style="Card.TLabel", anchor="center") \
                          .grid(row=month - 6, column=1, sticky="ew", padx=30, pady=padding)
        
        self.monthly_stats.grid_columnconfigure(0, weight=1)
        self.monthly_stats.grid_columnconfigure(1, weight=1)
        self.monthly_stats.grid_rowconfigure(0, weight=1)
        self.monthly_stats.grid_rowconfigure(1, weight=1)
        self.monthly_stats.grid_rowconfigure(2, weight=1)
        self.monthly_stats.grid_rowconfigure(3, weight=1)
        self.monthly_stats.grid_rowconfigure(4, weight=1)
        self.monthly_stats.grid_rowconfigure(5, weight=1)
        self.monthly_stats.grid_rowconfigure(6, weight=1)


    def show_page(self, page_name):
        self.show_page_callback(page_name)