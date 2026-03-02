import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk  
import os
from src.database.json_db import JsonDB
from src.audio_engine.player import AudioEngine
from src.ui.chat_widget import ChatWidget
from src.ui.mixer_view import MixerView
from rapidfuzz import process, fuzz

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class App(ctk.CTk): 
    def __init__(self):
        super().__init__()
        
        self.current_song_path = None
        self.title("Smart Music Player")
        self.geometry("450x800") 
        
        self.engine = AudioEngine()
        self.db = JsonDB()
        
        saved_vol = self.db.get_setting("volume", 80)
        self.engine.set_volume(saved_vol)

        self.playlist_paths = []
        self.icons = {}

        self.create_menu()
        
        
        self.art_frame = ctk.CTkFrame(self, fg_color="#252525", width=300, height=250, corner_radius=20)
        self.art_frame.pack(pady=20)
        self.art_frame.pack_propagate(False) 
        ctk.CTkLabel(self.art_frame, text="🎵", text_color="#444", font=("Arial", 80)).pack(expand=True)

        
        self.lbl_title = ctk.CTkLabel(self, text="No Song Loaded", text_color="white", 
                                      font=("Segoe UI", 20, "bold"))
        self.lbl_title.pack(pady=(0, 5))
        
        self.lbl_artist = ctk.CTkLabel(self, text="Open File to Begin", text_color="#888888", 
                                       font=("Segoe UI", 14))
        self.lbl_artist.pack()

        self.btn_open = ctk.CTkButton(
            self, 
            text="OPEN FOLDER", 
            command=self.open_dir, 
            fg_color="#1DB954",         
            hover_color="#1ed760",      
            text_color="black",         
            font=("Circular Std", 12, "bold"), 
            corner_radius=25,           
            height=40
        )
        self.btn_open.pack(pady=(15, 10))

        
        self.time_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.time_frame.pack(fill="x", padx=25)
        
        self.lbl_current = ctk.CTkLabel(self.time_frame, text="00:00", text_color="#888888", font=("Consolas", 12))
        self.lbl_current.pack(side=tk.LEFT)
        
        self.lbl_total = ctk.CTkLabel(self.time_frame, text="00:00", text_color="#888888", font=("Consolas", 12))
        self.lbl_total.pack(side=tk.RIGHT)
       
        self.configure(fg_color="#121212") 

        self.slider = ctk.CTkSlider(
            self, 
            from_=0, 
            to=100, 
            progress_color="#1DB954",   
            button_color="white",       
            button_hover_color="#1ed760", 
            fg_color="#535353",         
            height=16
        )
        self.slider.pack(fill="x", padx=25, pady=5)
        self.slider.bind("<Button-1>", self.on_slider_press)
        self.slider.bind("<ButtonRelease-1>", self.on_slider_release)
        self.is_dragging = False

        
        self.controls_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.controls_frame.pack(pady=15, anchor="center") 

        self.create_icon_btn(self.controls_frame, "Prev", self.play_prev, "prev")
        self.btn_play = self.create_icon_btn(self.controls_frame, "Play", self.toggle_play, "play")
        self.create_icon_btn(self.controls_frame, "Next", self.play_next, "next")

        ctk.CTkLabel(
            self.controls_frame, 
            text="Vol", 
            text_color="#888888", 
            font=("Arial", 10, "bold")
        ).pack(side="left", padx=(25, 2)) 

       
        self.vol_slider = ctk.CTkSlider(
            self.controls_frame, 
            from_=0, 
            to=150, 
            width=80, 
            progress_color="#1DB954",  
            button_color="white",       
            button_hover_color="#1ed760",
            command=self.set_volume
        )
        self.vol_slider.set(self.db.get_setting("volume", 80))
        self.vol_slider.pack(side="left", padx=2)

        ctk.CTkButton(
            self.controls_frame, 
            text="EQ", 
            fg_color="#333333", 
            hover_color="#444444",
            width=35, 
            height=25, 
            font=("Arial", 10, "bold"),
            command=self.toggle_mixer
        ).pack(side="left", padx=(10, 0))

        self.effects_frame = ctk.CTkScrollableFrame(self, orientation="horizontal", height=40, fg_color="transparent")
        self.effects_frame.pack(fill="x", padx=20, pady=5)
        
        self.create_effect_btn("Lo-fi", self.apply_lofi_ui)
        self.create_effect_btn("Bass Boost", self.apply_bass_ui)
        self.create_effect_btn("Reverb", self.apply_reverb_ui)
        self.create_effect_btn("Slowed", lambda: self.engine.set_rate(0.8))
        self.create_effect_btn("Speed", lambda: self.engine.set_rate(1.2))
        self.create_effect_btn("3D Audio", self.apply_3d_ui)
        self.create_effect_btn("Reset", self.reset_eq_ui)

        self.playlist_frame = ctk.CTkFrame(self, fg_color="#1E1E1E")
        self.playlist_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.playlist_box = tk.Listbox(self.playlist_frame, bg="#252525", fg="#DDDDDD", 
                                       selectbackground="#6200EA", selectforeground="white", 
                                       relief="flat", borderwidth=0, height=6)
        self.playlist_box.pack(side=tk.LEFT, fill="both", expand=True)
        
        scrollbar = tk.Scrollbar(self.playlist_frame)
        scrollbar.pack(side=tk.RIGHT, fill="y")
        self.playlist_box.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.playlist_box.yview)

        self.playlist_box.bind('<Double-1>', self.play_selected)

        self.mixer = MixerView(self, self.engine)
        self.mixer_visible = False
        
        self.chat = ChatWidget(self, self)
        self.chat.pack(side=tk.BOTTOM, fill="x", padx=10, pady=10)

        self.is_playing = False
        self.update_loop() 
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.load_library()

    def create_menu(self):
        
        menubar = tk.Menu(self)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open File", command=self.open_file)
        file_menu.add_command(label="Open Directory", command=self.open_dir)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_close)
        menubar.add_cascade(label="File", menu=file_menu)
        self.config(menu=menubar)

    def create_icon_btn(self, parent, text, command, icon_key):
        
        if icon_key == "play":
            btn = ctk.CTkButton(
                parent, 
                text="▶",            
                width=60, 
                height=60,           
                fg_color="white",    
                text_color="black",  
                hover_color="#DDDDDD",
                corner_radius=30,   
                font=("Arial", 24),
                command=command
            )
        else:
            
            btn = ctk.CTkButton(
                parent, 
                text="⏮" if icon_key == "prev" else "⏭", 
                width=40, 
                height=40, 
                fg_color="transparent",
                text_color="#B3B3B3", 
                hover_color="#222222",
                font=("Arial", 20),
                command=command
            )
            
        btn.pack(side=tk.LEFT, padx=10)
        return btn

    def create_effect_btn(self, text, command):
        btn = ctk.CTkButton(
            self.effects_frame, 
            text=text, 
            width=70, 
            height=32,
            fg_color="transparent",      
            border_width=1,              
            border_color="#777777",      
            text_color="white",
            hover_color="#282828",      
            corner_radius=16,            
            font=("Arial", 11, "bold"),
            command=command
        )
        btn.pack(side=tk.LEFT, padx=4)

    def toggle_mixer(self):
        if self.mixer_visible:
            self.mixer.pack_forget()
            self.mixer_visible = False
        else:
            
            self.mixer.pack(after=self.controls_frame, fill="x", padx=10, pady=10)
            self.mixer_visible = True

    def smart_search_and_play(self, query):
        print(f"🧠 AI Searching for: {query}")
        query = query.lower().strip()
        if not query: return
        all_items = list(self.playlist_box.get(0, tk.END))
        if not all_items: return

        result = process.extractOne(query, all_items, scorer=fuzz.WRatio)
        if result:
            match_text, score, index = result
            if score > 65:
                self.playlist_box.selection_clear(0, tk.END)
                self.playlist_box.selection_set(index)
                self.playlist_box.see(index)
                target = self.playlist_paths[index]
                
                if os.path.exists(target): self.load_song(target)
                else: self.play_stream_thread(target)
                self.chat.log(f"Matched: {match_text} ({int(score)}%)")
            else:
                self.chat.speak(f"I'm not sure which song you mean by {query}")

    def save_library(self):
        self.db.data["library"] = self.playlist_paths
        self.db.save() 

    def load_library(self):
        paths = self.db.data.get("library", [])
        self.playlist_box.delete(0, tk.END)
        self.playlist_paths = []
        for path in paths:
            if os.path.exists(path) or path.startswith("http"):
                self.playlist_paths.append(path)
                self.playlist_box.insert(tk.END, os.path.basename(path))

    def open_file(self):
        path = filedialog.askopenfilename(filetypes=[("Audio", "*.mp3 *.wav *.flac *.m4a *.ogg")])
        if path:
            self.add_to_playlist([path])
            self.load_song(path)

    def open_dir(self):
        directory = filedialog.askdirectory()
        if directory:
            audio_files = [os.path.join(directory, f) for f in os.listdir(directory) 
                           if f.lower().endswith(('.mp3', 'wav', '.flac', '.ogg', 'm4a'))]
            if audio_files:
                self.add_to_playlist(audio_files)
                self.load_song(audio_files[0])
            else:
                messagebox.showinfo("Info", "No audio files found in folder.")
        self.save_library()

    def add_to_playlist(self, paths):
        self.playlist_paths.clear()
        self.playlist_box.delete(0, tk.END)
        for path in paths:
            self.playlist_paths.append(path)
            self.playlist_box.insert(tk.END, os.path.basename(path))
    
    def play_selected(self, event):
        selection = self.playlist_box.curselection()
        if selection:
            self.load_song(self.playlist_paths[selection[0]])

    def play_next(self):
        if not self.playlist_paths: return
        try:
            curr = self.playlist_paths.index(self.current_song_path) if self.current_song_path in self.playlist_paths else -1
            next_idx = (curr + 1) % len(self.playlist_paths)
        except ValueError: next_idx = 0
        self.load_song(self.playlist_paths[next_idx])

    def play_prev(self):
        if not self.playlist_paths: return
        try:
            curr = self.playlist_paths.index(self.current_song_path) if self.current_song_path in self.playlist_paths else -1
            prev_idx = (curr - 1) % len(self.playlist_paths)
        except ValueError: prev_idx = 0
        self.load_song(self.playlist_paths[prev_idx])

    def load_song(self, path):
        self.engine.stop()
        self.current_song_path = path
        self.slider.set(0)
        self.lbl_current.configure(text="00:00")
        self.lbl_total.configure(text="--:--")
        self.lbl_title.configure(text=os.path.basename(path))
        
        self.engine.load_track(path)
        self.db.add_song_to_library(path)
        self.db.update_setting("last_played", path)

        try:
            idx = self.playlist_paths.index(path)
            self.playlist_box.selection_clear(0, tk.END)
            self.playlist_box.selection_set(idx)
            self.playlist_box.see(idx)
        except ValueError: pass

        self.engine.play()
        self.is_playing = True
        self.update_play_icon()
        self.after(500, self.sync_duration)

    def toggle_play(self):
        if not self.current_song_path: return
        if self.is_playing:
            self.engine.pause()
            self.is_playing = False
        else:
            self.engine.play()
            self.is_playing = True
        self.update_play_icon()
    
    def sync_duration(self):
        total_ms = self.engine.get_length()
        if total_ms > 0:
            self.slider.configure(to=total_ms)
            self.lbl_total.configure(text=self.format_time(total_ms))
        else:
            self.after(500, self.sync_duration)
    
    def set_volume(self, val):
        volume = int(val)
        self.engine.set_volume(volume)
        self.db.update_setting("volume", volume)

    def update_play_icon(self):
        if self.is_playing:
            self.btn_play.configure(text="⏸") 
        else:
            self.btn_play.configure(text="▶")

    def apply_lofi_ui(self):
        self.engine.apply_lofi_preset()
        if hasattr(self.mixer, 'update_sliders_from_preset'):
            self.mixer.update_sliders_from_preset([-2, 0, 4, 4, 2, -5, -10, -15, -15, -18])

    def apply_bass_ui(self):
        self.engine.apply_bass_boost_preset()
        if hasattr(self.mixer, 'update_sliders_from_preset'):
            self.mixer.update_sliders_from_preset([12, 8, 3, 0, -2, -2, -2, -2, -2 , -2])

    def apply_reverb_ui(self):
        if not self.current_song_path: return
        self.configure(cursor="watch")
        self.update()
        self.engine.apply_reverb_effect(self.current_song_path)
        self.configure(cursor="")
        self.slider.configure(to=self.engine.get_length())

    def apply_3d_ui(self):
        if not self.current_song_path: return
        self.configure(cursor="watch")
        self.update()
        self.engine.apply_3d_effect(self.current_song_path)
        self.configure(cursor="")
        self.slider.configure(to=self.engine.get_length())

    def reset_eq_ui(self):
        self.engine.reset_eq()
        self.engine.set_rate(1.0)
        if hasattr(self.mixer, 'update_sliders_from_preset'):
            self.mixer.update_sliders_from_preset([0]*10)

    def on_slider_press(self, event):
        self.is_dragging = True

    def on_slider_release(self, event):
        val = self.slider.get()
        self.engine.set_time(int(val))
        self.after(200, lambda: setattr(self, 'is_dragging', False))

    def update_loop(self):
        if self.is_playing and not self.is_dragging:
            curr_ms = self.engine.get_time()
            total_ms = self.slider.cget("to") 

            if curr_ms >= 0:
                self.slider.set(curr_ms)
                self.lbl_current.configure(text=self.format_time(curr_ms))

            if total_ms > 2000 and curr_ms >= (total_ms - 1500):
                print("🎵 Song finished.")
                self.is_playing = False
                self.after(100, self.play_next)
        
        self.after(500, self.update_loop)

    def format_time(self, ms):
        if ms < 0: ms = 0
        seconds = int(ms / 1000)
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02}:{seconds:02}"

    def on_close(self):
        self.engine.shutdown()
        self.destroy()

if __name__ == "__main__":
    app = App()
    app.mainloop()