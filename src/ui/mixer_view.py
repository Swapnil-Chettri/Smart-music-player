import customtkinter as ctk

class MixerView(ctk.CTkFrame):
    def __init__(self, parent, audio_engine, **kwargs):
        super().__init__(parent, fg_color="#181818", corner_radius=15, border_width=1, border_color="#333", **kwargs)
        self.engine = audio_engine

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=10, pady=(15, 10))
        
        ctk.CTkLabel(header, text="🎚️ EQUALIZER", text_color="white", 
                     font=("Circular Std", 12, "bold")).pack(side="left")

        ctk.CTkButton(
            header, 
            text="Reset", 
            width=50, 
            height=20,
            fg_color="transparent", 
            text_color="#1DB954",  # Spotify Green
            hover_color="#222",
            font=("Arial", 11),
            command=self.reset_all
        ).pack(side="right")

        self.sliders_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.sliders_frame.pack(fill="both", expand=True, padx=10, pady=(0, 15))

        self.frequencies = ["60", "170", "310", "600", "1K", "3K", "6K", "12K", "14K", "16K"]
        self.sliders = []

        for i, freq in enumerate(self.frequencies):
            band_col = ctk.CTkFrame(self.sliders_frame, fg_color="transparent")
            band_col.pack(side="left", fill="y", expand=True, padx=2)
            
            slider = ctk.CTkSlider(
                band_col, 
                from_=20, to=-20, 
                orientation="vertical",
                height=140,
                width=18,             
                progress_color="#1DB954", 
                button_color="white",     
                button_hover_color="#1ed760",
                fg_color="#404040",       
                command=lambda val, idx=i: self.on_slider_move(idx, val)
            )
            slider.set(0) 
            slider.pack(pady=(0, 5))
            self.sliders.append(slider)

            ctk.CTkLabel(
                band_col, 
                text=freq, 
                text_color="#888888", 
                font=("Consolas", 9)
            ).pack()

    def on_slider_move(self, band_index, value):
        gain = float(value)
        
        if self.engine:
            if hasattr(self.engine, 'set_eq_band'):
                self.engine.set_eq_band(band_index, gain)
            elif hasattr(self.engine, 'set_band_gain'):
                self.engine.set_band_gain(band_index, gain)

    def update_sliders_from_preset(self, preset_values):
        if len(preset_values) != 10: 
            return
        
        for i, slider in enumerate(self.sliders):
            slider.set(preset_values[i])

    def reset_all(self):
        self.update_sliders_from_preset([0]*10)
        
        if self.engine:
            self.engine.reset_eq()