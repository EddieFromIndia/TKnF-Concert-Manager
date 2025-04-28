from tkinter import ttk, messagebox, Frame
from datetime import datetime

from libs.supabase_client import Supabase
from libs.utils import generate_contract_pdf, format_indian_number

class ConcertsPage(ttk.Frame):
    def __init__(self, parent: Frame, supabase: Supabase, show_page_callback):
        super().__init__(parent)
        self.show_page_callback = show_page_callback
        self.supabase = supabase
        self.concerts = {}

        ttk.Label(self, text="Tanmay Kar and Friends Concerts", font=("Arial Black", 24)).pack(pady=10)

        # Treeview setup
        columns = ("organizer", "venue", "district", "date", "time", "total", "advance", "note")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=15)
        for col in columns:
            self.tree.heading(col, text=col.capitalize())
            self.tree.column(col, anchor="center", width=100)

        self.tree.pack(fill="both", expand=True, padx=20, pady=(10, 5))

        self.tree.tag_configure("cancelled", background="#f8d7da")  # light red for cancelled
        self.tree.tag_configure("today", background="#d4edda")  # light green for today
        self.tree.bind("<<TreeviewSelect>>", self.on_concert_selected)

        # Action buttons
        action_frame = ttk.Frame(self)
        action_frame.pack(pady=(10, 20))

        self.edit_btn = ttk.Button(action_frame, text="Edit", command=self.edit_concert, state="disabled")
        self.edit_btn.pack(side="left", padx=5, ipady=5)

        self.cancel_btn = ttk.Button(action_frame, text="Cancel/Restore", width=20, command=self.cancel_concert, state="disabled")
        self.cancel_btn.pack(side="left", padx=5, ipady=5)

        self.delete_btn = ttk.Button(action_frame, text="Delete", command=self.delete_concert, state="disabled")
        self.delete_btn.pack(side="left", padx=5, ipady=5)

        self.mark_paid_btn = ttk.Button(action_frame, text="Mark Full Paid", width=20, command=self.mark_paid_concert, state="disabled")
        self.mark_paid_btn.pack(side="left", padx=5, ipady=5)

        self.generate_pdf_btn = ttk.Button(action_frame, text="Generate PDF", width=20, command=self.generate_pdf, state="disabled")
        self.generate_pdf_btn.pack(side="left", padx=5, ipady=5)

        # Add concert button
        ttk.Button(self, text="Add New Concert", width=20, command=lambda: self.show_page("home")).pack(pady=(0, 20), ipady=5)

        self.load_concerts()

    def load_concerts(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.concerts.clear()

        concerts = self.supabase.get_concerts()

        for concert in concerts:
            display_organizer = f"🔊 {concert['organizer']}" if concert["is_sound_included"] else concert["organizer"]
            values = (
                display_organizer,
                concert["venue"] or "-",
                concert["district"] or "-",
                datetime.strptime(concert["date"], "%Y-%m-%d").strftime("%d %b, %Y") or "-",
                datetime.strptime(concert["time"], "%H:%M:%S").strftime("%I:%M %p") or "-",
                format_indian_number(concert["total"]) or "-",
                format_indian_number(concert["advance"]) or "-",
                concert["contact"] or "-",
                concert["note"] or "-"
            )
            tags = ("cancelled",) if concert["is_cancelled"] else ()
            tags += ("today",) if concert["date"] == datetime.now().strftime("%Y-%m-%d") else ()

            iid = str(concert["id"])
            self.tree.insert("", "end", iid=iid, values=values, tags=tags)
            self.concerts[iid] = concert
        
        self.tree.column("organizer", width=220, stretch=True)
        self.tree.column("venue", width=220, stretch=True)
        self.tree.column("district", width=100, stretch=True)
        self.tree.column("date", width=70, stretch=True)
        self.tree.column("time", width=70, stretch=True)
        self.tree.column("total", width=70, stretch=True)
        self.tree.column("advance", width=70, stretch=True)
        self.tree.column("note", width=120, stretch=True)
    

    def on_concert_selected(self, event=None):
        selected = self.tree.selection()
        if selected:
            concert_id = selected[0]
            concert = self.concerts.get(concert_id, {})

            if concert["is_cancelled"]:
                self.cancel_btn.config(text="Restore Concert")
            else:
                self.cancel_btn.config(text="Cancel Concert")
            
            self.edit_btn.config(state="normal")
            self.cancel_btn.config(state="normal")
            self.delete_btn.config(state="normal")
            self.mark_paid_btn.config(state="normal")
            self.generate_pdf_btn.config(state="normal")
        else:
            self.edit_btn.config(state="disabled")
            self.cancel_btn.config(state="disabled")
            self.delete_btn.config(state="disabled")
            self.mark_paid_btn.config(state="disabled")
            self.generate_pdf_btn.config(state="disabled")


    def get_selected_concert(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a concert.")
            return None
        
        iid = selected[0]
        return self.concerts.get(iid)


    def edit_concert(self):
        concert = self.get_selected_concert()
        if concert:
            self.show_page("home", concert)


    def cancel_concert(self):
        concert = self.get_selected_concert()
        if not concert:
            return
        
        if concert["is_cancelled"]:
            # Restore the concert
            if messagebox.askyesno(
                "Restore Confirmation",
                f"Are you sure you want to restore the concert by {concert['organizer']} on {concert['date']}?"
            ):
                self.supabase.restore_concert(concert["id"])
                self.tree.item(concert["id"], tags=())
                concert["is_cancelled"] = not concert["is_cancelled"]
                self.cancel_btn.config(text="Cancel Concert")

        else:
            # Cancel the concert
            if messagebox.askyesno(
                "Cancel Confirmation",
                f"Are you sure you want to cancel the concert by {concert['organizer']} on {concert['date']}?"
            ):
                self.supabase.cancel_concert(concert["id"])
                self.tree.item(concert["id"], tags=("cancelled",))
                concert["is_cancelled"] = not concert["is_cancelled"]
                self.cancel_btn.config(text="Restore Concert")
    

    def delete_concert(self):
        concert = self.get_selected_concert()
        if concert and messagebox.askyesno("Delete Confirmation", F"Are you sure you want to DELETE the concert by {concert['organizer']} on {concert['date']}?"):
            self.supabase.delete_concert(concert["id"])
            self.load_concerts()
            messagebox.showinfo("Success", "Concert deleted!")
    

    def generate_pdf(self):
        concert = self.get_selected_concert()
        if concert:
            file_path = generate_contract_pdf(concert)
            messagebox.showinfo("Success", f"Contract PDF generated and saved in {file_path}")
    

    def mark_paid_concert(self):
        concert = self.get_selected_concert()
        if concert and messagebox.askyesno("Mark Full Paid", "Are you sure you want to mark the concert as full paid?"):
            generate_contract_pdf(concert, paid_in_full=True)
            concert["advance"] = concert["total"]
            self.supabase.save_concert(concert)
            self.load_concerts()
            messagebox.showinfo("Success", "Concert marked as paid!")
            

    def show_page(self, page_name, data=None):
        """Function to switch pages by hiding the current frame and showing the next one."""
        self.show_page_callback(page_name, data)