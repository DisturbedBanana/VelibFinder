import tkinter as tk
from tkinter import ttk, messagebox
from velib_fetcher import VelibFetcher
import json
from datetime import datetime

class VelibApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Velib Station Finder - Lucas Guichard")
        self.root.geometry("1000x600")  # Made window wider
        
        # Configure dark theme colors
        self.setup_dark_theme()
        
        # Initialize the fetcher
        self.fetcher = VelibFetcher()
        self.stations_data = None
        
        # Create the main frame
        self.main_frame = ttk.Frame(root, padding="10", style='Dark.TFrame')
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create the search frame
        self.create_search_frame()
        
        # Create the results frame
        self.create_results_frame()
        
        # Create the status bar
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(root, textvariable=self.status_var, relief=tk.SUNKEN, style='Dark.TLabel')
        self.status_bar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Configure the style for the treeview
        self.style = ttk.Style()
        self.style.configure("Treeview", rowheight=28, font=('Segoe UI', 10))
        self.style.configure("Treeview.Heading", font=('Segoe UI', 10, 'bold'))
        
        # Initial fetch
        self.fetch_data()

    def setup_dark_theme(self):
        """Configure the dark theme colors and styles"""
        # Softer dark theme color palette
        self.colors = {
            'bg_dark': '#2b2b2b',
            'bg_medium': '#3c3c3c',
            'bg_light': '#4a4a4a',
            'text_primary': '#e0e0e0',
            'text_secondary': '#b8b8b8',
            'accent_blue': '#5dade2',
            'accent_green': '#58d68d',
            'accent_red': '#ec7063',
            'accent_orange': '#f39c12',
            'border': '#555555',
            'hover': '#4a4a4a',
            'selection': '#5dade2'
        }
        
        # Configure root window
        self.root.configure(bg=self.colors['bg_dark'])
        
        # Configure ttk styles
        style = ttk.Style()
        style.theme_use('clam')  # Use clam theme as base
        
        # Configure main styles
        style.configure('Dark.TFrame', background=self.colors['bg_dark'])
        style.configure('Dark.TLabel', background=self.colors['bg_dark'], foreground=self.colors['text_primary'])
        style.configure('Dark.TButton', 
                       background=self.colors['bg_medium'], 
                       foreground=self.colors['text_primary'],
                       borderwidth=1,
                       focuscolor=self.colors['accent_blue'])
        
        # Configure Treeview
        style.configure('Dark.Treeview',
                       background=self.colors['bg_medium'],
                       foreground=self.colors['text_primary'],
                       fieldbackground=self.colors['bg_medium'],
                       borderwidth=0,
                       rowheight=28,
                       font=('Segoe UI', 10))
        
        style.configure('Dark.Treeview.Heading',
                       background=self.colors['bg_light'],
                       foreground=self.colors['text_primary'],
                       borderwidth=0,
                       font=('Segoe UI', 10, 'bold'))
        
        # Configure LabelFrame
        style.configure('Dark.TLabelframe',
                       background=self.colors['bg_dark'],
                       foreground=self.colors['text_primary'],
                       borderwidth=1,
                       bordercolor=self.colors['border'])
        
        style.configure('Dark.TLabelframe.Label',
                       background=self.colors['bg_dark'],
                       foreground=self.colors['text_primary'])
        
        # Configure Entry
        style.configure('Dark.TEntry',
                       fieldbackground=self.colors['bg_medium'],
                       foreground=self.colors['text_primary'],
                       borderwidth=1,
                       bordercolor=self.colors['border'])
        
        # Configure Scrollbar
        style.configure('Dark.Vertical.TScrollbar',
                       background=self.colors['bg_medium'],
                       troughcolor=self.colors['bg_dark'],
                       borderwidth=0,
                       arrowcolor=self.colors['text_secondary'])
        
        # Configure Status bar
        style.configure('Dark.TLabel',
                       background=self.colors['bg_light'],
                       foreground=self.colors['text_primary'])

    def create_search_frame(self):
        search_frame = ttk.LabelFrame(self.main_frame, text="Search", padding="5", style='Dark.TLabelframe')
        search_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Search entry
        ttk.Label(search_frame, text="Station Name:", style='Dark.TLabel').grid(row=0, column=0, padx=5)
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=40, style='Dark.TEntry')
        self.search_entry.grid(row=0, column=1, padx=5)
        self.search_entry.bind('<Return>', lambda e: self.search_stations())
        
        # Search button
        ttk.Button(search_frame, text="Search", command=self.search_stations, style='Dark.TButton').grid(row=0, column=2, padx=5)
        
        # Refresh button
        ttk.Button(search_frame, text="Refresh Data", command=self.fetch_data, style='Dark.TButton').grid(row=0, column=3, padx=5)

    def create_results_frame(self):
        # Create a frame for the results
        results_frame = ttk.LabelFrame(self.main_frame, text="Station Information", padding="5", style='Dark.TLabelframe')
        results_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Create a treeview for the results
        self.tree = ttk.Treeview(results_frame, columns=("name", "ebikes", "mechanical", "status"), 
                                 show="headings", style='Dark.Treeview')
        
        # Define headings
        self.tree.heading("name", text="Station Name")
        self.tree.heading("ebikes", text="E-Bikes")
        self.tree.heading("mechanical", text="Mechanical")
        self.tree.heading("status", text="Status")
        
        # Define columns
        self.tree.column("name", width=400)
        self.tree.column("ebikes", width=100)
        self.tree.column("mechanical", width=100)
        self.tree.column("status", width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.tree.yview, style='Dark.Vertical.TScrollbar')
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Grid the treeview and scrollbar
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Bind double-click event
        self.tree.bind('<Double-1>', self.show_station_details)
        
        # Configure tag colors for dark theme
        # Removed background colors for cleaner look
        self.tree.tag_configure('active', foreground=self.colors['accent_green'])
        self.tree.tag_configure('inactive', foreground=self.colors['accent_red'])

    def fetch_data(self):
        self.status_var.set("Fetching data...")
        self.root.update()
        
        data = self.fetcher.get_stations()
        if data and "results" in data:
            self.stations_data = data["results"]
            self.update_station_list()
            self.status_var.set(f"Data updated at {datetime.now().strftime('%H:%M:%S')}")
        else:
            messagebox.showerror("Error", "Failed to fetch data from Velib API")
            self.status_var.set("Error fetching data")

    def update_station_list(self, stations=None):
        # Clear the treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # If no stations provided, use all stations
        if stations is None and self.stations_data:
            stations = self.stations_data
        
        # Add stations to the treeview
        for station in stations:
            is_active = station.get("is_installed") and station.get("is_renting")
            status = "Active" if is_active else "Inactive"
            tag = 'active' if is_active else 'inactive'
            
            self.tree.insert("", tk.END, values=(
                station.get("name", "Unknown"),
                station.get("ebike", 0),
                station.get("mechanical", 0),
                status
            ), tags=(tag,))

    def search_stations(self):
        search_term = self.search_var.get().lower()
        if not search_term:
            self.update_station_list()
            return
        
        if not self.stations_data:
            messagebox.showinfo("Info", "No data available. Please refresh first.")
            return
        
        # Filter stations
        filtered_stations = [
            station for station in self.stations_data
            if search_term in station.get("name", "").lower()
        ]
        
        self.update_station_list(filtered_stations)
        self.status_var.set(f"Found {len(filtered_stations)} matching stations")

    def create_bike_list(self, parent, bikes, title):
        """Create a frame showing a list of bikes"""
        frame = ttk.LabelFrame(parent, text=f"{title} ({len(bikes)} bikes)", padding="5", style='Dark.TLabelframe')
        frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Create a treeview for the bikes
        tree = ttk.Treeview(frame, columns=("number", "type", "status"), 
                           show="headings", height=min(6, max(3, len(bikes))), style='Dark.Treeview')
        
        # Define headings
        tree.heading("number", text="Bike Number")
        tree.heading("type", text="Type")
        tree.heading("status", text="Status")
        
        # Define columns
        tree.column("number", width=150)
        tree.column("type", width=120)
        tree.column("status", width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview, style='Dark.Vertical.TScrollbar')
        tree.configure(yscrollcommand=scrollbar.set)
        
        # Grid the treeview and scrollbar
        tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Configure grid weights
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
        
        # Add bikes to the treeview with color coding
        for bike in bikes:
            bike_type = bike.get("type", "Unknown")
            status = bike.get("status", "Unknown")
            
            # Set tag based on bike type
            tag = 'ebike' if bike_type == "E-Bike" else 'mechanical'
            
            tree.insert("", tk.END, values=(
                bike.get("number", "Unknown"),
                bike_type,
                status
            ), tags=(tag,))
        
        # Configure tag colors for dark theme
        tree.tag_configure('ebike', background=self.colors['accent_blue'], foreground=self.colors['text_primary'])
        tree.tag_configure('mechanical', background=self.colors['bg_light'], foreground=self.colors['text_primary'])
        
        return frame

    def show_station_details(self, event):
        # Get selected item
        item = self.tree.selection()[0]
        station_name = self.tree.item(item)["values"][0]
        
        # Find the full station data
        station = next((s for s in self.stations_data if s.get("name") == station_name), None)
        if station:
            # Create a new window for details
            details_window = tk.Toplevel(self.root)
            details_window.title(f"Station Details - {station_name} - Lucas Guichard")
            details_window.geometry("700x600")
            
            # Configure dark theme for details window
            details_window.configure(bg=self.colors['bg_dark'])
            
            # Main info frame
            main_frame = ttk.Frame(details_window, padding="10", style='Dark.TFrame')
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Station name and status
            name_label = tk.Label(main_frame, text=f"Station: {station.get('name', 'Unknown')}", 
                                 font=('Segoe UI', 16, 'bold'), 
                                 bg=self.colors['bg_dark'], fg=self.colors['text_primary'])
            name_label.pack(pady=5)
            
            # Station code
            code_label = tk.Label(main_frame, text=f"Station Code: {station.get('stationcode', 'Unknown')}", 
                                 font=('Segoe UI', 11), 
                                 bg=self.colors['bg_dark'], fg=self.colors['text_secondary'])
            code_label.pack(pady=2)
            
            # Status indicators
            status_frame = ttk.Frame(main_frame, style='Dark.TFrame')
            status_frame.pack(fill=tk.X, pady=10)
            
            # Create status indicators with text and colors
            is_installed = station.get('is_installed')
            is_renting = station.get('is_renting')
            is_returning = station.get('is_returning')
            
            installed_color = self.colors['accent_green'] if is_installed else self.colors['accent_red']
            renting_color = self.colors['accent_green'] if is_renting else self.colors['accent_red']
            returning_color = self.colors['accent_green'] if is_returning else self.colors['accent_red']
            
            tk.Label(status_frame, 
                    text=f"Installed: {'Yes' if is_installed else 'No'}",
                    fg=installed_color, bg=self.colors['bg_dark'], font=('Segoe UI', 11)).pack(side=tk.LEFT, padx=10)
            tk.Label(status_frame, 
                    text=f"Renting: {'Yes' if is_renting else 'No'}",
                    fg=renting_color, bg=self.colors['bg_dark'], font=('Segoe UI', 11)).pack(side=tk.LEFT, padx=10)
            tk.Label(status_frame, 
                    text=f"Returning: {'Yes' if is_returning else 'No'}",
                    fg=returning_color, bg=self.colors['bg_dark'], font=('Segoe UI', 11)).pack(side=tk.LEFT, padx=10)
            
            # Bike summary frame
            summary_frame = ttk.LabelFrame(main_frame, text="Bike Summary", padding="5", style='Dark.TLabelframe')
            summary_frame.pack(fill=tk.X, pady=5)
            
            # Bike counts
            ebike_count = station.get("ebike", 0)
            mechanical_count = station.get("mechanical", 0)
            capacity = station.get("capacity", 0)
            total_bikes = ebike_count + mechanical_count
            
            summary_text = f"E-Bikes: {ebike_count} | Mechanical: {mechanical_count} | Total: {total_bikes}/{capacity}"
            summary_label = tk.Label(summary_frame, text=summary_text, font=('Segoe UI', 12), 
                                   bg=self.colors['bg_dark'], fg=self.colors['text_primary'])
            summary_label.pack(pady=5)
            
            # Bike information
            bikes_frame = ttk.LabelFrame(main_frame, text="Individual Bikes", padding="5", style='Dark.TLabelframe')
            bikes_frame.pack(fill=tk.BOTH, expand=True, pady=10)
            
            # Show individual bikes if available
            if "bikes" in station:
                bikes = station["bikes"]
                if bikes:
                    # Separate e-bikes and mechanical bikes
                    ebikes = [b for b in bikes if b.get("type") == "E-Bike"]
                    mechanical = [b for b in bikes if b.get("type") == "Mechanical"]
                    
                    # Create bike lists
                    if ebikes:
                        self.create_bike_list(bikes_frame, ebikes, "E-Bikes")
                    if mechanical:
                        self.create_bike_list(bikes_frame, mechanical, "Mechanical Bikes")
                    
                    # Add note about generated bike numbers
                    note_frame = ttk.Frame(main_frame, style='Dark.TFrame')
                    note_frame.pack(fill=tk.X, pady=5)
                    note_label = tk.Label(note_frame, 
                                        text="Note: Bike numbers are generated based on station data. E-bikes start with 'E', mechanical bikes with 'M'.",
                                        font=('Segoe UI', 10), fg=self.colors['text_secondary'], bg=self.colors['bg_dark'])
                    note_label.pack()
                else:
                    no_bikes_label = tk.Label(bikes_frame, text="No bike information available", 
                                            bg=self.colors['bg_dark'], fg=self.colors['text_secondary'], font=('Segoe UI', 11))
                    no_bikes_label.pack(pady=5)
            else:
                no_details_label = tk.Label(bikes_frame, text="No detailed bike information available", 
                                          bg=self.colors['bg_dark'], fg=self.colors['text_secondary'], font=('Segoe UI', 11))
                no_details_label.pack(pady=5)
            
            # Coordinates if available
            if "coordonnees_geo" in station:
                coords = station["coordonnees_geo"]
                coords_frame = ttk.Frame(main_frame, style='Dark.TFrame')
                coords_frame.pack(fill=tk.X, pady=5)
                coords_label = tk.Label(coords_frame, 
                                      text=f"Location: {coords.get('lat', 'N/A')}, {coords.get('lon', 'N/A')}",
                                      bg=self.colors['bg_dark'], fg=self.colors['text_secondary'], font=('Segoe UI', 10))
                coords_label.pack()
            
            # Last update time
            time_label = tk.Label(main_frame, 
                                text=f"Last updated: {datetime.now().strftime('%H:%M:%S')}",
                                bg=self.colors['bg_dark'], fg=self.colors['text_secondary'], font=('Segoe UI', 10))
            time_label.pack(pady=5)

def main():
    root = tk.Tk()
    app = VelibApp(root)
    root.mainloop()

if __name__ == "__main__":
    main() 