import uuid
import ttkbootstrap as ttk
from tkinter import messagebox, Event
from PIL import Image, ImageTk
from datetime import datetime

from libs.supabase_client import Supabase
from libs.data import Districts
from libs.utils import generate_contract_pdf, format_indian_number, lighten_color

class HomePage(ttk.Frame):
    def __init__(self, parent: ttk.Frame, supabase: Supabase, show_page_callback):
        super().__init__(parent)
        self.show_page_callback = show_page_callback
        self.supabase = supabase

        self.style = ttk.Style()
        self.style.configure("Custom.TEntry", padding=6)
        self.grid_columnconfigure(0, weight=1)

        self.form = ttk.Frame(self)
        self.form.grid(row=0, column=0, sticky="ew", padx=30, pady=30)

        def add_label_entry(row, text, col=0, colspan=2):
            label = ttk.Label(self.form, text=text, font=("Arial", 10))
            label.grid(row=row, column=col, sticky="e", padx=10, pady=5)
            entry = ttk.Entry(self.form, width=60, font=("Arial", 10), style="Custom.TEntry")
            entry.grid(row=row, column=col+1, columnspan=colspan, sticky="ew", pady=10)
            return entry
        
        self.org_entry = add_label_entry(0, "Organizer:", colspan=1)
        self.venue_entry = add_label_entry(0, "Venue:", col=2, colspan=1)
        self.city_entry = add_label_entry(1, "City:", colspan=1)

        
        self.style.configure("Custom.TCombobox", padding=6)
        ttk.Label(self.form, text="District:", font=("Arial, 10")).grid(row=1, column=2, sticky="e", padx=(0, 10), pady=5)
        districts = ["-- Select District --"] + Districts
        self.district_cb = ttk.Combobox(self.form, width=40, state="readonly", style="Custom.TCombobox", values=districts)
        self.district_cb.current(0)
        self.district_cb.grid(row=1, column=3, sticky="ew")

        # Date & Time row
        # Date
        ttk.Label(self.form, text="Date:", font=("Arial, 10")).grid(row=2, column=0, sticky="e", padx=(0, 10), pady=5)
        self.day_cb = ttk.Combobox(self.form, values=[f"{d:02}" for d in range(1, 32)], width=3, state="readonly")
        self.day_cb.current(0)
        self.day_cb.grid(row=2, column=1, sticky="w")

        self.month_cb = ttk.Combobox(self.form, width=4, state="readonly",
                        values=["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])
        self.month_cb.current(0)
        self.month_cb.grid(row=2, column=1, sticky="w", padx=(50, 0))

        self.year_cb = ttk.Combobox(self.form, values=[f"{y:02}" for y in range(2020, 2035)], width=5, state="readonly")
        self.year_cb.current(5)
        self.year_cb.grid(row=2, column=1, sticky="w", padx=(105, 0))

        # Time
        ttk.Label(self.form, text="Time:", font=("Arial, 10")).grid(row=2, column=1, sticky="e", padx=(0, 150), pady=5)
        self.hour_cb = ttk.Combobox(self.form, values=[f"{h:02}" for h in range(1, 13)], width=3, state="readonly")
        self.hour_cb.current(0)
        self.hour_cb.grid(row=2, column=1, sticky="e", padx=(0, 100))

        self.min_cb = ttk.Combobox(self.form, values=[f"{m:02}" for m in range(0, 60, 15)], width=3, state="readonly")
        self.min_cb.current(0)
        self.min_cb.grid(row=2, column=1, sticky="e", padx=(0, 50))

        self.ampm_cb = ttk.Combobox(self.form, values=["AM", "PM"], width=3, state="readonly")
        self.ampm_cb.current(1)
        self.ampm_cb.grid(row=2, column=1, sticky="e")

        # Sound checkbox
        self.style.configure("Custom.TCheckbutton", font=("Arial", 10))
        self.sound_var = ttk.BooleanVar()
        self.sound_cb = ttk.Checkbutton(self.form, text="With Input Sound", variable=self.sound_var, style="Custom.TCheckbutton")
        self.sound_cb.grid(row=2, column=3, sticky="w")

        # Contract Amount row
        self.total_entry = add_label_entry(3, "Total (₹):", colspan=1)
        self.advance_entry = add_label_entry(3, "Advance (₹):", col=2, colspan=1)
        self.contact_entry = add_label_entry(4, "Contacts:", colspan=1)
        self.note_entry = add_label_entry(4, "Note:", col=2, colspan=1)

        self.total_entry.bind("<KeyRelease>", lambda e: self.on_amount_entry(e, self.total_entry))
        self.advance_entry.bind("<KeyRelease>", lambda e: self.on_amount_entry(e, self.advance_entry))

        # Buttons
        button_frame = ttk.Frame(self)
        button_frame.grid(row=1, column=0, pady=20)

        view_btn = ttk.Button(button_frame, text="View Concerts", width=16, command=lambda: self.show_page("concerts"))
        view_btn.pack(side="left", padx=5, ipady=5)

        clear_btn = ttk.Button(button_frame, text="Clear", command=self.clear_form)
        clear_btn.pack(side="left", padx=5, ipady=5)

        save_btn = ttk.Button(button_frame, text="Save Concert", width=16, style="success", command=self.save_concert)
        save_btn.pack(side="left", padx=5, ipady=5)

        self.form.grid_columnconfigure(0, weight=0)  # Labels - don't stretch
        self.form.grid_columnconfigure(1, weight=1)  # Entries - stretch
        self.form.grid_columnconfigure(2, weight=0)  # Labels - don't stretch
        self.form.grid_columnconfigure(3, weight=1)  # Entries - stretch

        self.stats = ttk.Frame(self)
        self.stats.grid(row=2, column=0, sticky="ew", padx=30, pady=(20, 0))
        self.stats.grid_columnconfigure(0, weight=1)
        self.stats.grid_columnconfigure(1, weight=1)

        theme_bg = self.style.lookup("TFrame", "background")
        self.card_bg = lighten_color(theme_bg, amount=0.1)

        self.style.configure("Card.TFrame", background=self.card_bg, borderwidth=1, relief="solid")

        self.yearly_stats = ttk.Frame(self.stats, style="Card.TFrame")
        self.yearly_stats.grid(row=0, column=0, sticky="news", padx=(20, 30), pady=(0, 10))

        self.district_stats = ttk.Frame(self.stats, style="Card.TFrame")
        self.district_stats.grid(row=1, column=0, sticky="news", padx=(20, 30), pady=(10, 0))

        self.monthly_stats = ttk.Frame(self.stats, style="Card.TFrame")
        self.monthly_stats.grid(row=0, rowspan=2, column=1, sticky="news", padx=(30, 20))

        self.style.configure("Card.TLabel", background=self.card_bg)
        self.load_stats()


    def load_stats(self):
        for stats in [self.yearly_stats, self.district_stats, self.monthly_stats]:
            for widget in stats.winfo_children():
                widget.destroy()
        
        year_stats, district_stats, month_stats = self.supabase.get_stats()

        # Create yearly stats
        ttk.Label(self.yearly_stats, text=f"Yearly Stats", font=("Arial Black", 12), style="Card.TLabel", anchor="center") \
            .grid(row=0, column=0, columnspan=2, sticky="ew", padx=2, pady=15)
        
        ttk.Label(self.yearly_stats, text=f"Last Year: {year_stats['previous']}", font=("Arial", 12), style="Card.TLabel", anchor="center") \
            .grid(row=1, column=0, sticky="ew", padx=2, pady=(10, 20))
        
        ttk.Label(self.yearly_stats, text=f"This Year: {year_stats['current']}", font=("Arial", 12), style="Card.TLabel", anchor="center") \
            .grid(row=1, column=1, sticky="ew", padx=2, pady=(10, 20))
        
        self.yearly_stats.grid_columnconfigure(0, weight=1)
        self.yearly_stats.grid_columnconfigure(1, weight=1)
        self.yearly_stats.grid_rowconfigure(0, weight=1)
        self.yearly_stats.grid_rowconfigure(1, weight=1)
        
        # Create district stats
        highest_district = max(district_stats.items(), key=lambda x: x[1])
        lowest_district = min({district: count for district, count in district_stats.items() if count > 0}.items(),
                              key=lambda x: x[1])
        
        ttk.Label(self.district_stats, text=f"District Stats", font=("Arial Black", 12), style="Card.TLabel", anchor="center") \
            .grid(row=0, column=0, columnspan=2, sticky="ew", padx=2, pady=15)
        
        ttk.Label(self.district_stats, text=f"Highest: {highest_district[0]} ({highest_district[1]})", font=("Arial", 12), style="Card.TLabel", anchor="center") \
            .grid(row=1, column=0, sticky="ew", padx=2, pady=(10, 20))
        
        ttk.Label(self.district_stats, text=f"Lowest: {lowest_district[0]} ({lowest_district[1]})", font=("Arial", 12), style="Card.TLabel", anchor="center") \
            .grid(row=1, column=1, sticky="ew", padx=2, pady=(10, 20))
        
        # Expand button
        self.expand_image_normal = ImageTk.PhotoImage(Image.open("assets/images/expand.png").resize((15, 15)))
        self.expand_image_hover = ImageTk.PhotoImage(Image.open("assets/images/expand_hover.png").resize((15, 15)))

        self.expand_stats = ttk.Label(self.district_stats, image=self.expand_image_normal, style="Card.TLabel", cursor="hand2")
        self.expand_stats.grid(row=0, column=1, sticky="ne", padx=(0, 15), pady=(15, 0))

        self.expand_stats.bind("<Enter>", self.on_enter)
        self.expand_stats.bind("<Leave>", self.on_leave)
        self.expand_stats.bind("<Button-1>", lambda e: self.show_page("stats"))
        
        self.district_stats.grid_columnconfigure(0, weight=1)
        self.district_stats.grid_columnconfigure(1, weight=1)
        self.district_stats.grid_rowconfigure(0, weight=1)
        self.district_stats.grid_rowconfigure(1, weight=1)

        # Create monthly stats
        ttk.Label(self.monthly_stats, text=f"Monthly Stats", font=("Arial Black", 12), style="Card.TLabel", anchor="center") \
            .grid(row=0, column=0, columnspan=2, sticky="ew", padx=2, pady=(10, 0))
        
        ttk.Label(self.monthly_stats, text=f"January: {month_stats.get(1, 0)}", font=("Arial", 12), style="Card.TLabel", anchor="center") \
            .grid(row=1, column=0, sticky="ew", padx=30)
        
        ttk.Label(self.monthly_stats, text=f"February: {month_stats.get(2, 0)}", font=("Arial", 12), style="Card.TLabel", anchor="center") \
            .grid(row=2, column=0, sticky="ew", padx=30)
        
        ttk.Label(self.monthly_stats, text=f"March: {month_stats.get(3, 0)}", font=("Arial", 12), style="Card.TLabel", anchor="center") \
            .grid(row=3, column=0, sticky="ew", padx=30)
        
        ttk.Label(self.monthly_stats, text=f"April: {month_stats.get(4, 0)}", font=("Arial", 12), style="Card.TLabel", anchor="center") \
            .grid(row=4, column=0, sticky="ew", padx=30)
        
        ttk.Label(self.monthly_stats, text=f"May: {month_stats.get(5, 0)}", font=("Arial", 12), style="Card.TLabel", anchor="center") \
            .grid(row=5, column=0, sticky="ew", padx=30)
        
        ttk.Label(self.monthly_stats, text=f"June: {month_stats.get(6, 0)}", font=("Arial", 12), style="Card.TLabel", anchor="center") \
            .grid(row=6, column=0, sticky="ew", padx=30, pady=(0, 20))
        
        ttk.Label(self.monthly_stats, text=f"July: {month_stats.get(7, 0)}", font=("Arial", 12), style="Card.TLabel", anchor="center") \
            .grid(row=1, column=1, sticky="ew", padx=30)
        
        ttk.Label(self.monthly_stats, text=f"August: {month_stats.get(8, 0)}", font=("Arial", 12), style="Card.TLabel", anchor="center") \
            .grid(row=2, column=1, sticky="ew", padx=30)
        
        ttk.Label(self.monthly_stats, text=f"September: {month_stats.get(9, 0)}", font=("Arial", 12), style="Card.TLabel", anchor="center") \
            .grid(row=3, column=1, sticky="ew", padx=30)
        
        ttk.Label(self.monthly_stats, text=f"October: {month_stats.get(10, 0)}", font=("Arial", 12), style="Card.TLabel", anchor="center") \
            .grid(row=4, column=1, sticky="ew", padx=30)
        
        ttk.Label(self.monthly_stats, text=f"November: {month_stats.get(11, 0)}", font=("Arial", 12), style="Card.TLabel", anchor="center") \
            .grid(row=5, column=1, sticky="ew", padx=30)
        
        ttk.Label(self.monthly_stats, text=f"December: {month_stats.get(12, 0)}", font=("Arial", 12), style="Card.TLabel", anchor="center") \
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


    def load_concert(self, concert):
        self.clear_form()
        self.concert_id = concert["id"]
        self.is_cancelled = concert["is_cancelled"]

        self.org_entry.insert(0, concert["organizer"] or "")
        self.venue_entry.insert(0, concert["venue"] or "")
        self.city_entry.insert(0, concert["city"] or "")
        self.district_cb.set(concert["district"] or "-- Select District --")

        self.total_entry.insert(0, format_indian_number(concert["total"]))
        self.advance_entry.insert(0, format_indian_number(concert["advance"]))
        self.contact_entry.insert(0, concert["contact"] or "")
        self.note_entry.insert(0, concert["note"] or "")

        self.sound_var.set(concert["is_sound_included"])

        # Parse date
        year, month, day = concert["date"].split("-")
        month_index = int(month) - 1
        month_name = self.month_cb["values"][month_index]
        self.day_cb.set(day)
        self.month_cb.set(month_name)
        self.year_cb.set(year)

        hour, minute, _ = concert["time"].split(":")
        hour = int(hour)
        ampm = "AM" if hour < 12 else "PM"
        hour_12 = hour % 12 or 12
        self.hour_cb.set(f"{hour_12:02}")
        self.min_cb.set(minute)
        self.ampm_cb.set(ampm)

        self.load_stats()


    def clear_form(self):
        for entry in [
            self.org_entry,
            self.venue_entry,
            self.city_entry,
            self.total_entry,
            self.advance_entry,
            self.contact_entry,
            self.note_entry,
        ]:
            entry.delete(0, ttk.END)

        self.district_cb.current(0)
        self.day_cb.current(0)
        self.month_cb.current(0)
        self.year_cb.current(datetime.now().year - 2020)

        self.hour_cb.current(0)
        self.min_cb.current(0)
        self.ampm_cb.current(1)

        self.sound_var.set(False)
        self.concert_id = str(uuid.uuid4())
        self.is_cancelled = False
        self.org_entry.focus_set()
    

    def on_amount_entry(self, event: Event, entry: ttk.Entry):
        value = entry.get()
        old_len = len(value)
        cursor_pos = entry.index(ttk.INSERT)

        if event.keysym == "BackSpace" and cursor_pos > 0 and self.is_comma_deleted(value):
            # Delete the character before the comma
            value = value[:cursor_pos - 1] + value[cursor_pos:]
            cursor_pos -= 1  # Move cursor back one more after manual deletion
        
        # Remove leading zeros (except when the number is 0)
        value = value.lstrip("0") or ""

        formatted = format_indian_number(value)
        new_len = len(formatted)

        entry.delete(0, ttk.END)
        entry.insert(0, formatted)

        # Adjust cursor position
        cursor_shift = new_len - old_len
        new_cursor_pos = cursor_pos + cursor_shift
        if new_cursor_pos < 0:
            new_cursor_pos = 0
        elif new_cursor_pos > new_len:
            new_cursor_pos = new_len

        entry.icursor(new_cursor_pos)
    

    def is_comma_deleted(self, value: str) -> bool:
        formatted_value = format_indian_number(value)
        return value.count(",") < formatted_value.count(",")


    def save_concert(self):
        if not self.org_entry.get():
            messagebox.showwarning("Missing Organizer", "Organizer cannot be empty.")
            return

        if not self.venue_entry.get():
            messagebox.showwarning("Missing Venue", "Venue cannot be empty.")
            return
        
        if not self.city_entry.get():
            messagebox.showwarning("Missing City", "City cannot be empty.")
            return
        
        if self.district_cb.get() == "-- Select District --":
            messagebox.showwarning("Missing District", "Select a District.")
            return
        
        if not self.total_entry.get():
            messagebox.showwarning("Missing Total", "Total cannot be empty.")
            return
        
        if not self.advance_entry.get():
            messagebox.showwarning("Missing Advance", "Advance cannot be empty.")
            return
        
        if int(self.total_entry.get().replace(",", "")) < int(self.advance_entry.get().replace(",", "")):
            messagebox.showwarning("Invalid Amounts", f"Total cannot be less than Advance.")
            return
        
        concert = {
            "id": self.concert_id,
            "organizer": self.org_entry.get().strip(),
            "venue": self.venue_entry.get().strip(),
            "city": self.city_entry.get().strip(),
            "district": self.district_cb.get(),
            "date": f"{self.year_cb.get()}-{self.month_cb.current() + 1:02}-{self.day_cb.get()}",
            "time": f"{int(self.hour_cb.get()) % 12 + (12 if self.ampm_cb.get() == 'PM' else 0):02}:{self.min_cb.get()}:00",
            "is_sound_included": self.sound_var.get(),
            "total": int(self.total_entry.get().replace(",", "")),
            "advance": int(self.advance_entry.get().replace(",", "")),
            "contact": self.contact_entry.get().strip() if self.contact_entry.get() else None,
            "note": self.note_entry.get().strip() if self.note_entry.get() else None,
            "is_cancelled": self.is_cancelled
        }

        generate_contract_pdf(concert)
        self.supabase.save_concert(concert)
        messagebox.showinfo("Success", "Concert saved successfully!")
        self.show_page("concerts")
    

    
    def on_enter(self, event):
        self.expand_stats.config(image=self.expand_image_hover)


    def on_leave(self, event):
        self.expand_stats.config(image=self.expand_image_normal)
    

    def show_page(self, page_name):
        self.show_page_callback(page_name)