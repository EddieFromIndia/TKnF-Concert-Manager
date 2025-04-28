import tkinter as tk
from tkinter import ttk, messagebox, Frame

from libs.supabase_client import Supabase

class StatsPage(ttk.Frame):
    def __init__(self, parent: Frame, supabase: Supabase, show_page_callback):
        super().__init__(parent)
        self.show_page_callback = show_page_callback
        self.supabase = supabase

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        ttk.Label(self, text="Tanmay Kar and Friends Concert Stats", font=("Arial Black", 24)) \
            .grid(row=0, column=0, columnspan=2, sticky="ew", pady=10)
        
        self.district_stats = tk.Frame(self, background="white", highlightbackground="gray", highlightthickness=1)
        self.district_stats.grid(row=1, rowspan=3, column=0, sticky="news", padx=(20, 30), pady=(10, 0))

        self.yearly_stats = tk.Frame(self, background="white", highlightbackground="gray", highlightthickness=1)
        self.yearly_stats.grid(row=1, column=1, sticky="news", padx=(30, 20), pady=(10, 0))

        self.sound_stats = tk.Frame(self, background="white", highlightbackground="gray", highlightthickness=1)
        self.sound_stats.grid(row=2, column=1, sticky="news", padx=(30, 20), pady=(10, 0))

        self.monthly_stats = tk.Frame(self, background="white", highlightbackground="gray", highlightthickness=1)
        self.monthly_stats.grid(row=3, column=1, sticky="news", padx=(30, 20), pady=(10, 0))
    

    def load_stats(self):
        for stats in [self.district_stats, self.yearly_stats, self.sound_stats, self.monthly_stats]:
            for widget in stats.winfo_children():
                widget.destroy()
        
        year_stats, district_stats, month_stats = self.supabase.get_stats()

        # Create district stats
        ttk.Label(self.district_stats, text=f"District Stats", font=("Arial Black", 12), anchor="center", background="white") \
            .grid(row=0, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        
        for index, (district, count) in enumerate(list(district_stats.items())[:12]):
            ttk.Label(self.district_stats, text=f"{district}: {count}", font=("Arial", 12), anchor="center", background="white") \
                .grid(row=index + 1, column=0, sticky="ew", padx=30)
        
        for index, (district, count) in enumerate(list(district_stats.items())[12:], start=12):
            ttk.Label(self.district_stats, text=f"{district}: {count}", font=("Arial", 12), anchor="center", background="white") \
                .grid(row=index + 1, column=1, sticky="ew", padx=30)
        
        self.monthly_stats.grid_columnconfigure(0, weight=1)
        self.monthly_stats.grid_columnconfigure(1, weight=1)
        self.monthly_stats.grid_rowconfigure(0, weight=1)
        self.monthly_stats.grid_rowconfigure(1, weight=1)
        self.monthly_stats.grid_rowconfigure(2, weight=1)
        self.monthly_stats.grid_rowconfigure(3, weight=1)
        self.monthly_stats.grid_rowconfigure(4, weight=1)
        self.monthly_stats.grid_rowconfigure(5, weight=1)
        self.monthly_stats.grid_rowconfigure(6, weight=1)
        self.monthly_stats.grid_rowconfigure(7, weight=1)
        self.monthly_stats.grid_rowconfigure(8, weight=1)
        self.monthly_stats.grid_rowconfigure(9, weight=1)
        self.monthly_stats.grid_rowconfigure(10, weight=1)
        self.monthly_stats.grid_rowconfigure(11, weight=1)
        self.monthly_stats.grid_rowconfigure(12, weight=1)

        # Create yearly stats
        ttk.Label(self.yearly_stats, text=f"Yearly Stats", font=("Arial Black", 12), anchor="center", background="white") \
            .grid(row=0, column=0, columnspan=2, sticky="ew", pady=15)
        
        ttk.Label(self.yearly_stats, text=f"Last Year: {year_stats['previous']}", font=("Arial", 12), anchor="center", background="white") \
            .grid(row=1, column=0, sticky="ew", pady=(10, 20))
        
        ttk.Label(self.yearly_stats, text=f"This Year: {year_stats['current']}", font=("Arial", 12), anchor="center", background="white") \
            .grid(row=1, column=1, sticky="ew", pady=(10, 20))
        
        self.yearly_stats.grid_columnconfigure(0, weight=1)
        self.yearly_stats.grid_columnconfigure(1, weight=1)
        self.yearly_stats.grid_rowconfigure(0, weight=1)
        self.yearly_stats.grid_rowconfigure(1, weight=1)
        
        # Create monthly stats
        ttk.Label(self.monthly_stats, text=f"Monthly Stats", font=("Arial Black", 12), anchor="center", background="white") \
            .grid(row=0, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        
        ttk.Label(self.monthly_stats, text=f"January: {month_stats.get(1, 0)}", font=("Arial", 12), anchor="center", background="white") \
            .grid(row=1, column=0, sticky="ew", padx=30)
        
        ttk.Label(self.monthly_stats, text=f"February: {month_stats.get(2, 0)}", font=("Arial", 12), anchor="center", background="white") \
            .grid(row=2, column=0, sticky="ew", padx=30)
        
        ttk.Label(self.monthly_stats, text=f"March: {month_stats.get(3, 0)}", font=("Arial", 12), anchor="center", background="white") \
            .grid(row=3, column=0, sticky="ew", padx=30)
        
        ttk.Label(self.monthly_stats, text=f"April: {month_stats.get(4, 0)}", font=("Arial", 12), anchor="center", background="white") \
            .grid(row=4, column=0, sticky="ew", padx=30)
        
        ttk.Label(self.monthly_stats, text=f"May: {month_stats.get(5, 0)}", font=("Arial", 12), anchor="center", background="white") \
            .grid(row=5, column=0, sticky="ew", padx=30)
        
        ttk.Label(self.monthly_stats, text=f"June: {month_stats.get(6, 0)}", font=("Arial", 12), anchor="center", background="white") \
            .grid(row=6, column=0, sticky="ew", padx=30, pady=(0, 20))
        
        ttk.Label(self.monthly_stats, text=f"July: {month_stats.get(7, 0)}", font=("Arial", 12), anchor="center", background="white") \
            .grid(row=1, column=1, sticky="ew", padx=30)
        
        ttk.Label(self.monthly_stats, text=f"August: {month_stats.get(8, 0)}", font=("Arial", 12), anchor="center", background="white") \
            .grid(row=2, column=1, sticky="ew", padx=30)
        
        ttk.Label(self.monthly_stats, text=f"September: {month_stats.get(9, 0)}", font=("Arial", 12), anchor="center", background="white") \
            .grid(row=3, column=1, sticky="ew", padx=30)
        
        ttk.Label(self.monthly_stats, text=f"October: {month_stats.get(10, 0)}", font=("Arial", 12), anchor="center", background="white") \
            .grid(row=4, column=1, sticky="ew", padx=30)
        
        ttk.Label(self.monthly_stats, text=f"November: {month_stats.get(11, 0)}", font=("Arial", 12), anchor="center", background="white") \
            .grid(row=5, column=1, sticky="ew", padx=30)
        
        ttk.Label(self.monthly_stats, text=f"December: {month_stats.get(12, 0)}", font=("Arial", 12), anchor="center", background="white") \
            .grid(row=6, column=1, sticky="ew", padx=30, pady=(0, 20))
        
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