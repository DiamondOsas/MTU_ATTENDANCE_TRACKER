import customtkinter as ctk
from tkinter import messagebox
from datetime import date, datetime
import calendar

class CalendarDialog(ctk.CTkToplevel):
    """
    A simple calendar dialog for date selection.
    This calendar allows users to select a date in DD/MM/YY format.
    """
    def __init__(self, parent, initial_date=None):
        super().__init__(parent)
        
        self.parent = parent
        self.selected_date = None
        
        # Parse initial date if provided
        if initial_date:
            try:
                self.current_date = datetime.strptime(initial_date, '%d/%m/%y').date()
            except ValueError:
                self.current_date = date.today()
        else:
            self.current_date = date.today()
        
        # Window configuration
        self.title("Select Date")
        self.geometry("400x400")
        self.resizable(False, False)
        
        # Make window modal
        self.transient(parent)
        self.grab_set()
        
        # Create calendar UI
        self.create_calendar_ui()
        
        # Center the dialog
        self.center_dialog()
    
    def center_dialog(self):
        """
        Centers the dialog on the parent window.
        """
        self.update_idletasks()
        x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - (self.winfo_width() // 2)
        y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")
    
    def create_calendar_ui(self):
        """
        Creates a simple calendar UI.
        """
        # Header with navigation
        header_frame = ctk.CTkFrame(self)
        header_frame.pack(fill="x", padx=10, pady=10)
        
        # Previous month button
        prev_btn = ctk.CTkButton(header_frame, text="<", width=30, command=self.prev_month)
        prev_btn.pack(side="left", padx=5)
        
        # Month/Year label
        self.month_label = ctk.CTkLabel(header_frame, text="", font=ctk.CTkFont(size=14, weight="bold"))
        self.month_label.pack(side="left", expand=True)
        
        # Next month button
        next_btn = ctk.CTkButton(header_frame, text=">", width=30, command=self.next_month)
        next_btn.pack(side="right", padx=5)
        
        # Days header
        days_frame = ctk.CTkFrame(self)
        days_frame.pack(fill="x", padx=10, pady=5)
        
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for i, day in enumerate(days):
            day_label = ctk.CTkLabel(days_frame, text=day, width=40, anchor="center")
            day_label.grid(row=0, column=i, padx=2, pady=2)
        
        # Calendar grid
        self.calendar_grid = ctk.CTkFrame(self)
        self.calendar_grid.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Buttons frame
        buttons_frame = ctk.CTkFrame(self)
        buttons_frame.pack(fill="x", padx=10, pady=10)
        
        # Today button
        today_btn = ctk.CTkButton(buttons_frame, text="Today", command=self.set_today)
        today_btn.pack(side="left", padx=10)
        
        # OK button
        ok_btn = ctk.CTkButton(buttons_frame, text="OK", command=self.confirm_selection, fg_color="green")
        ok_btn.pack(side="right", padx=10)
        
        # Cancel button
        cancel_btn = ctk.CTkButton(buttons_frame, text="Cancel", command=self.destroy)
        cancel_btn.pack(side="right", padx=5)
        
        # Initialize calendar
        self.update_calendar()
    
    def update_calendar(self):
        """
        Updates the calendar display.
        """
        # Clear grid
        for widget in self.calendar_grid.winfo_children():
            widget.destroy()
        
        # Update month label
        month_names = ["January", "February", "March", "April", "May", "June",
                      "July", "August", "September", "October", "November", "December"]
        self.month_label.configure(text=f"{month_names[self.current_date.month-1]} {self.current_date.year}")
        
        # Get calendar data
        month_calendar = calendar.monthcalendar(self.current_date.year, self.current_date.month)
        
        # Display days
        for week_num, week in enumerate(month_calendar):
            for day_num, day in enumerate(week):
                if day == 0:  # Empty cell
                    cell = ctk.CTkLabel(self.calendar_grid, text="", width=40, height=30)
                else:
                    btn = ctk.CTkButton(
                        self.calendar_grid,
                        text=str(day),
                        width=40,
                        height=30,
                        command=lambda d=day: self.select_day(d)
                    )
                    
                    # Highlight today
                    if (day == date.today().day and 
                        self.current_date.month == date.today().month and 
                        self.current_date.year == date.today().year):
                        btn.configure(fg_color=("gray75", "gray25"))
                    
                    # Highlight selected date
                    if (self.selected_date and 
                        day == self.selected_date.day and
                        self.current_date.month == self.selected_date.month and
                        self.current_date.year == self.selected_date.year):
                        btn.configure(fg_color=("blue", "darkblue"))
                    
                    cell = btn
                
                cell.grid(row=week_num+1, column=day_num, padx=2, pady=2)
    
    def select_day(self, day):
        """
        Selects a day and updates the calendar.
        """
        self.selected_date = date(self.current_date.year, self.current_date.month, day)
        self.update_calendar()
    
    def confirm_selection(self):
        """
        Confirms the date selection.
        """
        if self.selected_date:
            self.destroy()
        else:
            messagebox.showwarning("No Selection", "Please select a date first.")
    
    def prev_month(self):
        """
        Goes to the previous month.
        """
        if self.current_date.month == 1:
            self.current_date = self.current_date.replace(year=self.current_date.year-1, month=12)
        else:
            self.current_date = self.current_date.replace(month=self.current_date.month-1)
        self.update_calendar()
    
    def next_month(self):
        """
        Goes to the next month.
        """
        if self.current_date.month == 12:
            self.current_date = self.current_date.replace(year=self.current_date.year+1, month=1)
        else:
            self.current_date = self.current_date.replace(month=self.current_date.month+1)
        self.update_calendar()
    
    def set_today(self):
        """
        Sets the date to today.
        """
        self.current_date = date.today()
        self.selected_date = date.today()
        self.update_calendar()