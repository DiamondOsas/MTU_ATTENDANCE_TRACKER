import customtkinter as ctk
import os
import shutil
import json
from pathlib import Path
from tkinter import messagebox

class RevertDBWindow(ctk.CTkToplevel):
    """
    Window to select and restore a database backup from AppData/MTU_BACKUP.
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Restore Database Backup")
        self.geometry("400x500")
        self.resizable(False, False)
        
        # Title
        self.title_label = ctk.CTkLabel(self, text="Select Backup to Restore", font=ctk.CTkFont(size=18, weight="bold"))
        self.title_label.pack(pady=20)
        
        # Scrollable list for backups
        self.backup_list_frame = ctk.CTkScrollableFrame(self, width=350, height=300)
        self.backup_list_frame.pack(pady=10, padx=20)
        
        self.selected_backup_path = None
        self.buttons = [] # Keep references
        
        self.load_backups()
        
        # Restore Button
        self.restore_button = ctk.CTkButton(
            self, 
            text="Restore Selected Backup", 
            state="disabled", 
            command=self.restore_backup_handler
        )
        self.restore_button.pack(pady=20)
        
    def get_backup_root(self) -> Path:
        """
        Returns the path to the MTU_BACKUP directory in AppData.
        """
        if os.name == 'nt':
            app_data = os.getenv('APPDATA')
            if not app_data:
                app_data = Path.home() / "AppData" / "Roaming"
            else:
                app_data = Path(app_data)
        else:
            app_data = Path.home() / ".config"
            
        return app_data / "MTU_BACKUP"

    def load_backups(self):
        """
        Populates the scrollable frame with available backups.
        """
        backup_root = self.get_backup_root()
        if not backup_root.exists():
            ctk.CTkLabel(self.backup_list_frame, text="No backups found.").pack()
            return

        # List directories (YYYY-MM-DD) and sort descending
        try:
            backups = sorted(
                [d for d in backup_root.iterdir() if d.is_dir()], 
                key=lambda x: x.name, 
                reverse=True
            )
        except Exception as e:
            ctk.CTkLabel(self.backup_list_frame, text=f"Error loading backups: {e}").pack()
            return
        
        if not backups:
             ctk.CTkLabel(self.backup_list_frame, text="No backups found.").pack()
             return

        for backup_dir in backups:
            date_name = backup_dir.name
            display_text = date_name
            
            # Try to read extra info from json
            json_path = backup_dir / "backup_info.json"
            if json_path.exists():
                try:
                    with open(json_path, "r") as f:
                        info = json.load(f)
                        if "timestamp" in info:
                            display_text += f"  ({info['timestamp']})"
                except:
                    pass
            
            # Create a button for each backup
            # We use a closure/default arg to capture the specific backup_dir
            btn = ctk.CTkButton(
                self.backup_list_frame, 
                text=display_text, 
                fg_color="transparent", 
                border_width=1, 
                text_color=("gray10", "gray90"), 
                anchor="w",
                command=lambda p=backup_dir: self.select_backup(p)
            )
            btn.pack(fill="x", pady=2)
            self.buttons.append(btn)

    def select_backup(self, backup_path):
        """
        Highlights the selected backup and enables the restore button.
        """
        self.selected_backup_path = backup_path
        self.restore_button.configure(state="normal", text=f"Restore: {backup_path.name}")
        
        # Optional: Update button visual states to show selection
        for btn in self.buttons:
            if btn.cget("text").startswith(backup_path.name):
                btn.configure(fg_color=("gray75", "gray25"))
            else:
                btn.configure(fg_color="transparent")

    def restore_backup_handler(self):
        """
        Restores the selected backup to the 'db' folder.
        """
        if not self.selected_backup_path:
            return
            
        confirm = messagebox.askyesno(
            "Confirm Restore", 
            f"Are you sure you want to restore data from {self.selected_backup_path.name}?\n\n"
            "Current data in the 'db' folder will be PERMANENTLY overwritten."
        )
        
        if confirm:
            try:
                # Paths
                current_db = Path("db")
                backup_db_source = self.selected_backup_path / "db"
                
                if not backup_db_source.exists():
                    messagebox.showerror("Error", "Backup is corrupted: 'db' folder missing inside backup.")
                    return
                
                # 1. Remove current 'db' folder
                if current_db.exists():
                    shutil.rmtree(current_db)
                
                # 2. Copy backup 'db' folder to current location
                shutil.copytree(backup_db_source, current_db)
                
                messagebox.showinfo(
                    "Restore Successful", 
                    "Database has been restored.\nPlease restart the application to ensure all changes take effect."
                )
                self.destroy()
                
            except Exception as e:
                messagebox.showerror("Restore Failed", f"An error occurred:\n{e}")
