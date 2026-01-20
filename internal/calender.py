import customtkinter as ctk
from datetime import date, datetime, timedelta
import calendar

class CalendarDialog(ctk.CTkToplevel):
    def __init__(self, parent, initial_date=None):
        super().__init__(parent)

        self.parent = parent
        self.selected_date = None  # This holds the result
        
        # --- Colors (Easy to change) ---
        self.colors = {
            "primary": "#1f6aa5",      # Selection color
            "hover": "#144870",        # Hover color
            "today": "#2cc985",        # Today color
            "text": "white"            # Text color
        }

        # --- Data Setup ---
        self._view_date = date.today().replace(day=1) # Current month being viewed

        if initial_date:
            try:
                dt = datetime.strptime(initial_date, '%d/%m/%y').date()
                self.selected_date = dt
                self._view_date = dt.replace(day=1)
            except ValueError:
                pass 

        # --- Window Config ---
        self.title("Select Date")
        self.geometry("340x400")
        self.resizable(False, False)
        
        # Make Modal (blocks other windows)
        self.transient(parent)
        self.grab_set()
        
        # --- Build UI ---
        self._create_widgets()
        self._update_grid()
        
        # Center the window
        self.after(10, self._center_window)

    def _center_window(self):
        self.update_idletasks()
        x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - (self.winfo_width() // 2)
        y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")

    def _create_widgets(self):
        """Creates the layout once. We just update text later."""
        
        # 1. Header (Month/Year)
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=10, pady=(15, 5))

        ctk.CTkButton(header, text="<", width=30, command=self._prev_month).pack(side="left")
        
        self.lbl_title = ctk.CTkLabel(header, text="Month", font=("Arial", 16, "bold"))
        self.lbl_title.pack(side="left", expand=True)
        
        ctk.CTkButton(header, text=">", width=30, command=self._next_month).pack(side="right")

        # 2. Days of Week
        days_frame = ctk.CTkFrame(self, fg_color="transparent")
        days_frame.pack(fill="x", padx=15, pady=5)
        for d in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]:
            ctk.CTkLabel(days_frame, text=d, width=40, font=("Arial", 12, "bold")).pack(side="left", expand=True)

        # 3. The Date Grid (Re-usable buttons)
        grid_frame = ctk.CTkFrame(self, fg_color="transparent")
        grid_frame.pack(fill="both", expand=True, padx=10)
        
        self.buttons = []
        for r in range(6):
            for c in range(7):
                btn = ctk.CTkButton(
                    grid_frame, text="", width=40, height=35,
                    fg_color="transparent",
                    command=lambda i=(r*7)+c: self._on_click(i)
                )
                btn.grid(row=r, column=c, padx=2, pady=2)
                self.buttons.append(btn)

        # 4. Footer
        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkButton(footer, text="Today", fg_color="transparent", border_width=1, 
                      text_color="gray90", command=self._goto_today).pack(side="left", padx=5)
        
        ctk.CTkButton(footer, text="Cancel", fg_color="transparent", text_color="red", 
                      width=60, hover_color="#330000", command=self.destroy).pack(side="right")
        
        ctk.CTkButton(footer, text="OK", width=80, fg_color="green", 
                      command=self._confirm).pack(side="right", padx=5)

    def _update_grid(self):
        """Refreshes button labels and colors."""
        year, month = self._view_date.year, self._view_date.month
        self.lbl_title.configure(text=f"{calendar.month_name[month]} {year}")
        
        # Get days
        month_days = calendar.monthcalendar(year, month)
        flat_days = [d for week in month_days for d in week]
        
        today = date.today()

        for i, btn in enumerate(self.buttons):
            if i < len(flat_days) and flat_days[i] != 0:
                d_val = flat_days[i]
                d_obj = date(year, month, d_val)
                
                btn.configure(text=str(d_val), state="normal")
                
                # Logic for coloring buttons
                if d_obj == self.selected_date:
                    btn.configure(fg_color=self.colors["primary"], hover_color=self.colors["hover"])
                elif d_obj == today:
                    btn.configure(fg_color=self.colors["today"], hover_color="#26ad73")
                else:
                    btn.configure(fg_color="transparent", hover_color="gray40")
            else:
                btn.configure(text="", fg_color="transparent", state="disabled")

    def _on_click(self, index):
        """Handle button click based on index."""
        btn = self.buttons[index]
        day_text = btn.cget("text")
        if day_text:
            self.selected_date = date(self._view_date.year, self._view_date.month, int(day_text))
            self._update_grid()

    def _prev_month(self):
        first = self._view_date.replace(day=1)
        self._view_date = (first - timedelta(days=1)).replace(day=1)
        self._update_grid()

    def _next_month(self):
        self._view_date = (self._view_date.replace(day=28) + timedelta(days=4)).replace(day=1)
        self._update_grid()

    def _goto_today(self):
        self.selected_date = date.today()
        self._view_date = date.today().replace(day=1)
        self._update_grid()

    def _confirm(self):
        if self.selected_date:
            self.destroy()
        else:
            print("Please select a date")