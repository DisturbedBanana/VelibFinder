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
        
        # Initialize the fetcher
        self.fetcher = VelibFetcher()
        self.stations_data = None
        
        # Create the main frame
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create the search frame
        self.create_search_frame()
        
        # Create the results frame
        self.create_results_frame()
        
        # Create the status bar
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(root, textvariable=self.status_var, relief=tk.SUNKEN)
        self.status_bar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Configure the style for the treeview
        self.style = ttk.Style()
        self.style.configure("Treeview", rowheight=25)
        
        # Initial fetch
        self.fetch_data()

    def create_search_frame(self):
        search_frame = ttk.LabelFrame(self.main_frame, text="Search", padding="5")
        search_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Search entry
        ttk.Label(search_frame, text="Station Name:").grid(row=0, column=0, padx=5)
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=40)
        self.search_entry.grid(row=0, column=1, padx=5)
        self.search_entry.bind('<Return>', lambda e: self.search_stations())
        
        # Search button
        ttk.Button(search_frame, text="Search", command=self.search_stations).grid(row=0, column=2, padx=5)
        
        # Refresh button
        ttk.Button(search_frame, text="Refresh Data", command=self.fetch_data).grid(row=0, column=3, padx=5)

    def create_results_frame(self):
        # Create a frame for the results
        results_frame = ttk.LabelFrame(self.main_frame, text="Station Information", padding="5")
        results_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Create a treeview for the results
        self.tree = ttk.Treeview(results_frame, columns=("name", "ebikes", "mechanical", "status"), show="headings")
        
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
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Grid the treeview and scrollbar
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Bind double-click event
        self.tree.bind('<Double-1>', self.show_station_details)
        
        # Configure tag colors
        self.tree.tag_configure('active', background='#e6ffe6')  # Light green
        self.tree.tag_configure('inactive', background='#ffe6e6')  # Light red

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
        frame = ttk.LabelFrame(parent, text=title, padding="5")
        frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Create a treeview for the bikes
        tree = ttk.Treeview(frame, columns=("number", "type", "status"), show="headings", height=4)
        
        # Define headings
        tree.heading("number", text="Bike Number")
        tree.heading("type", text="Type")
        tree.heading("status", text="Status")
        
        # Define columns
        tree.column("number", width=100)
        tree.column("type", width=100)
        tree.column("status", width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        # Grid the treeview and scrollbar
        tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Add bikes to the treeview
        for bike in bikes:
            tree.insert("", tk.END, values=(
                bike.get("number", "Unknown"),
                bike.get("type", "Unknown"),
                bike.get("status", "Unknown")
            ))
        
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
            details_window.geometry("600x500")
            
            # Main info frame
            main_frame = ttk.Frame(details_window, padding="10")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Station name and status
            ttk.Label(main_frame, text=f"Station: {station.get('name', 'Unknown')}", 
                     font=('Arial', 12, 'bold')).pack(pady=5)
            
            # Status indicators
            status_frame = ttk.Frame(main_frame)
            status_frame.pack(fill=tk.X, pady=5)
            
            # Create status indicators with text and colors
            is_installed = station.get('is_installed')
            is_renting = station.get('is_renting')
            is_returning = station.get('is_returning')
            
            ttk.Label(status_frame, 
                     text=f"Installed: {'Yes' if is_installed else 'No'}",
                     foreground='green' if is_installed else 'red').pack(side=tk.LEFT, padx=10)
            ttk.Label(status_frame, 
                     text=f"Renting: {'Yes' if is_renting else 'No'}",
                     foreground='green' if is_renting else 'red').pack(side=tk.LEFT, padx=10)
            ttk.Label(status_frame, 
                     text=f"Returning: {'Yes' if is_returning else 'No'}",
                     foreground='green' if is_returning else 'red').pack(side=tk.LEFT, padx=10)
            
            # Bike information
            bikes_frame = ttk.LabelFrame(main_frame, text="Bike Information", padding="5")
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
                else:
                    ttk.Label(bikes_frame, text="No bike information available").pack(pady=5)
            else:
                ttk.Label(bikes_frame, text="No detailed bike information available").pack(pady=5)
            
            # Total capacity
            capacity = station.get("capacity", 0)
            total_bikes = station.get("ebike", 0) + station.get("mechanical", 0)
            ttk.Label(main_frame, 
                     text=f"Total Capacity: {total_bikes}/{capacity} bikes").pack(pady=5)
            
            # Coordinates if available
            if "coordonnees_geo" in station:
                coords = station["coordonnees_geo"]
                ttk.Label(main_frame, 
                         text=f"Location: {coords.get('lat', 'N/A')}, {coords.get('lon', 'N/A')}").pack(pady=5)
            
            # Last update time
            ttk.Label(main_frame, 
                     text=f"Last updated: {datetime.now().strftime('%H:%M:%S')}").pack(pady=5)

def main():
    root = tk.Tk()
    app = VelibApp(root)
    root.mainloop()

if __name__ == "__main__":
    main() 