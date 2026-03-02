import os
import sys
import numpy as np
from pydub import AudioSegment, effects

base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ffmpeg_exe = os.path.join(base_dir, "ffmpeg.exe")
ffprobe_exe = os.path.join(base_dir, "ffprobe.exe")

if os.path.exists(ffmpeg_exe):
    AudioSegment.converter = ffmpeg_exe
    AudioSegment.ffmpeg = ffmpeg_exe
    print(f"✅ FFmpeg active: {ffmpeg_exe}")
else:
    print(f"❌ Error: ffmpeg.exe missing from {base_dir}")

if os.path.exists(ffprobe_exe):
    AudioSegment.ffprobe = ffprobe_exe
    print(f"✅ FFprobe active: {ffprobe_exe}")
else:
    print(f"⚠️ Warning: ffprobe.exe missing! Reverb might fail.")

def _get_samples(sound: AudioSegment) -> np.ndarray:
    sound = sound.set_channels(1)
    samples = np.array(sound.get_array_of_samples()).astype(np.float32)
    return samples, sound.frame_rate

def _audio_from_samples(samples, original_sound):
    samples = np.clip(samples, -32768, 32767)
    processed_samples = samples.astype(np.int16)

    new_sound = AudioSegment(
        processed_samples.tobytes(),
        frame_rate=original_sound.frame_rate,
        sample_width=original_sound.sample_width,
        channels=original_sound.channels
    )
    return new_sound


def apply_reverb(input_path, output_path, delay_ms=150, decay=0.5):
    try:
        print(f"Applying Reverb to {input_path}...")
        sound = AudioSegment.from_file(input_path)

        sound = effects.normalize(sound)

        channels = sound.split_to_mono()
        processed_channels = []

        for channel in channels:
            samples, rate = _get_samples(channel)
            delay_samples = int((delay_ms / 1000.0 * rate))

            output = np.zeros(len(samples)+ delay_samples)

            output[:len(samples)] += samples

            output[delay_samples:] += samples * decay

            processed_channels.append(_audio_from_samples(output, channel))

        if len(processed_channels) == 2:
            final_sound = AudioSegment.from_mono_audiosegments(processed_channels[0], processed_channels[1])

        else:
            final_sound = processed_channels[0]
        final_sound.export(output_path, format="wav")
        return output_path
    
    except Exception as e:
        print(f"❌ CRITICAL REVERB FAILURE: {e}")
        import traceback
        traceback.print_exc()
        return None

def apply_3d_audio(input_path, output_path, pan_speed=2000):
    try:
        print(f"applying 3D Audio to {input_path}...")
        sound = AudioSegment.from_file(input_path)
        sound = effects.normalize(sound)

        left, right = sound.split_to_mono()

        wide_right = right.invert_phase()

        final_sound = AudioSegment.from_mono_audiosegments(left, wide_right)
        
        final_sound.export(output_path, format="wav")
        print(f"✅ 3D Audio saved to: {output_path}")
        return output_path
    
    except Exception as e:
        print(f"❌ 3D AUDIO FAILURE: {e}")
        return None
   
    

        

