try:
    import vlc  
except Exception as e:
    vlc = None  
    _vlc_import_error = e

import time
from src.audio_processing import effects
import os
class AudioEngine:
    def __init__(self):
        if vlc is None:
            
            raise ImportError(
                "Module 'python-vlc' is not available or the VLC runtime (libvlc) is missing.\n"
                "Install the Python wrapper into your environment:\n"
                "    python -m pip install python-vlc\n"
                "On Windows, also install VLC from: https://www.videolan.org/\n"
                f"Original import error: {_vlc_import_error!r}"
            )

        self.vlc_instance = vlc.Instance()
        if self.vlc_instance is None:
            raise RuntimeError("could not create VLC instance. Is VLC installed?")
        self.player = self.vlc_instance.media_player_new()
        self.equalizer = self.setup_equalizer()
        self.current_media = None
        print("AudioEngine initialized using VLC.")
    
    def setup_equalizer(self):
        eq = vlc.libvlc_audio_equalizer_new()

        vlc.libvlc_audio_equalizer_set_preamp(eq, 12.0)

        for i in range(10):
            vlc.libvlc_audio_equalizer_set_amp_at_index(eq, 0.0, i)
        print("Equalizer initialized.")
        return eq
    def load_track(self, file_path: str):
        self.stop()
        self.current_media = self.vlc_instance.media_new(file_path)
        self.player.set_media(self.current_media)

        if self.equalizer:
            result = vlc.libvlc_media_player_set_equalizer(self.player, self.equalizer)
            if result == 0:
                print("✅ Equalizwer attached successfully.")
            else:
                print("❌ Failed to attach Equalizer.")
        
        print(f"Track '{file_path}' loaded.")

    def play(self):
        if self.current_media:
            self.player.play()
    def pause(self):
        self.player.pause()
    def stop(self):
        self.player.stop()
    
    def set_volume(self, volume: int):
        if 0 <= volume <= 100:
            self.player.audio_set_volume(volume)
    
    def set_time(self, milliseconds: int):
         return self.player.set_time(milliseconds)
    
    def get_time(self) -> int:
        t = self.player.get_time()
        return max(0, t)
    
    def get_length(self) ->int:
        if self.current_media:
            if self.current_media.get_duration() == -1:
                self.current_media.parse_with_options(0, 0)
            return self.current_media.get_duration()
        return 0
    def set_rate(self,rate: float):
        self.player.set_rate(rate)
    
    def set_eq_band(self, band_index: int, gain: float):
        if self.equalizer:
            vlc.libvlc_audio_equalizer_set_amp_at_index(self.equalizer, gain, band_index)
            vlc.libvlc_media_player_set_equalizer(self.player, self.equalizer)
    def apply_preset(self, gains: list[float]):
        if len(gains) != 10:
            print("Error: Preset must have exactly 10 values.")
            return
        
        for i, gain in enumerate(gains):
            self.set_eq_band(i, gain)
    def reset_eq(self):
        self.apply_preset([0.0] * 10)
    
    def shutdown(self):
        self.stop()
        self.player.release()
        self.vlc_instance.release()
        print("AudioEngine shut down")
    
    def apply_lofi_preset(self):
        print("Applying Lo-fi preset...")

        lofi_gains = [
            -2.0,
            0.0,
            4.0,
            4.0,
            2.0,
            -5.0,
            -10.0,
            -15.0,
            -15.0,
            -18.0

        ]
        self.apply_preset(lofi_gains)
    
    def apply_bass_boost_preset(self):
        print(f"Applying Bass Boost preset... ")
        bass_gains = [
            12.0,
            8.0,
            3.0,
            0.0,
            -2.0,
            -2.0,
            -2.0,
            -2.0,
            -2.0,
            -2.0
        ]
        self.apply_preset(bass_gains)
    
    
    def apply_reverb_effect(self, input_path):
        print(f"Generating Reverb for: {input_path}")

        temp_dir = os.path.join(os.getcwd(), "temp")
        os.makedirs(temp_dir, exist_ok=True)

        output_path = os.path.join(temp_dir, "temp_reverb.wav")

        result_path = effects.apply_reverb(input_path, output_path)

        if result_path:
            self.load_track(result_path)
            self.play()
            print("Reverb applied successfully.")
        else:
            print("Failed to apply reverb (Is FFmpeg installed?)")

    def apply_3d_effect(self, input_path):
        print(f"Generating 3D Audio for: {input_path}")

        temp_dir = os.path.join(os.getcwd(), "temp")
        os.makedirs(temp_dir, exist_ok=True)
        output_path = os.path.join(temp_dir, "temp_3d.wav")

        result = effects.apply_3d_audio(input_path, output_path)

        if result:
            self.load_track(result)
            self.play()
            print("3D Audio applied.")
        else:
            print("Failed to apply 3D Audio.")