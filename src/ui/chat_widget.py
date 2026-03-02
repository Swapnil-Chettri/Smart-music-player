import customtkinter as ctk
import tkinter as tk  
import threading
import os
import json
import queue
import sounddevice as sd
from vosk import Model, KaldiRecognizer
import pyttsx3

class ChatWidget(ctk.CTkFrame):
    def __init__(self, parent, app_instance):
        super().__init__(parent, fg_color="#181818", corner_radius=15, border_width=1, border_color="#333")
        self.app = app_instance
        
        self.model_path = r"C:\Users\SWAPNIL CHETTRI\Downloads\vosk-model-small-en-in-0.4\vosk-model-small-en-in-0.4"
        if self.model_path.lower().endswith('am'):
             self.model_path = os.path.dirname(self.model_path)

        self.model_exists = False
        if os.path.exists(self.model_path):
            try:
                self.model = Model(self.model_path)
                self.model_exists = True
                print("✅ OFFLINE AI MODEL LOADED")
            except Exception as e:
                print(f"❌ VOSK LOAD ERROR: {e}")
        
        self.audio_queue = queue.Queue()
        self.tts = pyttsx3.init()
        self.tts.setProperty('rate', 160)
     
        self.base_commands = [
            "play", "stop", "pause", "next", "previous", "back", "skip",
            "volume", "set", "bass", "boost", "reverb", "lofi", "3d audio", "zero", "ten",
            "twenty", "thirty", "forty", "fifty", "sixty", "seventy",
            "eighty", "ninety", "hundred", "one fifty"
        ]

        top_frame = ctk.CTkFrame(self, fg_color="transparent", height=20)
        top_frame.pack(fill="x", padx=15, pady=(10, 5))
        ctk.CTkLabel(top_frame, text="AI ASSISTANT", text_color="#1DB954", 
                     font=("Circular Std", 12, "bold")).pack(side="left")
        
        self.status_lbl = ctk.CTkLabel(top_frame, text="OFFLINE", text_color="#555", font=("Arial", 10))
        self.status_lbl.pack(side="right")

        self.display = ctk.CTkTextbox(
            self, 
            fg_color="#121212", 
            text_color="#DDDDDD", 
            font=("Consolas", 11),
            corner_radius=10,
            activate_scrollbars=True
        )
        self.display.pack(fill="both", expand=True, padx=10, pady=5)
        self.display.insert("0.0", "System: AI Initialized...\n")
        self.display.configure(state="disabled")

        input_frame = ctk.CTkFrame(self, fg_color="transparent")
        input_frame.pack(fill="x", padx=10, pady=10)

        self.entry = ctk.CTkEntry(
            input_frame, 
            placeholder_text="Type or Speak command...", 
            fg_color="#282828", 
            border_color="#444",
            text_color="white",
            height=35
        )
        self.entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.entry.bind("<Return>", self.on_text_send)

        self.btn_send = ctk.CTkButton(
            input_frame, 
            text="➤", 
            width=40, 
            height=35,
            fg_color="#1DB954", 
            hover_color="#1ed760",
            text_color="black",
            command=self.on_text_send
        )
        self.btn_send.pack(side="right")

        if self.model_exists:
            threading.Thread(target=self.background_listener, daemon=True).start()

    def log(self, text):
        self.display.configure(state="normal")
        self.display.insert("end", f"🤖 {text}\n")
        self.display.see("end")
        self.display.configure(state="disabled")

    def on_text_send(self, event=None):
        msg = self.entry.get().strip().lower()
        if not msg: return
        
        self.display.configure(state="normal")
        self.display.insert("end", f"You: {msg}\n")
        self.display.see("end")
        self.display.configure(state="disabled")
        
        self.entry.delete(0, "end")
        self.execute_brain(msg)

    def speak(self, text, restore_volume=True):
        try:
            captured_vol = self.app.vol_slider.get()
        except:
            captured_vol = 80 

        def tts_task():
            if restore_volume:
                self.app.after(0, lambda: self.app.engine.set_volume(20))
            
            try:
                local_engine = pyttsx3.init()
                local_engine.setProperty('rate', 160)
                local_engine.say(text)
                local_engine.runAndWait()
                local_engine.stop() 
            except Exception as e:
                print(f"TTS Error: {e}")
            finally:
                if restore_volume:
                    print(f"🔊 Restoring volume to {int(captured_vol)}")
                    self.app.after(0, lambda: self._force_restore(captured_vol))

        threading.Thread(target=tts_task, daemon=True).start()

    def _force_restore(self, vol):
        self.app.engine.set_volume(int(vol))
        self.app.vol_slider.set(vol)

    def audio_callback(self, indata, frames, time, status):
        self.audio_queue.put(bytes(indata))

    def background_listener(self):
        try:
            song_words = []
            try:
                all_items = self.app.playlist_box.get(0, tk.END)
                for song in all_items:
                    clean = "".join(e for e in song if e.isalnum() or e.isspace()).lower()
                    song_words.extend(clean.split())
            except:
                pass
            
            final_vocab = list(set(self.base_commands + song_words))
            vocab_json = json.dumps(final_vocab + ["[unk]"])

            device_info = sd.query_devices(None, 'input')
            samplerate = int(device_info['default_samplerate'])

            with sd.RawInputStream(samplerate=samplerate, blocksize=4000, dtype='int16', 
                                   channels=1, callback=self.audio_callback):
                
                rec = KaldiRecognizer(self.model, samplerate, vocab_json)
                self.app.after(0, lambda: self.status_lbl.configure(text="👂 LISTENING", text_color="#1DB954"))

                while True:
                    data = self.audio_queue.get()
                    if rec.AcceptWaveform(data):
                        result = json.loads(rec.Result())
                        text = result.get("text", "").lower()
                        if text:
                            print(f"AI Heard: {text}")
                            self.app.after(0, lambda cmd=text: self.execute_brain(cmd))
                            
        except Exception as e:
            print(f"🎤 Mic Error: {e}")
            self.app.after(0, lambda: self.status_lbl.configure(text="❌ MIC ERROR", text_color="red"))

    def execute_brain(self, cmd):
        self.log(f"Cmd: {cmd}")

        if "play" in cmd:
            query = cmd.replace("play", "").strip()
            if not query:
                self.app.toggle_play()
                self.speak("Toggling playback")
            else:
                self.app.smart_search_and_play(query)
                self.speak(f"Playing {query}")

        elif "volume" in cmd:
            vol = self.extract_volume(cmd)
            if vol is not None:
                self._force_restore(vol)
                self.speak(f"Volume {vol}", restore_volume=False)

        elif "pause" in cmd or "stop" in cmd:
            self.app.toggle_play()
            self.speak("Paused")
            
        elif "next" in cmd or "skip" in cmd:
            self.app.play_next()
            self.speak("Next track")

        elif "prev" in cmd or "back" in cmd:
            self.app.play_prev()
            self.speak("Previous track")
            
        elif "bass" in cmd:
            self.app.apply_bass_ui()
            self.speak("Bass Boosted")
        elif "lofi" in cmd:
            self.app.apply_lofi_ui()
            self.speak("Applying Lo-fi vibes")
        elif "reverb" in cmd:
            self.app.apply_reverb_ui()
            self.speak("Reverb enabled")
        elif "3d" in cmd:
            self.app.apply_3d_ui()
            self.speak("3D Audio enabled")

    def extract_volume(self, text):
        word_nums = {"zero":0, "ten":10, "twenty":20, "thirty":30, "forty":40, "fifty":50, 
                     "sixty":60, "seventy":70, "eighty":80, "ninety":90, "hundred":100, "one fifty":150}
        for word in text.split():
            if word.isdigit(): return int(word)
            if word in word_nums: return word_nums[word]
        return None