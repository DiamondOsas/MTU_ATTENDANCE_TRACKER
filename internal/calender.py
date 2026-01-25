import customtkinter as ctk
from datetime import date, datetime, timedelta
import calendar

class CalendarDialog(ctk.CTkToplevel):
    def __init__(self, parent, initial_date=None, selection_mode="single"):
        super().__init__(parent)

        self.parent = parent
        self.selection_mode = selection_mode  # "single" or "range"
        
        self.selected_date = None      # For single mode
        self.start_date = None         # For range mode
        self.end_date = None           # For range mode
        
        # --- Colors ---
        self.colors = {
            "primary": "#1f6aa5",      # Selection color
            "range": "#1f6aa5",        # Range fill color
            "hover": "#144870",        # Hover color
            "today": "#2cc985",        # Today color
            "text": "white",            # Text color
            "text_disabled": "gray50"
        }

        # --- Data Setup ---
        self._view_date = date.today().replace(day=1) # Current month being viewed

        if initial_date:
            try:
                dt = datetime.strptime(initial_date, '%d/%m/%y').date()
                if self.selection_mode == "single":
                    self.selected_date = dt
                else:
                    self.start_date = dt
                self._view_date = dt.replace(day=1)
            except ValueError:
                pass 

        # --- Window Config ---
        title = "Select Date" if selection_mode == "single" else "Select Date Range"
        self.title(title)
        self.geometry("340x450") # Slightly taller for instructions/status
        self.resizable(False, False)
        
        # Make Modal
        self.transient(parent)
        self.grab_set()
        
        # --- Build UI ---
        self._create_widgets()
        self._update_grid()
        
        # Center the window
        self.after(10, self._center_window)

    def get_selection(self):
        """Returns the result based on mode."""
        if self.selection_mode == "single":
            return self.selected_date
        else:
            return self.start_date, self.end_date

    def _center_window(self):
        self.update_idletasks()
        try:
            x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - (self.winfo_width() // 2)
            y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - (self.winfo_height() // 2)
            self.geometry(f"+{int(x)}+{int(y)}")
        except Exception:
            # Fallback if parent geometry is weird
            self.eval('tk::PlaceWindow . center')

    def _create_widgets(self):
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

        # 3. The Date Grid
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
        
        # 4. Info Label (For Range Mode)
        self.lbl_info = ctk.CTkLabel(self, text="", font=("Arial", 12))
        self.lbl_info.pack(pady=5)

        # 5. Footer
        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkButton(footer, text="Today", fg_color="transparent", border_width=1, 
                      text_color="gray90", command=self._goto_today).pack(side="left", padx=5)
        
        ctk.CTkButton(footer, text="Cancel", fg_color="transparent", text_color="#ff5555", 
                      width=60, hover_color="#330000", command=self.destroy).pack(side="right")
        
        ctk.CTkButton(footer, text="OK", width=80, fg_color="green", 
                      command=self._confirm).pack(side="right", padx=5)

    def _update_grid(self):
        year, month = self._view_date.year, self._view_date.month
        self.lbl_title.configure(text=f"{calendar.month_name[month]} {year}")
        
        month_days = calendar.monthcalendar(year, month)
        flat_days = [d for week in month_days for d in week]
        today = date.today()

        # Update Info Label
        if self.selection_mode == "single":
            txt = f"Selected: {self.selected_date.strftime('%d/%m/%y')}" if self.selected_date else "Select a date"
        else:
            s = self.start_date.strftime('%d/%m/%y') if self.start_date else "?"
            e = self.end_date.strftime('%d/%m/%y') if self.end_date else "?"
            txt = f"Range: {s} - {e}"
        self.lbl_info.configure(text=txt)

        for i, btn in enumerate(self.buttons):
            if i < len(flat_days) and flat_days[i] != 0:
                d_val = flat_days[i]
                current_date = date(year, month, d_val)
                
                btn.configure(text=str(d_val), state="normal")
                
                # Default style
                fg = "transparent"
                hover = "gray40"
                text_col = self.colors["text"]

                # Logic for coloring
                if self.selection_mode == "single":
                    if current_date == self.selected_date:
                        fg = self.colors["primary"]
                        hover = self.colors["hover"]
                else:
                    # Range Mode Logic
                    if self.start_date and current_date == self.start_date:
                        fg = self.colors["primary"]
                    elif self.end_date and current_date == self.end_date:
                        fg = self.colors["primary"]
                    elif self.start_date and self.end_date:
                        if self.start_date < current_date < self.end_date:
                             fg = self.colors["range"]
                             # Make it slightly lighter or different if possible, 
                             # but for flat design same color often works if contiguous.
                             # Let's use a slightly transparent look or same color.
                             pass
                
                # Today highlight (if not selected)
                if current_date == today and fg == "transparent":
                    fg = self.colors["today"]
                    hover = "#26ad73"

                btn.configure(fg_color=fg, hover_color=hover, text_color=text_col)
            else:
                btn.configure(text="", fg_color="transparent", state="disabled")

    def _on_click(self, index):
        btn = self.buttons[index]
        day_text = btn.cget("text")
        if not day_text: return
        
        clicked_date = date(self._view_date.year, self._view_date.month, int(day_text))

        if self.selection_mode == "single":
            self.selected_date = clicked_date
        else:
            # Range logic
            if self.start_date is None:
                self.start_date = clicked_date
                self.end_date = None
            elif self.end_date is None:
                # Second click
                if clicked_date < self.start_date:
                    self.end_date = self.start_date
                    self.start_date = clicked_date
                else:
                    self.end_date = clicked_date
            else:
                # Third click - reset and start new range
                self.start_date = clicked_date
                self.end_date = None
        
        self._update_grid()

    def _prev_month(self):
        first = self._view_date.replace(day=1)
        self._view_date = (first - timedelta(days=1)).replace(day=1)
        self._update_grid()

    def _next_month(self):
        self._view_date = (self._view_date.replace(day=28) + timedelta(days=4)).replace(day=1)
        self._update_grid()

    def _goto_today(self):
        self._view_date = date.today().replace(day=1)
        if self.selection_mode == "single":
            self.selected_date = date.today()
        # In range mode, maybe just show today but don't select? Or select start?
        # Let's just view today.
        self._update_grid()

    def _confirm(self):
        if self.selection_mode == "single":
            if self.selected_date:
                self.destroy()
        else:
            if self.start_date and self.end_date:
                self.destroy()
            else:
                # Allow single day range? Sure, start=end
                if self.start_date:
                    self.end_date = self.start_date
                    self.destroy()