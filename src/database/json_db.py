import json
import os

class JsonDB:
    def __init__(self, filename="library.json"):
        
        self.path = filename
        
        
        self.data = self.load_db()

    def load_db(self):
        """Loads data from JSON and ensures it is a proper Dictionary."""
        
        if not os.path.exists(self.path) or os.stat(self.path).st_size == 0:
            return {"settings": {}, "library": []}

        try:
            with open(self.path, 'r') as f:
                data = json.load(f)
                
            if isinstance(data, list):
                print("⚠️ Warning: JSON was a list. Converting to dictionary...")
                return {"settings": {}, "library": data}
            
            if "settings" not in data: data["settings"] = {}
            if "library" not in data: data["library"] = []
            
            return data
            
        except (json.JSONDecodeError, Exception) as e:
            print(f"❌ Database Load Error: {e}")
            return {"settings": {}, "library": []}

    def save(self):
        """Saves the current self.data dictionary to the JSON file."""
        try:
            with open(self.path, 'w') as f:
                json.dump(self.data, f, indent=4)
        except Exception as e:
            print(f"❌ Database Save Error: {e}")

    def add_song_to_library(self, path):
        """Adds a song path to the library list if it's not already there."""
        if path not in self.data["library"]:
            self.data["library"].append(path)
            self.save() # Save changes immediately
            print(f"💾 Added to JSON: {os.path.basename(path)}")
            
    def get_setting(self, key, default=None):
        """Safely gets a setting from the 'settings' dictionary."""
        return self.data.get("settings", {}).get(key, default)

    def update_setting(self, key, value):
        """Updates a setting and saves to disk."""
        self.data["settings"][key] = value
        self.save()